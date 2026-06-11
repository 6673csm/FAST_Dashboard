export default function LoadingSpinner({ size = 'md', text = '' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', padding: '2rem' }}>
      <div className={`spinner ${size === 'sm' ? 'spinner-sm' : ''}`} />
      {text && <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{text}</p>}
    </div>
  )
}
