"""
Report Generator Page - FAST Dashboard
Export findings and generate comprehensive reports
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.helpers import inject_custom_css, show_success, show_error, show_info

st.set_page_config(
    page_title="Report Generator - FAST",
    page_icon="📄",
    layout="wide"
)

inject_custom_css()

st.title("📄 Report Generator")
st.markdown("Export findings, visualizations, and comprehensive reports")

st.markdown("---")

# Check if data is available
if not st.session_state.get('data_loaded', False):
    show_error("No data loaded! Please go to Data Explorer first.")
    st.stop()

# Report sections
st.markdown("### 📋 Available Reports")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Data Reports")
    
    # Data summary
    if st.button("📥 Download Data Summary", use_container_width=True):
        df = st.session_state.df
        summary = df.describe()
        csv = summary.to_csv()
        
        st.download_button(
            label="Save Data Summary CSV",
            data=csv,
            file_name=f"data_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        show_success("Data summary ready for download!")
    
    # Cleaned data
    if st.button("📥 Download Cleaned Dataset", use_container_width=True):
        df = st.session_state.df
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="Save Cleaned Data CSV",
            data=csv,
            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        show_success("Cleaned dataset ready for download!")

with col2:
    st.markdown("#### 🤖 Model Reports")
    
    # Leaderboard
    if 'leaderboard' in st.session_state:
        if st.button("📥 Download Model Leaderboard", use_container_width=True):
            leaderboard = st.session_state.leaderboard
            csv = leaderboard.to_csv(index=False)
            
            st.download_button(
                label="Save Leaderboard CSV",
                data=csv,
                file_name=f"model_leaderboard_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            show_success("Leaderboard ready for download!")
    else:
        st.info("Train models first to generate leaderboard")
    
    # Feature importance
    if 'feature_importance' in st.session_state:
        if st.button("📥 Download Feature Importance", use_container_width=True):
            importance = st.session_state.feature_importance
            csv = importance.to_csv(index=False)
            
            st.download_button(
                label="Save Feature Importance CSV",
                data=csv,
                file_name=f"feature_importance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            show_success("Feature importance ready for download!")
    else:
        st.info("Train models first to generate feature importance")

st.markdown("---")

# Comprehensive report
st.markdown("### 📝 Comprehensive Report")

if st.button("📄 Generate Full Report", type="primary", use_container_width=True):
    
    # Compile report
    report_content = f"""
# FAST Dashboard - Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This report summarizes the analysis conducted using the FAST (Forecasting Aggregate-level Self-harm Trends) Dashboard.

### Dataset Overview
"""
    
    if st.session_state.get('metadata'):
        metadata = st.session_state.metadata
        report_content += f"""
- **Total Records**: {metadata['cleaned_rows']:,}
- **Data Quality Score**: {metadata['data_quality_score']:.1f}%
- **Date Range**: {metadata['date_range'][0]} to {metadata['date_range'][1] if metadata['date_range'] else 'N/A'}
- **Missing Values**: {metadata['missing_values_after']}
"""
    
    report_content += "\n---\n\n## Model Performance\n\n"
    
    if 'leaderboard' in st.session_state:
        leaderboard = st.session_state.leaderboard
        best_model = leaderboard.iloc[0]
        
        report_content += f"""
### Best Performing Model: {best_model['Model']}

**Performance Metrics:**
- MAE: {best_model['MAE']:.4f}
- RMSE: {best_model['RMSE']:.4f}
- MAPE: {best_model['MAPE']:.2f}%
- R² Score: {best_model['R²']:.4f}
- Training Time: {best_model['Training Time (s)']:.2f}s

### All Models Comparison

"""
        report_content += leaderboard.to_markdown(index=False)
    
    report_content += "\n\n---\n\n## Feature Importance\n\n"
    
    if 'feature_importance' in st.session_state:
        importance = st.session_state.feature_importance.head(10)
        report_content += "### Top 10 Predictive Features\n\n"
        report_content += importance.to_markdown(index=False)
        
        top_feature = importance.iloc[0]
        report_content += f"\n\n**Key Finding**: {top_feature['Feature']} is the most important predictor, contributing {top_feature['Importance']:.1f}% to the model's predictions.\n"
    
    report_content += "\n\n---\n\n## Simulation Results\n\n"
    
    if 'simulation_results' in st.session_state:
        sim = st.session_state.simulation_results
        impact = sim['impact_metrics']
        interventions = sim['interventions']
        
        report_content += f"""
### Policy Intervention Simulation

**Interventions Applied:**
- Fear Signal: {interventions['me-fea']:+.0f}%
- Anger Signal: {interventions['me-ang']:+.0f}%
- Sadness Signal: {interventions['me-sad']:+.0f}%

**Predicted Impact:**
- Baseline Average: {impact['avg_baseline']:.2f}
- Simulated Average: {impact['avg_simulated']:.2f}
- Change: {impact['avg_change']:.2f} ({impact['pct_change']:+.1f}%)
- Direction: {impact['direction'].title()}

