import FunnelWaveform from './FunnelWaveform.jsx'
import RankedSegments from './RankedSegments.jsx'

const SEGMENT_LABEL_KEYS = {
  'by-tier': 'engagement_tier',
  'by-tenure': 'tenure_bucket',
  'by-market': 'market',
  'by-platform': 'platform',
}

const SECTION_TITLES = {
  summary: 'Overall funnel',
  'by-tier': 'By engagement tier',
  'by-tenure': 'By tenure',
  'by-market': 'By market',
  'by-platform': 'By platform',
}

// Strip markdown bold markers the model sometimes includes in headlines,
// since this is a display surface, not a markdown renderer.
function cleanText(text) {
  return (text || '').replace(/\*\*/g, '')
}

export default function InsightCard({ insight, index }) {
  const { insight_key, headline, body, supporting_data } = insight
  const title = SECTION_TITLES[insight_key] || insight_key

  return (
    <section className="insight-card" aria-labelledby={`insight-${insight_key}`}>
      <div className="insight-card__eyebrow mono">
        {String(index + 1).padStart(2, '0')} — {title}
      </div>
      <h2 className="insight-card__headline" id={`insight-${insight_key}`}>
        {cleanText(headline)}
      </h2>
      <p className="insight-card__body">{cleanText(body)}</p>

      {insight_key === 'summary' ? (
        <FunnelWaveform data={supporting_data} />
      ) : (
        <RankedSegments
          segments={supporting_data}
          labelKey={SEGMENT_LABEL_KEYS[insight_key]}
        />
      )}
    </section>
  )
}
