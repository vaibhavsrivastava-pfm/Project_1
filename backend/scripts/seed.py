"""
backend/scripts/seed.py

Loads the Free-to-Paid Conversion Funnel CSV (pulled from Argus) into Supabase.
Run AFTER creating the table via schema.sql in the Supabase SQL Editor.

Usage:
    python backend/scripts/seed.py
    (uses the default path below unless you pass a different one as an argument)

    python backend/scripts/seed.py /some/other/path.csv

Requires:
    pip install pandas supabase python-dotenv
"""

import os
import sys
import math
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]  # service role key, for writes

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BATCH_SIZE = 1000

DEFAULT_CSV_PATH = "/Users/pocketfm/Downloads/Free-to-paid-funnel.csv"

INT_COLUMNS = [
    "active_users", "attempted_users", "paid_users",
    "attempted_orders", "successful_orders",
]
FLOAT_COLUMNS = [
    "revenue_usd", "conversion_pct", "attempt_rate_pct", "attempt_success_pct",
]
COLUMNS = ["date", "market", "platform", "engagement_tier", "tenure_bucket"] + INT_COLUMNS + FLOAT_COLUMNS


def clean_value(v):
    """Final safety net: catch any NaN/NaT/pd.NA that survives, in any form."""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def load_and_clean(csv_path: str) -> list[dict]:
    df = pd.read_csv(csv_path)

    # Normalize blank platform to None rather than empty string
    if "platform" in df.columns:
        df["platform"] = df["platform"].replace("", None)

    # CRITICAL FIX: use pandas' nullable "Int64" (capital I) dtype for
    # integer columns that contain blanks. Plain int64 can't hold missing
    # values, so pandas silently upgrades those columns to float64 instead
    # (e.g. 14 -> 14.0), and Postgres then rejects "14.0" for an int column.
    # Int64 supports pd.NA directly, keeping whole numbers whole.
    for col in INT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in FLOAT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[COLUMNS]

    # Cast to object dtype BEFORE replacing nulls with None, so numpy/pandas
    # doesn't silently coerce our None back into NaN for numeric columns.
    df = df.astype(object)
    df = df.where(pd.notnull(df), None)

    records = df.to_dict(orient="records")

    # Second safety net: sanitize every value in every record.
    clean_records = [{k: clean_value(v) for k, v in r.items()} for r in records]
    return clean_records


def batched_insert(records: list[dict]):
    total = len(records)
    n_batches = math.ceil(total / BATCH_SIZE)
    for i in range(n_batches):
        chunk = records[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        supabase.table("funnel_metrics").insert(chunk).execute()
        print(f"  inserted batch {i + 1}/{n_batches} ({len(chunk)} rows)")


def main(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"ERROR: file not found at {csv_path}")
        sys.exit(1)
    records = load_and_clean(csv_path)
    print(f"Seeding funnel_metrics: {len(records)} rows from {csv_path}")
    batched_insert(records)
    print("Done.")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_PATH
    main(csv_path)