**Recommendation**: {'This intervention shows promise and warrants further investigation.' if impact['direction'] == 'reduction' else 'This intervention may be counterproductive and should be reconsidered.'}
"""
    else:
        report_content += "No simulation results available. Run the Policy Simulator to generate intervention analysis.\n"
    
    report_content += "\n\n---\n\n## Recommendations\n\n"
    
    report_content += """
### Next Steps

1. **Validation**: Validate model predictions with real-world data
2. **Pilot Testing**: Implement promising interventions in pilot programs
3. **Monitoring**: Establish continuous monitoring systems
4. **Iteration**: Refine models as new data becomes available

### Ethical Considerations

⚠️ **Important**: This system predicts aggregate national-level trends only, NOT individual risk assessment. 
All predictions should be used as decision support tools, not definitive forecasts.

---

## About FAST

FAST (Forecasting Aggregate-level Self-harm Trends) is an AI-powered decision support system designed 
to help policymakers predict and prevent self-harm at the national level using machine learning and 
social media mental health signals.

**Developed for**: Public Health Decision Support  
**Version**: 1.0  
**Technology**: Streamlit, Scikit-learn, XGBoost, Plotly
"""
    
    # Display report
    st.markdown(report_content)
    
    # Download button
    st.download_button(
        label="📥 Download Full Report (Markdown)",
        data=report_content,
        file_name=f"FAST_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )
    
    show_success("Report generated successfully!")

st.markdown("---")

# System documentation
st.markdown("### 📚 System Documentation")

with st.expander("View System Architecture", expanded=False):
    st.markdown("""
    ## System Architecture
    
    ### Components
    
    1. **Data Layer**
       - CSV upload and validation
       - Auto-cleaning and preprocessing
       - Feature engineering
    
    2. **ML Layer**
       - 5 model training pipeline (ARIMA, RF, XGBoost, SVR, Bayesian Ridge)
       - Automated evaluation and comparison
       - Model persistence
    
    3. **Presentation Layer**
       - Interactive Streamlit dashboard
       - Plotly visualizations
       - Real-time simulation
    
    ### Technology Stack
    
    - **Frontend**: Streamlit
    - **Visualization**: Plotly Express & Graph Objects
    - **ML**: Scikit-learn, XGBoost, Statsmodels
    - **Data**: Pandas, NumPy
    
    ### Data Flow
    
    ```
    CSV Upload → Auto-Clean → Feature Engineering → Model Training → 
    Evaluation → Leaderboard → Forecasting → Policy Simulation → Reports
    ```
    """)

with st.expander("View Usage Guide", expanded=False):
    st.markdown("""
    ## Usage Guide
    
    ### Getting Started
    
    1. **Upload Data**: Go to Data Explorer and upload CSV or use sample data
    2. **Explore**: Review correlations and time series plots
    3. **Train Models**: Navigate to AutoML Arena and train all models
    4. **Evaluate**: View forecasts and residual analysis
    5. **Simulate**: Test policy interventions in Policy Simulator
    6. **Report**: Generate and download comprehensive reports
    
    ### Data Format Requirements
    
    Your CSV must contain:
    - `date`: Date column (YYYY-MM-DD)
    - `me-fea`: Fear signal (0-1)
    - `me-ang`: Anger signal (0-1)
    - `me-sad`: Sadness signal (0-1)
    - `gh-death`: Death rate (positive number)
    - `gh-injure`: Injury rate (positive number)
    
    ### Best Practices
    
    - Use at least 90 days of data for reliable predictions
    - Validate model predictions with holdout data
    - Test multiple intervention scenarios
    - Consider ethical implications of predictions
    - Use as decision support, not definitive forecasts
    """)

with st.expander("View Model Details", expanded=False):
    st.markdown("""
    ## Model Details
    
    ### ARIMA
    - **Type**: Time series model
    - **Use Case**: Baseline, captures temporal patterns
    - **Pros**: Simple, interpretable
    - **Cons**: Limited feature usage
    
    ### Random Forest
    - **Type**: Ensemble (decision trees)
    - **Use Case**: Non-linear patterns
    - **Pros**: Robust, feature importance
    - **Cons**: Can overfit
    
    ### XGBoost
    - **Type**: Gradient boosting
    - **Use Case**: Best overall performance
    - **Pros**: High accuracy, handles complex patterns
    - **Cons**: Requires tuning
    
    ### SVR
    - **Type**: Support vector regression
    - **Use Case**: Small datasets
    - **Pros**: Good generalization
    - **Cons**: Slower training
    
    ### Bayesian Ridge
    - **Type**: Probabilistic linear model
    - **Use Case**: Uncertainty quantification
    - **Pros**: Regularization, probabilistic
    - **Cons**: Assumes linearity
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
    <p><strong>FAST Dashboard v1.0</strong></p>
    <p>For questions or support, please contact your system administrator.</p>
</div>
""", unsafe_allow_html=True)
