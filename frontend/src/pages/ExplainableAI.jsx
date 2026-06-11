import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import client from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

const LAYOUT_BASE = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#F0F4FF', family: 'Inter' },
  xaxis: { gridcolor: 'rgba(255,255,255,0.05)', linecolor: 'rgba(255,255,255,0.1)' },
  yaxis: { gridcolor: 'rgba(255,255,255,0.05)', linecolor: 'rgba(255,255,255,0.1)' },
  legend: { bgcolor: 'rgba(20,20,32,0.8)', bordercolor: 'rgba(64,196,255,0.2)', borderwidth: 1 },
  margin: { l: 60, r: 20, t: 60, b: 60 },
}

export default function ExplainableAI() {
  const [datasets, setDatasets] = useState([])
  const [form, setForm] = useState({ dataset_id: '', model_name: 'XGBoost', target: 'gh-death' })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/data/list').then(r => { setDatasets(r.data); if (r.data.length) setForm(f => ({ ...f, dataset_id: r.data[0].id })) }).catch(() => {})
  }, [])

  const load = async () => {
    if (!form.dataset_id) { setError('Select a dataset'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const r = await client.get(`/models/feature-importance/${form.dataset_id}/${form.model_name}/${form.target}`)
      setResult(r.data)
    } catch (err) { setError(err.response?.data?.detail || 'Could not load feature importance — train the model first') }
    finally { setLoading(false) }
  }

  const top = result?.features?.slice(0, 15) || []

  return (
    <div>
      <div className="page-header">
        <h1>🔍 <span className="gradient-text">Explainable AI</span></h1>
        <p>Understand which features and signals drive model predictions</p>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.25rem' }}>⚙️ Configuration</h3>
        <div className="grid-3">
          <div className="form-group">
            <label className="form-label">Dataset</label>
            <select className="select" value={form.dataset_id} onChange={e => setForm(f => ({ ...f, dataset_id: e.target.value }))}>
              {datasets.map(d => <option key={d.id} value={d.id}>#{d.id} — {d.filename}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Model</label>
            <select className="select" value={form.model_name} onChange={e => setForm(f => ({ ...f, model_name: e.target.value }))}>
              {['XGBoost','Random Forest','Bayesian Ridge'].map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Target</label>
            <select className="select" value={form.target} onChange={e => setForm(f => ({ ...f, target: e.target.value }))}>
              <option value="gh-death">gh-death</option>
              <option value="gh-injure">gh-injure</option>
            </select>
          </div>
        </div>
        <button className="btn btn-primary" onClick={load} disabled={loading}>
          {loading ? <><div className="spinner spinner-sm" /> Loading...</> : '🔍 Explain Model'}
        </button>
      </div>

      {loading && <LoadingSpinner text="Computing feature importance..." />}

      {result && top.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>📊 Top Feature Importances — {result.model_name}</h3>
          <Plot
            data={[{
              type: 'bar', orientation: 'h',
              x: top.map(f => f.importance).reverse(),
              y: top.map(f => f.feature).reverse(),
              marker: {
                color: top.map((_, i) => `hsl(${200 + i * 8}, 80%, ${65 - i * 2}%)`).reverse(),
              },
              text: top.map(f => `${f.importance.toFixed(2)}%`).reverse(),
              textposition: 'outside',
            }]}
            layout={{
              ...LAYOUT_BASE,
              title: { text: 'Feature Importance (% contribution)', font: { color: '#fff', size: 14 } },
              yaxis: { ...LAYOUT_BASE.yaxis, automargin: true },
              xaxis: { ...LAYOUT_BASE.xaxis, title: { text: 'Importance (%)', font: { color: '#40C4FF' } } },
              height: Math.max(300, top.length * 28 + 80),
            }}
            style={{ width: '100%' }} config={{ displayModeBar: false, responsive: true }}
          />

          <div className="table-wrapper" style={{ marginTop: '1.5rem' }}>
            <table>
              <thead><tr><th>#</th><th>Feature</th><th>Importance</th><th>Contribution</th></tr></thead>
              <tbody>
                {top.map((f, i) => (
                  <tr key={f.feature}>
                    <td style={{ color: 'var(--text-muted)' }}>{i + 1}</td>
                    <td style={{ fontFamily: 'monospace', color: 'var(--accent-blue)' }}>{f.feature}</td>
                    <td><strong>{f.importance.toFixed(2)}%</strong></td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ flex: 1, height: '6px', borderRadius: '999px', background: 'rgba(255,255,255,0.05)' }}>
                          <div style={{ width: `${f.importance}%`, height: '100%', borderRadius: '999px', background: 'var(--gradient-main)' }} />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
