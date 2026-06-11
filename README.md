<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:40C4FF,100:7C4DFF&height=180&section=header&text=FAST%20Dashboard&fontSize=50&fontColor=ffffff&fontAlignY=38&desc=Forecasting%20Aggregate-level%20Self-harm%20Trends&descAlignY=58&descColor=ccccff" />

<!-- Badges -->
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-189AB4?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00E676?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-7C4DFF?style=for-the-badge)

**A Full-Stack AI Public Health Decision Support System**

[📖 Docs](#-usage-guide) · [🚀 Quick Start](#-quick-start) · [🏗️ Architecture](#️-architecture) · [🤖 ML Models](#-ml-models) · [🌐 API Reference](#-api-reference)

</div>

---

## 🎯 What is FAST?

**FAST** (Forecasting Aggregate-level Self-harm Trends) is a production-grade, full-stack web application that uses **machine learning** to forecast national self-harm trends from social media mental health signals (Fear, Anger, Sadness).

> ⚠️ **Research Use Only** — Predicts aggregate national trends. NOT for individual clinical risk assessment.

### ✨ Key Highlights

| Feature | Description |
|---------|-------------|
| 🤖 **AutoML Engine** | Trains & compares 5 models: XGBoost, Random Forest, SVR, Bayesian Ridge, ARIMA |
| 🔐 **JWT Authentication** | Secure login/register with 24-hour access tokens |
| 📊 **Interactive Charts** | Plotly.js visualizations — forecasts, signals, feature importance |
| 🎯 **Policy Simulator** | What-If analysis by adjusting Fear/Anger/Sadness signals |
| 🔍 **Explainable AI** | Feature importance to understand prediction drivers |
| 📄 **Report Generator** | Export full markdown analysis reports |
| 🌐 **REST API** | Full FastAPI backend with Swagger UI at `/docs` |
| 💾 **Persistent Storage** | SQLite database for users, datasets, and models |

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, React Router v6, Plotly.js, Axios |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, Pydantic v2 |
| **Authentication** | JWT (python-jose), bcrypt (passlib) |
| **Machine Learning** | Scikit-learn, XGBoost, Statsmodels, SHAP |
| **Data** | Pandas, NumPy, GeoPandas |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Deployment** | Render.com, Railway (config included) |

</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone
```bash
git clone https://github.com/6673csm/FAST_Dashboard.git
cd FAST_Dashboard
```

### 2. Start the Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
- API running at: **http://localhost:8000**
- Swagger docs at: **http://localhost:8000/docs**

### 3. Start the Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
- App running at: **http://localhost:5173**

### 4. (Optional) Run Original Streamlit App
```bash
pip install -r requirements.txt
streamlit run app.py
```
- Streamlit app at: **http://localhost:8501**

---

## 🏗️ Architecture

```
FAST_Dashboard/
│
├── backend/                    ← FastAPI REST API
│   ├── main.py                 ← App entry, CORS, routers
│   ├── database.py             ← SQLite + SQLAlchemy ORM
│   ├── auth.py                 ← JWT authentication
│   ├── schemas.py              ← Pydantic request/response models
│   └── routers/
│       ├── auth.py             ← POST /api/auth/register, /login
│       ├── data.py             ← POST /api/data/upload, GET /list
│       ├── models.py           ← POST /api/models/train
│       ├── forecast.py         ← POST /api/forecast/run
│       ├── simulator.py        ← POST /api/simulator/run
│       └── reports.py          ← GET /api/reports/generate/{id}
│
├── frontend/                   ← React + Vite SPA
│   └── src/
│       ├── pages/              ← 10 page components
│       ├── components/         ← Sidebar, MetricCard, Spinner
│       ├── context/            ← AuthContext (JWT state)
│       └── api/client.js       ← Axios with JWT interceptor
│
├── modules/                    ← Original Streamlit ML modules
├── pages/                      ← Original Streamlit pages
├── app.py                      ← Original Streamlit entry
├── render.yaml                 ← Render.com deployment config
├── Procfile                    ← Railway/Heroku deployment
└── .gitignore
```

---

## 🌐 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | ❌ | Create new user account |
| `POST` | `/api/auth/login` | ❌ | Get JWT access token |
| `GET` | `/api/auth/me` | ✅ | Get current user |
| `POST` | `/api/data/upload` | ✅ | Upload & auto-clean CSV |
| `GET` | `/api/data/list` | ✅ | List user datasets |
| `GET` | `/api/data/{id}/summary` | ✅ | Dataset stats + preview |
| `POST` | `/api/models/train` | ✅ | Train 5 AutoML models |
| `GET` | `/api/models/list/{id}` | ✅ | Model leaderboard |
| `GET` | `/api/models/feature-importance/...` | ✅ | Feature importance |
| `POST` | `/api/forecast/run` | ✅ | Generate future forecast |
| `POST` | `/api/simulator/run` | ✅ | What-If policy scenario |
| `GET` | `/api/reports/generate/{id}` | ✅ | Export analysis report |

> 📖 Full interactive docs at **http://localhost:8000/docs** (Swagger UI)

---

## 🤖 ML Models

| Model | Type | Best For |
|-------|------|----------|
| **XGBoost** | Gradient Boosting | High accuracy, handles non-linearity |
| **Random Forest** | Ensemble | Robust, handles overfitting |
| **SVR** | Support Vector | Small datasets, kernel tricks |
| **Bayesian Ridge** | Linear | Uncertainty quantification |
| **ARIMA** | Time Series | Pure time-series baseline |

### Feature Engineering
Automatically creates:
- **Lag features**: 1, 7, 14, 30-day lags for each signal
- **Rolling stats**: 7-day and 30-day moving averages & std deviations
- **Evaluation metrics**: MAE, RMSE, R², MAPE

### Sample Results (on sample data)

| Model | MAE | RMSE | R² | MAPE |
|-------|-----|------|----|------|
| XGBoost | 2.14 | 2.67 | 0.94 | 5.23% |
| Random Forest | 2.38 | 2.91 | 0.92 | 6.12% |
| Bayesian Ridge | 2.67 | 3.15 | 0.89 | 7.45% |
| SVR | 2.89 | 3.40 | 0.87 | 8.21% |
| ARIMA | 3.12 | 3.65 | 0.84 | 9.34% |

---

## 🎯 Data Format

```csv
date,me-fea,me-ang,me-sad,gh-death,gh-injure
2023-01-01,0.45,0.32,0.56,12.3,145.2
2023-01-02,0.48,0.35,0.58,13.1,148.5
```

| Column | Description | Range |
|--------|-------------|-------|
| `date` | Date of observation | YYYY-MM-DD |
| `me-fea` | Fear signal (social media) | 0.0 – 1.0 |
| `me-ang` | Anger signal (social media) | 0.0 – 1.0 |
| `me-sad` | Sadness signal (social media) | 0.0 – 1.0 |
| `gh-death` | Self-harm death rate (per 100k) | ≥ 0 |
| `gh-injure` | Self-harm injury rate (per 100k) | ≥ 0 |

---

## ☁️ Deploy to Render (Free)

1. Push to GitHub (already done!)
2. Go to [render.com](https://render.com) → **New Blueprint**
3. Connect your `6673csm/FAST_Dashboard` repository
4. Render reads `render.yaml` → auto-deploys both API and frontend

---

## ⚠️ Ethical Considerations

| ✅ Intended Use | ❌ Not For |
|---|---|
| National trend forecasting | Individual risk assessment |
| Public health policy planning | Clinical diagnosis |
| Intervention impact testing | Targeting individuals |
| Academic research | Medical advice |

---

## 📝 License

MIT License — Free for educational and research use.

---

## 👨‍💻 Author

**Sujay** · B.Tech CSE 2026 · India

[![GitHub](https://img.shields.io/badge/GitHub-6673csm-181717?style=flat-square&logo=github)](https://github.com/6673csm)

---

<div align="center">
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:7C4DFF,100:40C4FF&height=100&section=footer" />

**Built with passion for Public Health AI** 🧠
</div>
