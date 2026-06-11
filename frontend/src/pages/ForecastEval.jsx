import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import client from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import MetricCard from '../components/MetricCard'

const LAYOUT_BASE = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#F0F4FF', family: 'Inter' },
  xaxis: { gridcolor: 'rgba(255,255,255,0.05)', linecolor: 'rgba(255,255,255,0.1)' },
  yaxis: { gridcolor: 'rgba(255,255,255,0.05)', linecolor: 'rgba(255,255,255,0.1)' },
  legend: { bgcolor: 'rgba(20,20,32,0.8)', bordercolor: 'rgba(64,196,255,0.2)', borderwidth: 1 },
  margin: { l: 60, r: 20, t: 60, b: 60 },
}

const MODEL_OPTIONS = ['XGBoost', 'Random Forest', 'SVR', 'Bayesian Ridge', 'ARIMA']

export default function ForecastEval() {
  const [datasets, setDatasets] = useState([])
  const [form, setForm] = useState({ dataset_id: '', model_name: 'XGBoost', target: 'gh-death', n_days: 90, extrapolation_method: 'moving_average', population: 1000000 })
  const [loading, setLoading] = useState(false)
  const [forecast, setForecast] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/data/list').then(r => { setDatasets(r.data); if (r.data.length) setForm(f => ({ ...f, dataset_id: r.data[0].id })) }).catch(() => {})
  }, [])

  const runForecast = async () => {
    if (!form.dataset_id) { setError('Select a dataset'); return }
    setLoading(true); setError(''); setForecast(null)
    try {
      const r = await client.post('/forecast/run', { ...form, dataset_id: Number(form.dataset_id), n_days: Number(form.n_days), population: Number(form.population) })
      setForecast(r.data)
    } catch (err) { setError(err.response?.data?.detail || 'Forecast failed — train models first') }
    finally { setLoading(false) }
  }

  return (
    <div>
      <div className="page-header">
        <h1>📈 <span className="gradient-text">Forecast & Evaluation</span></h1>
        <p>Generate future predictions and visualize self-harm trends</p>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      {/* Config Card */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.25rem' }}>⚙️ Forecast Configuration</h3>
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
              {MODEL_OPTIONS.map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Target</label>
            <select className="select" value={form.target} onChange={e => setForm(f => ({ ...f, target: e.target.value }))}>
              <option value="gh-death">gh-death (Deaths)</option>
              <option value="gh-injure">gh-injure (Injuries)</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Forecast Days</label>
            <select className="select" value={form.n_days} onChange={e => setForm(f => ({ ...f, n_days: e.target.value }))}>
              <option value={30}>30 days (1 month)</option>
              <option value={60}>60 days (2 months)</option>
              <option value={90}>90 days (3 months)</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Signal Extrapolation</label>
            <select className="select" value={form.extrapolation_method} onChange={e => setForm(f => ({ ...f, extrapolation_method: e.target.value }))}>
              <option value="moving_average">Moving Average (30-day)</option>
              <option value="last_value">Last Observed Value</option>
              <option value="trend">Linear Trend</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Population</label>
            <input className="input" type="number" value={form.population} onChange={e => setForm(f => ({ ...f, population: e.target.value }))} />
          </div>
        </div>
        <button className="btn btn-primary" onClick={runForecast} disabled={loading || !form.dataset_id}>
          {loading ? <><div className="spinner spinner-sm" /> Running Forecast...</> : '📈 Run Forecast'}
        </button>
      </div>

      {loading && <LoadingSpinner text="Generating forecast..." />}

      {/* Results */}
      {forecast && (
        <>
          <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
            <MetricCard icon="📅" label="Forecast Days"   value={forecast.dates?.length} />
            <MetricCard icon="📊" label="Avg Daily Cases" value={Math.round(forecast.predicted_cases?.reduce((a, b) => a + b, 0) / forecast.predicted_cases?.length)} color="var(--accent-blue)" />
            <MetricCard icon="🔺" label="Peak Cases"      value={Math.max(...(forecast.predicted_cases || [0]))} color="var(--accent-red)" />
            <MetricCard icon="🔻" label="Min Cases"       value={Math.min(...(forecast.predicted_cases || [0]))} color="var(--accent-green)" />
          </div>

          {/* Summary */}
          <div className="alert alert-info" style={{ marginBottom: '1.5rem', whiteSpace: 'pre-line' }}>{forecast.summary}</div>

          {/* Cases Chart */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>🔮 Predicted Daily Cases</h3>
            <Plot
              data={[{
                type: 'scatter', mode: 'lines',
                x: forecast.dates, y: forecast.predicted_cases,
                name: 'Predicted Cases',
                line: { color: '#40C4FF', width: 2 },
                fill: 'tozeroy', fillcolor: 'rgba(64,196,255,0.08)',
              }]}
              layout={{ ...LAYOUT_BASE, title: { text: `${form.target} — ${form.n_days}-Day Forecast`, font: { color: '#fff', size: 14 } }, yaxis: { ...LAYOUT_BASE.yaxis, title: { text: 'Cases', font: { color: '#40C4FF' } } } }}
              style={{ width: '100%' }} config={{ displayModeBar: true, responsive: true }}
            />
          </div>

          {/* Signals Chart */}
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>📡 Extrapolated Mental Health Signals</h3>
            <Plot
              data={[
                { type: 'scatter', mode: 'lines', x: forecast.dates, y: forecast.me_fea,  name: 'Fear',    line: { color: '#FF5252', width: 1.5 } },
                { type: 'scatter', mode: 'lines', x: forecast.dates, y: forecast.me_ang,  name: 'Anger',   line: { color: '#FFD740', width: 1.5 } },
                { type: 'scatter', mode: 'lines', x: forecast.dates, y: forecast.me_sad,  name: 'Sadness', line: { color: '#7C4DFF', width: 1.5 } },
              ]}
              layout={{ ...LAYOUT_BASE, title: { text: 'Signal Extrapolation', font: { color: '#fff', size: 14 } } }}
              style={{ width: '100%' }} config={{ displayModeBar: false, responsive: true }}
            />
          </div>
        </>
      )}
    </div>
  )
}
