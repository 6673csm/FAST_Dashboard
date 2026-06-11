import { useState, useEffect } from 'react'
import client from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function ReportGenerator() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/data/list').then(r => { setDatasets(r.data); if (r.data.length) setSelectedDataset(r.data[0].id) }).catch(() => {})
  }, [])

  const generate = async () => {
    if (!selectedDataset) { setError('Select a dataset'); return }
    setLoading(true); setError(''); setReport('')
    try {
      const r = await client.get(`/reports/generate/${selectedDataset}`)
      setReport(r.data)
    } catch (err) { setError(err.response?.data?.detail || 'Report generation failed') }
    finally { setLoading(false) }
  }

  const download = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `FAST_Report_Dataset_${selectedDataset}.md`; a.click()
    URL.revokeObjectURL(url)
  }

  // Simple markdown renderer
  const renderMarkdown = (md) => {
    return md
      .replace(/^### (.+)$/gm, '<h3 style="color:#40C4FF;margin:1rem 0 0.5rem">$1</h3>')
      .replace(/^## (.+)$/gm,  '<h2 style="color:#fff;margin:1.5rem 0 0.75rem;border-bottom:1px solid rgba(64,196,255,0.2);padding-bottom:0.5rem">$1</h2>')
      .replace(/^# (.+)$/gm,   '<h1 style="color:#fff;margin:0 0 1.5rem">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong style="color:#F0F4FF">$1</strong>')
      .replace(/\*(.+?)\*/g,    '<em style="color:var(--text-secondary)">$1</em>')
      .replace(/`(.+?)`/g,      '<code style="background:rgba(64,196,255,0.1);padding:2px 6px;border-radius:4px;font-size:0.85em;color:#40C4FF">$1</code>')
      .replace(/^---$/gm,       '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:1.5rem 0">')
      .replace(/^\|(.+)\|$/gm,  (row) => {
        if (row.includes('---')) return ''
        const cells = row.split('|').filter(Boolean)
        const isHeader = false
        return `<tr>${cells.map(c => `<td style="padding:0.6rem 1rem;border-bottom:1px solid rgba(255,255,255,0.05);color:var(--text-secondary)">${c.trim()}</td>`).join('')}</tr>`
      })
      .replace(/^- (.+)$/gm,   '<li style="color:var(--text-secondary);margin:0.25rem 0;margin-left:1rem">$1</li>')
      .replace(/\n\n/g, '<br/><br/>')
  }

  return (
    <div>
      <div className="page-header">
        <h1>📄 <span className="gradient-text">Report Generator</span></h1>
        <p>Generate and download a comprehensive markdown analysis report</p>
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
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
            <button className="btn btn-primary" onClick={generate} disabled={loading || !selectedDataset}>
              {loading ? <><div className="spinner spinner-sm" /> Generating...</> : '📄 Generate Report'}
            </button>
            {report && (
              <button className="btn btn-secondary" onClick={download}>⬇️ Download .md</button>
            )}
          </div>
        </div>
      </div>

      {loading && <LoadingSpinner text="Generating report..." />}

      {report && (
        <div className="card">
          <div style={{ lineHeight: 1.8, fontSize: '0.9rem' }} dangerouslySetInnerHTML={{ __html: renderMarkdown(report) }} />
        </div>
      )}

      {!report && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📄</div>
          <p>Select a dataset and click <strong>Generate Report</strong> to create a comprehensive analysis</p>
        </div>
      )}
    </div>
  )
}
