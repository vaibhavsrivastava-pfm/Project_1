"""
backend/app/routers/funnel.py

Serves funnel-metrics data with support for filtering (date range,
market, platform, engagement_tier, tenure_bucket) so the dashboard can
drill down interactively, plus a /trend endpoint for time-series charts.

Supabase's PostgREST layer doesn't do GROUP BY aggregation through the
simple query builder, so we fetch the (small, ~38k row) table once and
filter/aggregate with pandas here.
"""

from typing import Optional
from fastapi import APIRouter
import pandas as pd
from app.db import supabase

router = APIRouter(prefix="/api/funnel", tags=["funnel"])

PAGE_SIZE = 1000  # Supabase/PostgREST default page size

_cache = {"df": None}


def fetch_all_funnel_rows() -> pd.DataFrame:
    """Paginates through funnel_metrics and returns the full table as a
    DataFrame. Cached in-process since the dataset doesn't change between
    requests -- avoids re-fetching ~38k rows on every dashboard interaction."""
    if _cache["df"] is not None:
        return _cache["df"].copy()

    all_rows = []
    start = 0
    while True:
        end = start + PAGE_SIZE - 1
        result = supabase.table("funnel_metrics").select("*").range(start, end).execute()
        rows = result.data
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        start += PAGE_SIZE

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"])
    _cache["df"] = df
    return df.copy()


def apply_filters(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: Optional[str] = None,
    platform: Optional[str] = None,
    engagement_tier: Optional[str] = None,
    tenure_bucket: Optional[str] = None,
) -> pd.DataFrame:
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]
    if market and market != "all":
        df = df[df["market"] == market]
    if platform and platform != "all":
        df = df[df["platform"] == platform]
    if engagement_tier and engagement_tier != "all":
        df = df[df["engagement_tier"] == engagement_tier]
    if tenure_bucket and tenure_bucket != "all":
        df = df[df["tenure_bucket"] == tenure_bucket]
    return df


def compute_funnel_rates(df: pd.DataFrame) -> dict:
    """Sums raw counts and recomputes rates from the sums -- never average
    pre-computed percentages, that's statistically wrong across uneven
    segment sizes."""
    active = int(df["active_users"].sum())
    attempted = int(df["attempted_users"].fillna(0).sum())
    paid = int(df["paid_users"].fillna(0).sum())
    revenue = float(df["revenue_usd"].fillna(0).sum())

    conversion_pct = round(100.0 * paid / active, 2) if active else 0.0
    attempt_rate_pct = round(100.0 * attempted / active, 2) if active else 0.0
    attempt_success_pct = round(100.0 * paid / attempted, 2) if attempted else 0.0
    arpu = round(revenue / paid, 2) if paid else 0.0

    return {
        "active_users": active,
        "attempted_users": attempted,
        "paid_users": paid,
        "revenue_usd": round(revenue, 2),
        "conversion_pct": conversion_pct,
        "attempt_rate_pct": attempt_rate_pct,
        "attempt_success_pct": attempt_success_pct,
        "arpu": arpu,
    }


@router.get("/filters")
def get_filter_options():
    """Distinct values for each filterable dimension, plus the overall
    date range -- powers the dashboard's filter bar dropdowns/date picker."""
    df = fetch_all_funnel_rows()
    return {
        "date_min": df["date"].min().strftime("%Y-%m-%d"),
        "date_max": df["date"].max().strftime("%Y-%m-%d"),
        "markets": sorted(df["market"].dropna().unique().tolist()),
        "platforms": sorted(df["platform"].dropna().unique().tolist()),
        "engagement_tiers": sorted(df["engagement_tier"].dropna().unique().tolist()),
        "tenure_buckets": sorted(df["tenure_bucket"].dropna().unique().tolist()),
    }


@router.get("/summary")
def get_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: Optional[str] = None,
    platform: Optional[str] = None,
    engagement_tier: Optional[str] = None,
    tenure_bucket: Optional[str] = None,
):
    df = fetch_all_funnel_rows()
    df = apply_filters(df, start_date, end_date, market, platform, engagement_tier, tenure_bucket)
    return compute_funnel_rates(df)


@router.get("/trend")
def get_trend(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: Optional[str] = None,
    platform: Optional[str] = None,
    engagement_tier: Optional[str] = None,
    tenure_bucket: Optional[str] = None,
):
    """Daily aggregates over the (optionally filtered) date range -- powers
    the trend line chart."""
    df = fetch_all_funnel_rows()
    df = apply_filters(df, start_date, end_date, market, platform, engagement_tier, tenure_bucket)
    results = []
    for date, group in df.groupby(df["date"].dt.strftime("%Y-%m-%d")):
        row = compute_funnel_rates(group)
        row["date"] = date
        results.append(row)
    results.sort(key=lambda r: r["date"])
    return results


@router.get("/by-tier")
def get_by_tier(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: Optional[str] = None,
    platform: Optional[str] = None,
    tenure_bucket: Optional[str] = None,
):
    df = fetch_all_funnel_rows()
    df = apply_filters(df, start_date, end_date, market, platform, None, tenure_bucket)
    results = []
    for tier, group in df.groupby("engagement_tier"):
        row = compute_funnel_rates(group)
        row["engagement_tier"] = tier
        results.append(row)
    results.sort(key=lambda r: r["conversion_pct"], reverse=True)
    return results


@router.get("/by-tenure")
def get_by_tenure(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: Optional[str] = None,
    platform: Optional[str] = None,
    engagement_tier: Optional[str] = None,
):
    df = fetch_all_funnel_rows()
    df = apply_filters(df, start_date, end_date, market, platform, engagement_tier, None)
    results = []
    for bucket, group in df.groupby("tenure_bucket"):
        row = compute_funnel_rates(group)
        row["tenure_bucket"] = bucket
        results.append(row)
    results.sort(key=lambda r: r["tenure_bucket"])
    return results


@router.get("/by-market")
def get_by_market(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    platform: Optional[str] = None,
    engagement_tier: Optional[str] = None,
    tenure_bucket: Optional[str] = None,
    min_active_users: int = 5000,
):
    df = fetch_all_funnel_rows()
    df = apply_filters(df, start_date, end_date, None, platform, engagement_tier, tenure_bucket)
    results = []
    for market, group in df.groupby("market"):
        row = compute_funnel_rates(group)
        if row["active_users"] < min_active_users:
            continue
        row["market"] = market
        results.append(row)
    results.sort(key=lambda r: r["active_users"], reverse=True)
    return results


@router.get("/by-platform")
def get_by_platform(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    market: Optional[str] = None,
    engagement_tier: Optional[str] = None,
    tenure_bucket: Optional[str] = None,
):
    df = fetch_all_funnel_rows()
    df = apply_filters(df, start_date, end_date, market, None, engagement_tier, tenure_bucket)
    df["platform"] = df["platform"].fillna("unknown")
    results = []
    for platform, group in df.groupby("platform"):
        row = compute_funnel_rates(group)
        row["platform"] = platform
        results.append(row)
    results.sort(key=lambda r: r["active_users"], reverse=True)
    return results