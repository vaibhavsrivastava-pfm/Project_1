import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell,
} from 'recharts'

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null
  const d = payload[0].payload
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date mono">{d.label}</div>
      <div className="chart-tooltip__row">Conversion: <strong className="mono">{d.conversion_pct}%</strong></div>
      <div className="chart-tooltip__row">Active users: <strong className="mono">{d.active_users.toLocaleString()}</strong></div>
      <div className="chart-tooltip__row">Revenue: <strong className="mono">${d.revenue_usd.toLocaleString()}</strong></div>
      <div className="chart-tooltip__row">ARPU: <strong className="mono">${d.arpu}</strong></div>
    </div>
  )
}

export default function SegmentBarChart({ title, segments, labelKey, activeFilter, onSelect }) {
  if (!segments || segments.length === 0) return null

  const data = segments.map((s) => ({ ...s, label: s[labelKey] }))

  return (
    <div className="panel">
      <div className="panel__title">
        {title}
        {activeFilter && activeFilter !== 'all' && (
          <button className="panel__clear-filter" onClick={() => onSelect('all')}>
            Filtering: {activeFilter} ✕
          </button>
        )}
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 0 }}>
          <CartesianGrid stroke="var(--ink-line)" horizontal={false} />
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="label"
            stroke="var(--paper-dim)"
            tick={{ fontSize: 12, fontFamily: 'Inter' }}
            tickLine={false}
            axisLine={false}
            width={100}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar
            dataKey="conversion_pct"
            radius={[0, 4, 4, 0]}
            onClick={(entry) => onSelect(entry.label)}
            style={{ cursor: 'pointer' }}
          >
            {data.map((entry) => (
              <Cell
                key={entry.label}
                fill={activeFilter === entry.label ? 'var(--amber)' : 'var(--teal)'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}