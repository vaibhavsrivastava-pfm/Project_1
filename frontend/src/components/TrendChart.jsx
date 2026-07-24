import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
} from 'recharts'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__date mono">{label}</div>
      {payload.map((p) => (
        <div className="chart-tooltip__row" key={p.dataKey}>
          <span style={{ color: p.color }}>●</span> {p.name}: <strong className="mono">{p.value}</strong>
        </div>
      ))}
    </div>
  )
}

export default function TrendChart({ data }) {
  if (!data || data.length === 0) return null

  return (
    <div className="panel">
      <div className="panel__title">Conversion rate over time</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
          <CartesianGrid stroke="var(--ink-line)" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="var(--paper-dim)"
            tick={{ fontSize: 11, fontFamily: 'IBM Plex Mono' }}
            tickLine={false}
            axisLine={{ stroke: 'var(--ink-line)' }}
            minTickGap={40}
          />
          <YAxis
            stroke="var(--paper-dim)"
            tick={{ fontSize: 11, fontFamily: 'IBM Plex Mono' }}
            tickLine={false}
            axisLine={false}
            unit="%"
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="conversion_pct"
            name="Conversion %"
            stroke="var(--teal)"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}