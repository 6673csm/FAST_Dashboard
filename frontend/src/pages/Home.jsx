import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import MetricCard from '../components/MetricCard'
import client from '../api/client'

export default function Home() {
  const { user } = useAuth()
  const [datasets, setDatasets] = useState([])
  const [health, setHealth] = useState(null)

  useEffect(() => {
    client.get('/health').then(r => setHealth(r.data)).catch(() => {})
    client.get('/data/list').then(r => setDatasets(r.data)).catch(() => {})
  }, [])

  const features = [
    { icon: '📊', title: 'Data Explorer',   desc: 'Upload & auto-clean CSV data with EDA',      to: '/data' },
    { icon: '🤖', title: 'AutoML Arena',     desc: 'Train & compare 5 ML models automatically',  to: '/automl' },
    { icon: '📈', title: 'Forecast & Eval',  desc: 'Visualize predictions with Plotly charts',   to: '/forecast' },
    { icon: '🎯', title: 'Policy Simulator', desc: 'Test "What-If" intervention scenarios',      to: '/simulator' },
    { icon: '🔍', title: 'Explainable AI',   desc: 'Understand which signals drive predictions', to: '/explainable' },
    { icon: '🗺️',  title: 'Geo Intelligence', desc: 'Geographic breakdown and mapping',           to: '/geo' },
    { icon: '📄', title: 'Report Generator', desc: 'Export findings as downloadable reports',    to: '/report' },
  ]

  const totalModels = datasets.reduce((acc, d) => acc + (d.metadata?.models_trained || 0), 0)

  return (
    <div>
      {/* Hero */}
      <div className="page-header">
        <h1>
          🧠 <span className="gradient-text">FAST Dashboard</span>
        </h1>
        <p style={{ fontSize: '1rem', marginTop: '0.5rem', color: 'var(--text-secondary)' }}>
          Forecasting Aggregate-level Self-harm Trends · Public Health AI · Welcome, <strong style={{ color: 'var(--accent-blue)' }}>{user?.username}</strong>
        </p>
      </div>

      {/* Status Metrics */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <MetricCard icon="🗄️" label="Datasets Loaded"   value={datasets.length}   color="var(--accent-blue)"   />
        <MetricCard icon="✅" label="API Status"         value={health ? 'Online' : 'Offline'}  color={health ? 'var(--accent-green)' : 'var(--accent-red)'} />
        <MetricCard icon="🔢" label="API Version"        value={health?.version || '—'}          color="var(--accent-purple)" />
        <MetricCard icon="👤" label="Signed In As"        value={user?.username}                  color="var(--accent-amber)"  />
      </div>

      {/* Disclaimer */}
      <div className="alert alert-warning" style={{ marginBottom: '2rem' }}>
        ⚠️ <strong>Research Use Only.</strong> This system predicts <strong>aggregate national trends only</strong> — NOT individual risk assessment. Do not use for clinical decisions.
      </div>

      {/* Features Grid */}
      <h2 style={{ marginBottom: '1.25rem' }}>⚡ Modules</h2>
      <div className="grid-3" style={{ marginBottom: '2rem' }}>
        {features.map(({ icon, title, desc, to }) => (
          <Link key={to} to={to} style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', height: '100%' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{icon}</div>
              <h3 style={{ marginBottom: '0.4rem', fontSize: '1rem', color: 'var(--text-primary)' }}>{title}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>{desc}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Getting Started */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>🚀 Getting Started</h3>
        <ol style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', paddingLeft: '1.25rem', lineHeight: 2.2 }}>
          <li>Go to <Link to="/data" style={{ color: 'var(--accent-blue)' }}>Data Explorer</Link> and upload your CSV file</li>
          <li>Head to <Link to="/automl" style={{ color: 'var(--accent-blue)' }}>AutoML Arena</Link> to train all 5 models</li>
          <li>View predictions in <Link to="/forecast" style={{ color: 'var(--accent-blue)' }}>Forecast &amp; Eval</Link></li>
          <li>Test interventions with <Link to="/simulator" style={{ color: 'var(--accent-blue)' }}>Policy Simulator</Link></li>
          <li>Export your findings from <Link to="/report" style={{ color: 'var(--accent-blue)' }}>Report Generator</Link></li>
        </ol>
      </div>
    </div>
  )
}
