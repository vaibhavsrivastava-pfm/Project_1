function formatNumber(n) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

export default function KpiTiles({ data }) {
  if (!data) return null

  const tiles = [
    { label: 'Active users', value: formatNumber(data.active_users) },
    { label: 'Attempted', value: formatNumber(data.attempted_users) },
    { label: 'Paid', value: formatNumber(data.paid_users) },
    { label: 'Conversion', value: `${data.conversion_pct}%`, accent: 'teal' },
    { label: 'Attempt success', value: `${data.attempt_success_pct}%` },
    { label: 'ARPU', value: `$${data.arpu}` },
    { label: 'Revenue', value: `$${formatNumber(data.revenue_usd)}`, accent: 'amber' },
  ]

  return (
    <div className="kpi-row">
      {tiles.map((tile) => (
        <div className={`kpi-tile ${tile.accent ? `kpi-tile--${tile.accent}` : ''}`} key={tile.label}>
          <div className="kpi-tile__value mono">{tile.value}</div>
          <div className="kpi-tile__label">{tile.label}</div>
        </div>
      ))}
    </div>
  )
}