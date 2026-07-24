import { useEffect, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function cleanText(text) {
  return (text || '')
    .replace(/\*\*/g, '')
    .replace(/^(headline|insight|summary)\s*:\s*/i, '')
}

export default function InsightsPanel() {
  const [status, setStatus] = useState('loading')
  const [items, setItems] = useState([])
  const [openKey, setOpenKey] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/insights/`)
      .then((res) => {
        if (!res.ok) throw new Error('failed')
        return res.json()
      })
      .then((data) => {
        setItems(data)
        setStatus('success')
      })
      .catch(() => setStatus('error'))
  }, [])

  if (status === 'loading') {
    return <div className="findings-panel findings-panel--loading mono">Generating key findings…</div>
  }
  if (status === 'error') {
    return <div className="findings-panel findings-panel--error">Key findings unavailable right now.</div>
  }

  return (
    <div className="findings-panel">
      <div className="findings-panel__title">Key findings</div>
      {items.map((item) => (
        <div className="finding" key={item.insight_key}>
          {item.error ? (
            <div className="finding__error">Couldn't generate this finding.</div>
          ) : (
            <>
              <button
                className="finding__headline"
                onClick={() => setOpenKey(openKey === item.insight_key ? null : item.insight_key)}
              >
                {cleanText(item.headline)}
              </button>
              {openKey === item.insight_key && (
                <p className="finding__body">{cleanText(item.body)}</p>
              )}
            </>
          )}
        </div>
      ))}
    </div>
  )
}