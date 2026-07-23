"""
backend/app/main.py

FastAPI entrypoint. Mounts the funnel and insights routers.
Run with: uvicorn app.main:app --reload   (from the backend/ directory)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import funnel, insights

app = FastAPI(title="PocketFM Funnel Insights API")

# Allow the local frontend dev server to call this API.
# Tighten this list once the frontend's real dev/prod origin is known.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(funnel.router)
app.include_router(insights.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}