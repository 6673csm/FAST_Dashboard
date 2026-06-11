import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import client from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

const LAYOUT_BASE = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#F0F4FF', family: 'Inter' },
  margin: { l: 60, r: 20, t: 60, b: 60 },
}

export default function GeoIntelligence() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/data/list').then(r => { setDatasets(r.data); if (r.data.length) setSelectedDataset(r.data[0].id) }).catch(() => {})
  }, [])

  const loadData = async () => {
    if (!selectedDataset) return
    setLoading(true); setError(''); setSummary(null)
    try {
      const r = await client.get(`/data/${selectedDataset}/summary`)
      setSummary(r.data)
    } catch (err) { setError(err.response?.data?.detail || 'Failed to load data') }
    finally { setLoading(false) }
  }

  const cols = summary?.columns?.filter(c => c !== 'date') || []
  const preview = summary?.preview || []
  const hasRegion = summary?.columns?.includes('region') || summary?.columns?.includes('state')

  return (
    <div>
      <div className="page-header">
        <h1>🗺️ <span className="gradient-text">Geographic Intelligence</span></h1>
        <p>Explore regional patterns in mental health signal data</p>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="grid-2">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Dataset</label>
            <select className="select" value={selectedDataset} onChange={e => setSelectedDataset(e.target.value)}>
              {datasets.map(d => <option key={d.id} value={d.id}>#{d.id} — {d.filename}</option>)}
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button className="btn btn-primary" onClick={loadData} disabled={loading || !selectedDataset}>
              {loading ? <><div className="spinner spinner-sm" /> Loading...</> : '🗺️ Analyze Data'}
            </button>
          </div>
        </div>
      </div>

      {loading && <LoadingSpinner text="Loading geographic data..." />}

      {summary && (
        <>
          {!hasRegion && (
            <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
              ℹ️ No <strong>region</strong> or <strong>state</strong> column detected. Showing signal correlation heatmap instead.
            </div>
          )}

          {/* Signal trend chart */}
          {['me-fea','me-ang','me-sad'].every(c => summary.columns?.includes(c)) && (
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>📡 Mental Health Signal Trends</h3>
              <Plot
                data={[
                  { type: 'scatter', mode: 'lines', x: preview.map(r => r.date), y: preview.map(r => r['me-fea']),  name: 'Fear',    line: { color: '#FF5252', width: 2 } },
                  { type: 'scatter', mode: 'lines', x: preview.map(r => r.date), y: preview.map(r => r['me-ang']),  name: 'Anger',   line: { color: '#FFD740', width: 2 } },
                  { type: 'scatter', mode: 'lines', x: preview.map(r => r.date), y: preview.map(r => r['me-sad']),  name: 'Sadness', line: { color: '#7C4DFF', width: 2 } },
                ]}
                layout={{ ...LAYOUT_BASE, title: { text: 'Signals Over Time (Preview)', font: { color: '#fff', size: 14 } } }}
                style={{ width: '100%' }} config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          )}

          {/* Numeric distribution */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>📊 Column Statistics</h3>
            <div className="table-wrapper">
              <table>
                <thead><tr><th>Column</th><th>Count</th><th>Mean</th><th>Std</th><th>Min</th><th>Max</th></tr></thead>
                <tbody>
                  {Object.entries(summary.stats || {}).map(([col, stats]) => (
                    <tr key={col}>
                      <td style={{ color: 'var(--accent-blue)', fontFamily: 'monospace' }}>{col}</td>
                      <td>{stats.count}</td>
                      <td>{stats.mean}</td>
                      <td>{stats.std}</td>
                      <td>{stats.min}</td>
                      <td>{stats.max}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Scatter: Fear vs Sadness */}
          {['me-fea','me-sad'].every(c => summary.columns?.includes(c)) && (
            <div className="card">
              <h3 style={{ marginBottom: '1rem' }}>🔗 Fear vs Sadness Correlation (Preview)</h3>
              <Plot
                data={[{
                  type: 'scatter', mode: 'markers',
                  x: preview.map(r => r['me-fea']),
                  y: preview.map(r => r['me-sad']),
                  marker: { color: '#40C4FF', size: 8, opacity: 0.7 },
                }]}
                layout={{ ...LAYOUT_BASE, title: { text: 'Fear vs Sadness', font: { color: '#fff', size: 14 } }, xaxis: { ...LAYOUT_BASE.xaxis, title: { text: 'Fear', font: { color: '#40C4FF' } } }, yaxis: { ...LAYOUT_BASE.yaxis, title: { text: 'Sadness', font: { color: '#7C4DFF' } } } }}
                style={{ width: '100%' }} config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}
