"""
backend/app/routers/insights.py

Ties the funnel aggregates to Argus's insight-generation model.
One endpoint, parameterized by which of the 5 views to generate an
insight for -- matches the PRD's "N=5 insights" structure directly.
"""

from fastapi import APIRouter, HTTPException
from app.routers.funnel import (
    get_summary, get_by_tier, get_by_tenure, get_by_market, get_by_platform,
)
from app.argus_client import generate_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])

# Maps each of the 5 PRD insights to its data-fetching function
INSIGHT_SOURCES = {
    "summary": get_summary,
    "by-tier": get_by_tier,
    "by-tenure": get_by_tenure,
    "by-market": get_by_market,
    "by-platform": get_by_platform,
}


@router.get("/{insight_key}")
def get_insight(insight_key: str):
    if insight_key not in INSIGHT_SOURCES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown insight '{insight_key}'. Valid options: {list(INSIGHT_SOURCES.keys())}",
        )

    stats = INSIGHT_SOURCES[insight_key]()
    insight = generate_insights(stats)

    return {
        "insight_key": insight_key,
        "headline": insight["headline"],
        "body": insight["body"],
        "supporting_data": stats,
    }


@router.get("/")
def get_all_insights():
    """Returns all 5 insights in one call -- convenient for the static
    frontend's single page load."""
    results = []
    for key in INSIGHT_SOURCES:
        stats = INSIGHT_SOURCES[key]()
        insight = generate_insights(stats)
        results.append({
            "insight_key": key,
            "headline": insight["headline"],
            "body": insight["body"],
            "supporting_data": stats,
        })
    return results