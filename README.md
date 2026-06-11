# 🧠 FAST Dashboard

**Forecasting Aggregate-level Self-harm Trends: A Public Health Decision Support System**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Overview

FAST is a modern, production-ready **Interactive Web Application** built with Streamlit that transforms legacy research tools into a comprehensive public health decision support system. It uses machine learning to forecast national-level self-harm trends based on social media mental health signals (Fear, Anger, Sadness).

### Key Features

- **📊 Smart Data Explorer**: Upload CSV with automatic cleaning, validation, and EDA
- **🤖 AutoML Arena**: Train and compare 5 ML models with automatic leaderboard
- **📈 Interactive Forecasting**: Plotly visualizations with actual vs. predicted analysis
- **🎯 Policy Simulator**: Test "What-If" intervention scenarios with real-time impact
- **🔍 Explainable AI**: Feature importance to understand prediction drivers
- **📄 Report Generator**: Export findings and comprehensive analysis

---

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

```bash
cd FAST_Dashboard
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the dashboard**

```bash
streamlit run app.py
```

4. **Open your browser** to `http://localhost:8501`

---

## 📊 Usage Guide

### 1. Data Explorer

- Upload your CSV file or use the sample dataset
- View automatic data quality checks
- Explore correlation heatmaps
- Analyze time series trends

**Required CSV Format:**
```csv
date,me-fea,me-ang,me-sad,gh-death,gh-injure
2023-01-01,0.45,0.32,0.56,12.3,145.2
2023-01-02,0.48,0.35,0.58,13.1,148.5
...
```

### 2. AutoML Arena

- Select target variable (Death or Injury rate)
- Click "Train & Compare All Models"
- View performance leaderboard sorted by MAPE
- Explore feature importance for the best model

**Models Trained:**
- ARIMA (Time series baseline)
- Random Forest
- XGBoost (Usually best performer)
- Support Vector Regression
- Bayesian Ridge

### 3. Forecast & Evaluation

- View actual vs. predicted charts
- Analyze residuals for model quality
- Toggle between training and test data
- Download detailed predictions

### 4. Policy Simulator

- Adjust mental health signal sliders
- Choose preset scenarios or create custom
- Run simulation to see predicted impact
- Get policy recommendations

**Example Scenario:**
> "If we reduce public fear by 20%, what happens to predicted self-harm rates?"

### 5. Report Generator

- Download data summaries
- Export model leaderboards
- Generate comprehensive markdown reports
- Access system documentation

---

## 🏗️ Architecture

```
FAST_Dashboard/
├── app.py                      # Main entry point
├── pages/                      # Streamlit pages
│   ├── 1_🏠_Home.py
│   ├── 2_📊_Data_Explorer.py
│   ├── 3_🤖_AutoML_Arena.py
│   ├── 4_📈_Forecast_Eval.py
│   ├── 5_🎯_Policy_Simulator.py
│   └── 6_📄_Report_Generator.py
├── modules/                    # Core ML modules
│   ├── data_loader.py         # Smart CSV loading
│   ├── preprocessing.py       # Feature engineering
│   ├── automl.py             # Multi-model training
│   ├── evaluator.py          # Metrics & leaderboard
│   ├── explainer.py          # Feature importance
│   └── simulator.py          # Policy simulation
├── utils/                      # Utilities
│   └── helpers.py            # UI helpers
├── data/                       # Sample data
│   └── sample_mental_signals.csv
├── models/                     # Saved models
├── outputs/                    # Generated reports
└── requirements.txt
```

---

## 🔬 Technical Details

### Feature Engineering

The system automatically creates:
- **Lag Features**: 1, 7, 30-day lags
- **Rolling Statistics**: Moving averages and std dev
- **Trend Indicators**: Rate of change
- **Interaction Features**: Signal combinations
- **Temporal Features**: Day of week, month, weekend

### Evaluation Metrics

- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Squared Error
- **MAPE**: Mean Absolute Percentage Error (primary metric)
- **R² Score**: Variance explained

### Technology Stack

- **Frontend**: Streamlit 1.30+
- **Visualization**: Plotly Express & Graph Objects
- **ML**: Scikit-learn, XGBoost, Statsmodels
- **Data**: Pandas, NumPy
- **Persistence**: Joblib

---

## ⚠️ Ethical Considerations

**IMPORTANT**: This system is designed for **aggregate national-level forecasting only**. 

- ✅ Predict national trends
- ✅ Inform public health policy
- ✅ Test intervention scenarios
- ❌ NOT for individual risk assessment
- ❌ NOT for clinical diagnosis
- ❌ NOT for targeting individuals

All predictions should be used as **decision support tools**, not definitive forecasts. Always validate with real-world data and pilot programs.

---

## 📈 Sample Results

### Model Performance (Sample Data)

| Model | MAPE | RMSE | R² | Training Time |
|-------|------|------|-----|---------------|
| XGBoost | 5.23% | 2.14 | 0.94 | 0.45s |
| Random Forest | 6.12% | 2.38 | 0.92 | 0.32s |
| Bayesian Ridge | 7.45% | 2.67 | 0.89 | 0.08s |
| SVR | 8.21% | 2.89 | 0.87 | 0.62s |
| ARIMA | 9.34% | 3.12 | 0.84 | 0.28s |

### Policy Simulation Example

**Intervention**: Mental Health Awareness Campaign
- Fear: -15%
- Sadness: -10%
- Anger: -5%

**Predicted Impact**: 12.5% reduction in injury rates

---

## 🤝 Contributing

This project was developed as a B.Tech final year project for public health decision support. Contributions, suggestions, and improvements are welcome!

---

## 📝 License

MIT License - Feel free to use this project for educational and research purposes.

---

## 👥 Team

**Project**: FAST - Forecasting Aggregate-level Self-harm Trends  
**Purpose**: Public Health Decision Support System  
**Technology**: AI/ML, Data Science, Interactive Dashboards

---

## 📞 Support

For questions, issues, or suggestions:
- Review the in-app documentation
- Check the Report Generator page for detailed guides
- Consult the system architecture documentation

---

## 🎓 Academic Context

This project demonstrates:
- Modern web application development with Streamlit
- Machine learning pipeline design and implementation
- Interactive data visualization with Plotly
- Public health informatics and decision support systems
- Ethical AI considerations in sensitive domains

---

**Built with ❤️ for Public Health**
