/**
 * Horizontal ranked bars for the 4 segment-comparison insights
 * (by-tier, by-tenure, by-market, by-platform). Sorted by conversion_pct,
 * bar width scaled to the top segment.
 */
export default function RankedSegments({ segments, labelKey }) {
  if (!segments || segments.length === 0) return null

  const sorted = [...segments].sort((a, b) => b.conversion_pct - a.conversion_pct)
  const maxRate = sorted[0].conversion_pct || 1

  return (
    <div className="ranked-segments">
      {sorted.slice(0, 8).map((seg) => {
        const widthPct = Math.max(4, Math.round((seg.conversion_pct / maxRate) * 100))
        return (
          <div className="ranked-segments__row" key={seg[labelKey]}>
            <div className="ranked-segments__label">{seg[labelKey]}</div>
            <div className="ranked-segments__track">
              <div
                className="ranked-segments__fill"
                style={{ width: `${widthPct}%` }}
              />
            </div>
            <div className="ranked-segments__value mono">{seg.conversion_pct}%</div>
          </div>
        )
      })}
    </div>
  )
}
