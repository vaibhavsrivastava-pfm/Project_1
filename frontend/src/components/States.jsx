export function LoadingState() {
  return (
    <div className="state-block" role="status" aria-live="polite">
      <div className="state-block__pulse" aria-hidden="true" />
      <p>Loading insights…</p>
    </div>
  )
}

export function EmptyState() {
  return (
    <div className="state-block">
      <p className="state-block__title">No insights yet</p>
      <p>The backend returned no data. Confirm funnel_metrics has rows in Supabase.</p>
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state-block state-block--error">
      <p className="state-block__title">Couldn't load insights</p>
      <p>{message || 'The backend request failed. Confirm the API is running.'}</p>
      {onRetry && (
        <button className="state-block__retry" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}
