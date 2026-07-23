/**
 * The report's signature element: active -> attempted -> paid rendered as
 * a shrinking equalizer/waveform, nodding to PocketFM's audio identity
 * while visualizing the drop-off at each funnel stage.
 */
export default function FunnelWaveform({ data }) {
  const stages = [
    { label: 'Active', value: data.active_users, color: 'var(--paper-dim)' },
    { label: 'Attempted', value: data.attempted_users, color: 'var(--amber)' },
    { label: 'Paid', value: data.paid_users, color: 'var(--teal)' },
  ]

  const max = stages[0].value

  return (
    <div className="funnel-waveform" role="img" aria-label={`Funnel: ${stages.map(s => `${s.label} ${s.value.toLocaleString()}`).join(', ')}`}>
      <div className="funnel-waveform__bars">
        {stages.map((stage, i) => {
          // Bars are grouped into 7 slim strokes per stage, height scaled
          // to the stage's share of the top of the funnel -- an
          // equalizer read, not a plain bar chart.
          const heightPct = Math.max(8, Math.round((stage.value / max) * 100))
          return (
            <div className="funnel-waveform__stage" key={stage.label}>
              <div className="funnel-waveform__strokes">
                {Array.from({ length: 7 }).map((_, j) => (
                  <span
                    key={j}
                    className="funnel-waveform__stroke"
                    style={{
                      height: `${heightPct}%`,
                      background: stage.color,
                      animationDelay: `${(i * 7 + j) * 30}ms`,
                    }}
                  />
                ))}
              </div>
              <div className="funnel-waveform__label">{stage.label}</div>
              <div className="funnel-waveform__value mono">{stage.value.toLocaleString()}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
