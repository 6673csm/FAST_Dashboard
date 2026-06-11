export default function MetricCard({ label, value, delta, icon, color }) {
  const accentColor = color || 'var(--accent-blue)'
  return (
    <div className="metric-card" style={{ borderColor: `${accentColor}30` }}>
      <div className="metric-label" style={{ color: accentColor }}>
        {icon && <span style={{ marginRight: '0.35rem' }}>{icon}</span>}
        {label}
      </div>
      <div className="metric-value">{value ?? '—'}</div>
      {delta !== undefined && (
        <div className="metric-delta">{delta}</div>
      )}
    </div>
  )
}
