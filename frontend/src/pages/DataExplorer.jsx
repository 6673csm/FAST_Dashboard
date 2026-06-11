import { useState, useRef } from 'react'
import client from '../api/client'
import MetricCard from '../components/MetricCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function DataExplorer() {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  const [datasets, setDatasets] = useState([])
  const [loadingList, setLoadingList] = useState(false)
  const fileRef = useRef(null)

  const fetchDatasets = async () => {
    setLoadingList(true)
    try { const r = await client.get('/data/list'); setDatasets(r.data) }
    catch { setDatasets([]) }
    finally { setLoadingList(false) }
  }

  useState(() => { fetchDatasets() }, [])

  const upload = async (file) => {
    if (!file || !file.name.endsWith('.csv')) { setError('Please upload a CSV file'); return }
    setLoading(true); setError(''); setSummary(null)
    const fd = new FormData(); fd.append('file', file)
    try {
      const r = await client.post('/data/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setSummary(r.data); fetchDatasets()
    } catch (err) { setError(err.response?.data?.detail || 'Upload failed') }
    finally { setLoading(false) }
  }

  const handleDrop = (e) => { e.preventDefault(); setDragging(false); upload(e.dataTransfer.files[0]) }

  return (
    <div>
      <div className="page-header">
        <h1>📊 <span className="gradient-text">Data Explorer</span></h1>
        <p>Upload a CSV file to auto-clean and explore your mental health signal data</p>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {/* Drop Zone */}
      <div
        className={`drop-zone ${dragging ? 'active' : ''}`}
        style={{ marginBottom: '2rem' }}
        onClick={() => fileRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <span className="drop-zone-icon">📁</span>
        <h3 style={{ marginBottom: '0.5rem' }}>Drop your CSV here or click to browse</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Required columns: date, me-fea, me-ang, me-sad, gh-death, gh-injure</p>
        <input ref={fileRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={e => upload(e.target.files[0])} />
      </div>

      {loading && <LoadingSpinner text="Processing and cleaning your data..." />}

      {/* Upload Result */}
      {summary && (
        <>
          <div className="alert alert-success">✅ File uploaded and cleaned successfully: <strong>{summary.filename}</strong></div>
          <div className="grid-4" style={{ marginBottom: '2rem' }}>
            <MetricCard icon="📋" label="Cleaned Rows"     value={summary.cleaned_rows?.toLocaleString()} />
            <MetricCard icon="📐" label="Columns"           value={summary.cleaned_cols} />
            <MetricCard icon="✨" label="Quality Score"     value={`${summary.data_quality_score?.toFixed(1)}%`} color="var(--accent-green)" />
            <MetricCard icon="🚫" label="Missing Fixed"     value={summary.missing_values_before - summary.missing_values_after} color="var(--accent-amber)" />
          </div>

          {summary.missing_required_cols?.length > 0 && (
            <div className="alert alert-warning">⚠️ Missing recommended columns: <strong>{summary.missing_required_cols.join(', ')}</strong></div>
          )}

          {/* Data Preview */}
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>📋 Data Preview (first 10 rows)</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>{summary.columns?.map(c => <th key={c}>{c}</th>)}</tr>
                </thead>
                <tbody>
                  {summary.preview?.map((row, i) => (
                    <tr key={i}>{summary.columns?.map(c => <td key={c}>{String(row[c] ?? '—')}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Datasets List */}
      <div className="card" style={{ marginTop: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3>🗄️ Your Datasets ({datasets.length})</h3>
          <button className="btn btn-secondary" onClick={fetchDatasets} style={{ fontSize: '0.8rem' }}>🔄 Refresh</button>
        </div>
        {loadingList ? <LoadingSpinner size="sm" /> : datasets.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No datasets yet. Upload a CSV above.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead><tr><th>ID</th><th>Filename</th><th>Rows</th><th>Quality</th><th>Uploaded</th></tr></thead>
              <tbody>
                {datasets.map(d => (
                  <tr key={d.id}>
                    <td><span className="badge badge-info">#{d.id}</span></td>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{d.filename}</td>
                    <td>{d.metadata?.cleaned_rows?.toLocaleString()}</td>
                    <td><span className={`badge ${d.metadata?.data_quality_score >= 80 ? 'badge-success' : 'badge-error'}`}>{d.metadata?.data_quality_score?.toFixed(1)}%</span></td>
                    <td>{new Date(d.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
