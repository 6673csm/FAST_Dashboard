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

function SliderInput({ label, value, onChange, min = -50, max = 50, step = 1, color }) {
  return (
    <div className="form-group">
      <label className="form-label" style={{ color }}>{label}: <strong style={{ color: 'var(--text-primary)' }}>{value > 0 ? '+' : ''}{value}%</strong></label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={e => onChange(Number(e.target.value))} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
        <span>{min}% (decrease)</span><span>0%</span><span>+{max}% (increase)</span>
      </div>
    </div>
  )
}

export default function PolicySimulator() {
  const [datasets, setDatasets] = useState([])
  const [form, setForm] = useState({ dataset_id: '', model_name: 'XGBoost', target: 'gh-death', fear_delta: 0, anger_delta: 0, sadness_delta: 0 })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/data/list').then(r => { setDatasets(r.data); if (r.data.length) setForm(f => ({ ...f, dataset_id: r.data[0].id })) }).catch(() => {})
  }, [])

  const runSim = async () => {
    if (!form.dataset_id) { setError('Select a dataset'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const r = await client.post('/simulator/run', { ...form, dataset_id: Number(form.dataset_id) })
      setResult(r.data)
    } catch (err) { setError(err.response?.data?.detail || 'Simulation failed — train models first') }
    finally { setLoading(false) }
  }

  const isIncrease = result?.pct_change > 0

  return (
    <div>
      <div className="page-header">
        <h1>🎯 <span className="gradient-text">Policy Simulator</span></h1>
        <p>Test "What-If" intervention scenarios by adjusting mental health signal levels</p>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="grid-2" style={{ alignItems: 'start', gap: '1.5rem' }}>
        {/* Config Panel */}
        <div className="card">
          <h3 style={{ marginBottom: '1.25rem' }}>⚙️ Scenario Configuration</h3>

          <div className="form-group">
            <label className="form-label">Dataset</label>
            <select className="select" value={form.dataset_id} onChange={e => setForm(f => ({ ...f, dataset_id: e.target.value }))}>
              {datasets.map(d => <option key={d.id} value={d.id}>#{d.id} — {d.filename}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Model</label>
            <select className="select" value={form.model_name} onChange={e => setForm(f => ({ ...f, model_name: e.target.value }))}>
              {['XGBoost','Random Forest','SVR','Bayesian Ridge'].map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Target</label>
            <select className="select" value={form.target} onChange={e => setForm(f => ({ ...f, target: e.target.value }))}>
              <option value="gh-death">gh-death (Deaths)</option>
              <option value="gh-injure">gh-injure (Injuries)</option>
            </select>
          </div>

          <div className="divider" />
          <h4 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Signal Adjustments (% change)
          </h4>

          <SliderInput label="😨 Fear"    value={form.fear_delta}    onChange={v => setForm(f => ({ ...f, fear_delta: v }))}    color="var(--accent-red)"    />
          <SliderInput label="😡 Anger"   value={form.anger_delta}   onChange={v => setForm(f => ({ ...f, anger_delta: v }))}   color="var(--accent-amber)"  />
          <SliderInput label="😢 Sadness" value={form.sadness_delta} onChange={v => setForm(f => ({ ...f, sadness_delta: v }))} color="var(--accent-purple)" />

          <button className="btn btn-primary" onClick={runSim} disabled={loading || !form.dataset_id} style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }}>
            {loading ? <><div className="spinner spinner-sm" /> Simulating...</> : '▶ Run Simulation'}
          </button>
        </div>

        {/* Results Panel */}
        <div>
          {loading && <div className="card"><LoadingSpinner text="Running simulation..." /></div>}
          {result && (
            <>
              <div className={`alert ${isIncrease ? 'alert-error' : 'alert-success'}`} style={{ marginBottom: '1rem' }}>
                {isIncrease ? '📈 ⚠️' : '📉 ✅'} Simulation predicts a <strong>{Math.abs(result.pct_change).toFixed(2)}% {isIncrease ? 'INCREASE' : 'DECREASE'}</strong> in {form.target}
              </div>

              <div className="grid-2" style={{ marginBottom: '1rem' }}>
                <MetricCard icon="📊" label="Baseline Avg"  value={result.baseline_avg?.toFixed(4)} color="var(--accent-blue)"   />
                <MetricCard icon="🔮" label="Simulated Avg" value={result.simulated_avg?.toFixed(4)} color={isIncrease ? 'var(--accent-red)' : 'var(--accent-green)'} />
              </div>

              <div className="card">
                <h3 style={{ marginBottom: '1rem' }}>📊 Baseline vs Simulated</h3>
                <Plot
                  data={[
                    { type: 'scatter', mode: 'lines', x: result.dates, y: result.baseline,  name: 'Baseline',  line: { color: '#40C4FF', width: 2 } },
                    { type: 'scatter', mode: 'lines', x: result.dates, y: result.simulated, name: 'Simulated', line: { color: '#FF5252', width: 2, dash: 'dash' } },
                  ]}
                  layout={{ ...LAYOUT_BASE, title: { text: 'What-If Scenario Impact', font: { color: '#fff', size: 14 } } }}
                  style={{ width: '100%' }} config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            </>
          )}
          {!result && !loading && (
            <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
              <p>Adjust the signal sliders and click <strong>Run Simulation</strong></p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
