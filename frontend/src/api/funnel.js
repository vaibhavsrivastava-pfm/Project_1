const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function buildQuery(filters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value && value !== 'all') params.set(key, value)
  })
  const qs = params.toString()
  return qs ? `?${qs}` : ''
}

async function get(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return response.json()
}

export const fetchFilterOptions = () => get('/api/funnel/filters')
export const fetchSummary = (filters) => get(`/api/funnel/summary${buildQuery(filters)}`)
export const fetchTrend = (filters) => get(`/api/funnel/trend${buildQuery(filters)}`)
export const fetchByTier = (filters) => get(`/api/funnel/by-tier${buildQuery(filters)}`)
export const fetchByTenure = (filters) => get(`/api/funnel/by-tenure${buildQuery(filters)}`)
export const fetchByMarket = (filters) => get(`/api/funnel/by-market${buildQuery(filters)}`)
export const fetchByPlatform = (filters) => get(`/api/funnel/by-platform${buildQuery(filters)}`)