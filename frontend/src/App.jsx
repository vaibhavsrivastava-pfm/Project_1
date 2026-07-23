import { useEffect, useState, useCallback } from 'react'
import { fetchAllInsights } from './api/insights.js'
import ProblemHeader from './components/ProblemHeader.jsx'
import InsightCard from './components/InsightCard.jsx'
import { LoadingState, EmptyState, ErrorState } from './components/States.jsx'

const INSIGHT_ORDER = ['summary', 'by-tier', 'by-tenure', 'by-market', 'by-platform']

export default function App() {
  const [status, setStatus] = useState('loading') // loading | success | empty | error
  const [insights, setInsights] = useState([])
  const [errorMessage, setErrorMessage] = useState('')

  const load = useCallback(() => {
    setStatus('loading')
    fetchAllInsights()
      .then((data) => {
        if (!data || data.length === 0) {
          setStatus('empty')
          return
        }
        const ordered = [...data].sort(
          (a, b) => INSIGHT_ORDER.indexOf(a.insight_key) - INSIGHT_ORDER.indexOf(b.insight_key)
        )
        setInsights(ordered)
        setStatus('success')
      })
      .catch((err) => {
        setErrorMessage(err.message)
        setStatus('error')
      })
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <main className="app-shell">
      <ProblemHeader />

      {status === 'loading' && <LoadingState />}
      {status === 'empty' && <EmptyState />}
      {status === 'error' && <ErrorState message={errorMessage} onRetry={load} />}
      {status === 'success' &&
        insights.map((insight, i) => (
          <InsightCard key={insight.insight_key} insight={insight} index={i} />
        ))}
    </main>
  )
}
