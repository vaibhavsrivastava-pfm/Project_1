"""
backend/app/argus_client.py

ALL calls to Argus live in this file, per CLAUDE.md's isolation rule.
Two functions:
  - run_databricks_query(sql)  -- NOT used in this project's final flow;
    we ingest via a pre-exported CSV instead (see backend/scripts/seed.py).
    Kept here documented in case a live-query path is needed later.
  - generate_insights(stats)   -- the real insight-generation call used
    by the /api/insights endpoint.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ARGUS_API_KEY = os.environ["ARGUS_API_KEY"]
ARGUS_BASE_URL = "https://argus.pocketfm.org/api"

# Confirmed via /api/models + a live test call (see PRD Section 3).
# Built on bedrock-claude-4.5-sonnet; purpose-built for exactly this task.
INSIGHT_MODEL = "argus-results-synthesizer"


def generate_insights(stats: dict) -> dict:
    """
    Sends aggregated funnel stats to Argus's results-synthesizer model
    and returns the generated insight text.

    Input: a dict of aggregated numbers (NOT raw rows) -- e.g. output of
    one of the /api/funnel/* endpoints.

    Returns: {"headline": str, "body": str, "raw": dict} -- raw is the
    full API response, kept for debugging/logging, not for display.
    """
    system_prompt = (
        "You are analyzing PocketFM's free-to-paid conversion funnel data. "
        "Given aggregated statistics (not raw user-level data), produce a "
        "clear, concise insight: one headline sentence, followed by 2-3 "
        "supporting sentences with specific numbers. Be objective -- note "
        "any important caveats (e.g. small sample size) if relevant. "
        "Do not invent numbers not present in the input. "
        "Write only the prose itself -- never include labels like "
        "'Headline:', 'Supporting details:', 'Insight:', or similar meta-text "
        "in your response. Do not use markdown formatting (no **bold**, no "
        "bullet points). Just plain sentences."
    )

    user_content = (
        f"Here is the aggregated data:\n\n{stats}\n\n"
        "Generate one insight following the system instructions."
    )

    payload = {
        "model": INSIGHT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }

    response = requests.post(
        f"{ARGUS_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {ARGUS_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]

    # Simple headline/body split: first sentence as headline, rest as body.
    # Good enough for now; revisit if the model's output format needs more
    # structure (e.g. ask it to return JSON directly instead).
    parts = content.split(". ", 1)
    headline = parts[0].strip().rstrip(".") + "."
    body = parts[1].strip() if len(parts) > 1 else ""

    return {"headline": headline, "body": body, "raw": data}


if __name__ == "__main__":
    # Quick manual test -- run: python backend/app/argus_client.py
    test_stats = {
        "active_users": 500000,
        "attempted_users": 45000,
        "paid_users": 38000,
        "conversion_pct": 7.6,
        "attempt_success_pct": 84.4,
    }
    result = generate_insights(test_stats)
    print("HEADLINE:", result["headline"])
    print("BODY:", result["body"])