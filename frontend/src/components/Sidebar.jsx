import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/',             icon: '🏠', label: 'Home' },
  { to: '/data',         icon: '📊', label: 'Data Explorer' },
  { to: '/automl',       icon: '🤖', label: 'AutoML Arena' },
  { to: '/forecast',     icon: '📈', label: 'Forecast & Eval' },
  { to: '/simulator',    icon: '🎯', label: 'Policy Simulator' },
  { to: '/explainable',  icon: '🔍', label: 'Explainable AI' },
  { to: '/geo',          icon: '🗺️',  label: 'Geo Intelligence' },
  { to: '/report',       icon: '📄', label: 'Report Generator' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside style={{
      width: '240px',
      minWidth: '240px',
      background: 'rgba(10, 10, 20, 0.95)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '1.5rem 0',
      backdropFilter: 'blur(20px)',
      position: 'sticky',
      top: 0,
      height: '100vh',
      overflowY: 'auto',
    }}>
      {/* Logo */}
      <div style={{ padding: '0 1.25rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <span style={{ fontSize: '1.8rem' }}>🧠</span>
          <div>
            <div style={{ fontWeight: 900, fontSize: '1.1rem', background: 'var(--gradient-main)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              FAST
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Dashboard v2
            </div>
          </div>
        </div>
      </div>

      {/* Nav Items */}
      <nav style={{ flex: 1, padding: '1rem 0.75rem' }}>
        {navItems.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              textDecoration: 'none',
              marginBottom: '0.15rem',
              fontSize: '0.875rem',
              fontWeight: isActive ? 700 : 400,
              color: isActive ? 'var(--accent-blue)' : 'var(--text-secondary)',
              background: isActive ? 'rgba(64,196,255,0.1)' : 'transparent',
              border: isActive ? '1px solid rgba(64,196,255,0.2)' : '1px solid transparent',
              transition: 'var(--transition)',
            })}
          >
            <span style={{ fontSize: '1rem', width: '20px', textAlign: 'center' }}>{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
          Signed in as <span style={{ color: 'var(--accent-blue)', fontWeight: 700 }}>{user?.username}</span>
        </div>
        <button className="btn btn-secondary" onClick={handleLogout} style={{ width: '100%', justifyContent: 'center', fontSize: '0.8rem' }}>
          🚪 Sign Out
        </button>
      </div>
    </aside>
  )
}
