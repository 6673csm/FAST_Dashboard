import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import client from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import MetricCard from '../components/MetricCard'

const PLOTLY_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#F0F4FF', family: 'Inter' },
  xaxis: { gridcolor: 'rgba(255,255,255,0.05)', linecolor: 'rgba(255,255,255,0.1)' },
  yaxis: { gridcolor: 'rgba(255,255,255,0.05)', linecolor: 'rgba(255,255,255,0.1)' },
  legend: { bgcolor: 'rgba(20,20,32,0.8)', bordercolor: 'rgba(64,196,255,0.2)', borderwidth: 1 },
  margin: { l: 50, r: 20, t: 50, b: 50 },
}

export default function AutoMLArena() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [target, setTarget] = useState('gh-death')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/data/list').then(r => { setDatasets(r.data); if (r.data.length) setSelectedDataset(r.data[0].id) }).catch(() => {})
  }, [])

  const trainModels = async () => {
    if (!selectedDataset) { setError('Please select a dataset first'); return }
    setLoading(true); setError(''); setResults(null)
    try {
      const r = await client.post('/models/train', { dataset_id: Number(selectedDataset), target })
      setResults(r.data)
    } catch (err) { setError(err.response?.data?.detail || 'Training failed') }
    finally { setLoading(false) }
  }

  const successModels = results?.results?.filter(r => r.status === 'success') || []
  const bestModel = successModels.reduce((best, m) => (!best || (m.metrics?.r2 || 0) > (best.metrics?.r2 || 0)) ? m : best, null)

  return (
    <div>
      <div className="page-header">
        <h1>🤖 <span className="gradient-text">AutoML Arena</span></h1>
        <p>Train & compare 5 ML models: Random Forest, XGBoost, SVR, Bayesian Ridge, ARIMA</p>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {/* Config */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.25rem' }}>⚙️ Training Configuration</h3>
        <div className="grid-2">
          <div className="form-group">
            <label className="form-label">Dataset</label>
            <select id="automl-dataset" className="select" value={selectedDataset} onChange={e => setSelectedDataset(e.target.value)}>
              {datasets.length === 0 && <option value="">No datasets — upload one first</option>}
              {datasets.map(d => <option key={d.id} value={d.id}>#{d.id} — {d.filename} ({d.metadata?.cleaned_rows?.toLocaleString()} rows)</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Target Variable</label>
            <select id="automl-target" className="select" value={target} onChange={e => setTarget(e.target.value)}>
              <option value="gh-death">gh-death (Self-harm Deaths)</option>
              <option value="gh-injure">gh-injure (Self-harm Injuries)</option>
            </select>
          </div>
        </div>
        <button id="automl-train-btn" className="btn btn-primary" onClick={trainModels} disabled={loading || !selectedDataset}>
          {loading ? <><div className="spinner spinner-sm" /> Training Models...</> : '🚀 Train All Models'}
        </button>
      </div>

      {loading && <LoadingSpinner text="Training 5 models... This may take 1-2 minutes." />}

      {/* Results */}
      {results && (
        <>
          {bestModel && (
            <div className="alert alert-success" style={{ marginBottom: '1.5rem' }}>
              🏆 Best model: <strong>{bestModel.model_name}</strong> — R² = {bestModel.metrics?.r2?.toFixed(4)}, MAE = {bestModel.metrics?.mae?.toFixed(4)}
            </div>
          )}

          <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
            <MetricCard icon="✅" label="Models Trained"  value={successModels.length} color="var(--accent-green)" />
            <MetricCard icon="🏆" label="Best R²"         value={bestModel?.metrics?.r2?.toFixed(4)} color="var(--accent-blue)" />
            <MetricCard icon="📉" label="Best MAE"        value={bestModel?.metrics?.mae?.toFixed(4)} color="var(--accent-amber)" />
            <MetricCard icon="🎯" label="Target"          value={target} color="var(--accent-purple)" />
          </div>

          {/* Results Table */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>📊 Model Leaderboard</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr><th>Model</th><th>Status</th><th>MAE</th><th>RMSE</th><th>R²</th><th>MAPE (%)</th><th>Time (s)</th></tr>
                </thead>
                <tbody>
                  {results.results.map(r => (
                    <tr key={r.model_name}>
                      <td style={{ fontWeight: 700, color: r.model_name === bestModel?.model_name ? 'var(--accent-blue)' : 'var(--text-primary)' }}>
                        {r.model_name === bestModel?.model_name ? '🏆 ' : ''}{r.model_name}
                      </td>
                      <td><span className={`badge ${r.status === 'success' ? 'badge-success' : 'badge-error'}`}>{r.status === 'success' ? '✓' : '✗'}</span></td>
                      <td>{r.metrics?.mae?.toFixed(4) ?? '—'}</td>
                      <td>{r.metrics?.rmse?.toFixed(4) ?? '—'}</td>
                      <td>{r.metrics?.r2?.toFixed(4) ?? '—'}</td>
                      <td>{r.metrics?.mape?.toFixed(2) ?? '—'}</td>
                      <td>{r.training_time?.toFixed(2)}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* R² Bar Chart */}
          {successModels.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>📈 R² Score Comparison</h3>
              <Plot
                data={[{
                  type: 'bar',
                  x: successModels.map(m => m.model_name),
                  y: successModels.map(m => m.metrics?.r2 ?? 0),
                  marker: { color: ['#40C4FF','#7C4DFF','#00E676','#FFD740','#FF5252'] },
                  text: successModels.map(m => m.metrics?.r2?.toFixed(4)),
                  textposition: 'outside',
                }]}
                layout={{ ...PLOTLY_LAYOUT, title: { text: 'R² Score by Model', font: { color: '#fff' } } }}
                style={{ width: '100%' }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}
