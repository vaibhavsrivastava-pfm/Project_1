import { useEffect, useState, useCallback } from 'react'
import {
  fetchFilterOptions, fetchSummary, fetchTrend,
  fetchByTier, fetchByTenure, fetchByMarket, fetchByPlatform,
} from './api/funnel.js'
import FilterBar from './components/FilterBar.jsx'
import KpiTiles from './components/KpiTiles.jsx'
import TrendChart from './components/TrendChart.jsx'
import SegmentBarChart from './components/SegmentBarChart.jsx'
import InsightsPanel from './components/InsightsPanel.jsx'
import { LoadingState, ErrorState } from './components/States.jsx'

export default function App() {
  const [options, setOptions] = useState(null)
  const [filters, setFilters] = useState({})
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [summary, setSummary] = useState(null)
  const [trend, setTrend] = useState([])
  const [byTier, setByTier] = useState([])
  const [byTenure, setByTenure] = useState([])
  const [byMarket, setByMarket] = useState([])
  const [byPlatform, setByPlatform] = useState([])

  useEffect(() => {
    fetchFilterOptions()
      .then(setOptions)
      .catch((err) => {
        setErrorMessage(err.message)
        setStatus('error')
      })
  }, [])

  const load = useCallback((f) => {
    setStatus('loading')
    Promise.all([
      fetchSummary(f),
      fetchTrend(f),
      fetchByTier(f),
      fetchByTenure(f),
      fetchByMarket(f),
      fetchByPlatform(f),
    ])
      .then(([s, t, tier, tenure, market, platform]) => {
        setSummary(s)
        setTrend(t)
        setByTier(tier)
        setByTenure(tenure)
        setByMarket(market)
        setByPlatform(platform)
        setStatus('success')
      })
      .catch((err) => {
        setErrorMessage(err.message)
        setStatus('error')
      })
  }, [])

  useEffect(() => {
    if (options) load(filters)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options, filters])

  function handleReset() {
    setFilters({})
  }

  return (
    <div className="dashboard-shell">
      <header className="dashboard-header">
        <div className="dashboard-header__eyebrow mono">PocketFM — Free-to-Paid Funnel</div>
        <h1 className="dashboard-header__title">Conversion dashboard</h1>
      </header>

      <FilterBar options={options} filters={filters} onChange={setFilters} onReset={handleReset} />

      {status === 'error' && <ErrorState message={errorMessage} onRetry={() => load(filters)} />}

      {status === 'loading' && !summary && <LoadingState />}

      {summary && (
        <>
          <KpiTiles data={summary} />

          <div className="dashboard-grid">
            <div className="dashboard-grid__full">
              <TrendChart data={trend} />
            </div>
            <SegmentBarChart
              title="By engagement tier"
              segments={byTier}
              labelKey="engagement_tier"
              activeFilter={filters.engagement_tier}
              onSelect={(v) => setFilters({ ...filters, engagement_tier: v })}
            />
            <SegmentBarChart
              title="By tenure"
              segments={byTenure}
              labelKey="tenure_bucket"
              activeFilter={filters.tenure_bucket}
              onSelect={(v) => setFilters({ ...filters, tenure_bucket: v })}
            />
            <SegmentBarChart
              title="By market"
              segments={byMarket}
              labelKey="market"
              activeFilter={filters.market}
              onSelect={(v) => setFilters({ ...filters, market: v })}
            />
            <SegmentBarChart
              title="By platform"
              segments={byPlatform}
              labelKey="platform"
              activeFilter={filters.platform}
              onSelect={(v) => setFilters({ ...filters, platform: v })}
            />
          </div>

          <InsightsPanel />
        </>
      )}
    </div>
  )
}