const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Fetches all 5 insights in one call, matching the backend's
 * GET /api/insights/ endpoint (see backend/app/routers/insights.py).
 */
export async function fetchAllInsights() {
  const response = await fetch(`${API_BASE_URL}/api/insights/`)
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return response.json()
}
