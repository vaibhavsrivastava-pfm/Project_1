"""
backend/app/routers/funnel.py

Serves the 5 funnel-metrics views defined in the PRD (Section 4/7):
  - /summary       : overall active -> attempted -> paid funnel
  - /by-tier       : grouped by engagement_tier
  - /by-tenure     : grouped by tenure_bucket
  - /by-market     : grouped by market (min volume filter applied)
  - /by-platform   : grouped by platform

Supabase's PostgREST layer doesn't do GROUP BY aggregation through the
simple query builder, so we fetch the (small, ~38k row) table and
aggregate with pandas here. This keeps the SQL-vs-Python logic in one
place instead of needing custom Postgres views/RPCs for a dataset this
size.
"""

from fastapi import APIRouter
import pandas as pd
from app.db import supabase

router = APIRouter(prefix="/api/funnel", tags=["funnel"])

PAGE_SIZE = 1000  # Supabase/PostgREST default page size


def fetch_all_funnel_rows() -> pd.DataFrame:
    """Paginates through funnel_metrics and returns the full table as a DataFrame."""
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
    return pd.DataFrame(all_rows)


def compute_funnel_rates(df: pd.DataFrame) -> dict:
    """Given a slice of rows, sum the raw counts and recompute rates from
    the sums (never average pre-computed percentages -- that's statistically
    wrong when segment sizes differ)."""
    active = int(df["active_users"].sum())
    attempted = int(df["attempted_users"].fillna(0).sum())
    paid = int(df["paid_users"].fillna(0).sum())
    revenue = float(df["revenue_usd"].fillna(0).sum())

    conversion_pct = round(100.0 * paid / active, 2) if active else 0.0
    attempt_rate_pct = round(100.0 * attempted / active, 2) if active else 0.0
    attempt_success_pct = round(100.0 * paid / attempted, 2) if attempted else 0.0

    return {
        "active_users": active,
        "attempted_users": attempted,
        "paid_users": paid,
        "revenue_usd": round(revenue, 2),
        "conversion_pct": conversion_pct,
        "attempt_rate_pct": attempt_rate_pct,
        "attempt_success_pct": attempt_success_pct,
    }


@router.get("/summary")
def get_summary():
    df = fetch_all_funnel_rows()
    return compute_funnel_rates(df)


@router.get("/by-tier")
def get_by_tier():
    df = fetch_all_funnel_rows()
    results = []
    for tier, group in df.groupby("engagement_tier"):
        row = compute_funnel_rates(group)
        row["engagement_tier"] = tier
        results.append(row)
    results.sort(key=lambda r: r["conversion_pct"], reverse=True)
    return results


@router.get("/by-tenure")
def get_by_tenure():
    df = fetch_all_funnel_rows()
    results = []
    for bucket, group in df.groupby("tenure_bucket"):
        row = compute_funnel_rates(group)
        row["tenure_bucket"] = bucket
        results.append(row)
    # tenure_bucket values are prefixed "A.", "B.", etc. -- sorts correctly as text
    results.sort(key=lambda r: r["tenure_bucket"])
    return results


@router.get("/by-market")
def get_by_market(min_active_users: int = 5000):
    df = fetch_all_funnel_rows()
    results = []
    for market, group in df.groupby("market"):
        row = compute_funnel_rates(group)
        if row["active_users"] < min_active_users:
            continue  # skip low-volume markets, same logic as the original SQL's HAVING clause
        row["market"] = market
        results.append(row)
    results.sort(key=lambda r: r["active_users"], reverse=True)
    return results


@router.get("/by-platform")
def get_by_platform():
    df = fetch_all_funnel_rows()
    df["platform"] = df["platform"].fillna("unknown")
    results = []
    for platform, group in df.groupby("platform"):
        row = compute_funnel_rates(group)
        row["platform"] = platform
        results.append(row)
    results.sort(key=lambda r: r["active_users"], reverse=True)
    return results