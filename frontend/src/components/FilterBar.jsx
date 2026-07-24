export default function FilterBar({ options, filters, onChange, onReset }) {
  if (!options) return null

  function update(key, value) {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="filter-bar">
      <div className="filter-bar__group">
        <label className="filter-bar__label">From</label>
        <input
          type="date"
          className="filter-bar__input"
          min={options.date_min}
          max={options.date_max}
          value={filters.start_date || options.date_min}
          onChange={(e) => update('start_date', e.target.value)}
        />
      </div>

      <div className="filter-bar__group">
        <label className="filter-bar__label">To</label>
        <input
          type="date"
          className="filter-bar__input"
          min={options.date_min}
          max={options.date_max}
          value={filters.end_date || options.date_max}
          onChange={(e) => update('end_date', e.target.value)}
        />
      </div>

      <Dropdown label="Market" value={filters.market} onChange={(v) => update('market', v)} items={options.markets} />
      <Dropdown label="Platform" value={filters.platform} onChange={(v) => update('platform', v)} items={options.platforms} />
      <Dropdown label="Tier" value={filters.engagement_tier} onChange={(v) => update('engagement_tier', v)} items={options.engagement_tiers} />
      <Dropdown label="Tenure" value={filters.tenure_bucket} onChange={(v) => update('tenure_bucket', v)} items={options.tenure_buckets} />

      <button className="filter-bar__reset" onClick={onReset}>Reset</button>
    </div>
  )
}

function Dropdown({ label, value, onChange, items }) {
  return (
    <div className="filter-bar__group">
      <label className="filter-bar__label">{label}</label>
      <select
        className="filter-bar__input"
        value={value || 'all'}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="all">All</option>
        {items.map((item) => (
          <option key={item} value={item}>{item}</option>
        ))}
      </select>
    </div>
  )
}