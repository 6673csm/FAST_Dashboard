"""
FAST Dashboard - Main Entry Point
Forecasting Aggregate-level Self-harm Trends
A Public Health Decision Support System
"""

import streamlit as st
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from utils.helpers import inject_custom_css

# Page configuration
st.set_page_config(
    page_title="FAST Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "FAST - Forecasting Aggregate-level Self-harm Trends. A Public Health Decision Support System."
    }
)

# Inject custom CSS
inject_custom_css()

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'models_trained' not in st.session_state:
    st.session_state.models_trained = {}
if 'df' not in st.session_state:
    st.session_state.df = None
if 'metadata' not in st.session_state:
    st.session_state.metadata = None

# Main page
st.title("🧠 FAST Dashboard")
st.markdown("### Forecasting Aggregate-level Self-harm Trends")
st.markdown("**A Public Health Decision Support System**")

st.markdown("---")

# Hero section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Welcome to FAST
    
    This interactive dashboard uses **machine learning** to forecast national-level self-harm trends 
    based on social media mental health signals (Fear, Anger, Sadness).
    
    ### 🎯 Key Features:
    
    - **📊 Smart Data Explorer**: Upload data with automatic cleaning and EDA
    - **🤖 AutoML Arena**: Train and compare 5 different ML models
    - **📈 Interactive Forecasting**: Visualize predictions with Plotly
    - **🎯 Policy Simulator**: Test "What-If" intervention scenarios
    - **🔍 Explainable AI**: Understand which factors drive predictions
    - **📄 Report Generator**: Export findings and visualizations
    
    ### 🚀 Getting Started:
    
    1. Navigate to **Data Explorer** to upload your data
    2. Go to **AutoML Arena** to train models
    3. View **Forecast & Evaluation** for predictions
    4. Try the **Policy Simulator** to test interventions
    """)

with col2:
    st.markdown("### 📊 Quick Stats")
    
    if st.session_state.data_loaded and st.session_state.metadata:
        metadata = st.session_state.metadata
        
        st.metric(
            "Total Records",
            f"{metadata['cleaned_rows']:,}",
            delta=None
        )
        
        st.metric(
            "Data Quality Score",
            f"{metadata['data_quality_score']:.1f}%",
            delta=None
        )
        
        st.metric(
            "Models Trained",
            len(st.session_state.models_trained),
            delta=None
        )
    else:
        st.info("📁 No data loaded yet. Go to **Data Explorer** to get started!")

st.markdown("---")

# System status
st.markdown("### 🔧 System Status")

col1, col2, col3 = st.columns(3)

with col1:
    data_status = "✅ Loaded" if st.session_state.data_loaded else "⏳ Not Loaded"
    st.markdown(f"**Data:** {data_status}")

with col2:
    models_count = len(st.session_state.models_trained)
    models_status = f"✅ {models_count} Trained" if models_count > 0 else "⏳ Not Trained"
    st.markdown(f"**Models:** {models_status}")

with col3:
    ready_status = "✅ Ready" if st.session_state.data_loaded and models_count > 0 else "⏳ Setup Required"
    st.markdown(f"**System:** {ready_status}")

st.markdown("---")

# Quick actions
st.markdown("### ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Upload Data", use_container_width=True):
        st.switch_page("pages/2_📊_Data_Explorer.py")

with col2:
    if st.button("🤖 Train Models", use_container_width=True):
        st.switch_page("pages/3_🤖_AutoML_Arena.py")

with col3:
    if st.button("📈 View Forecasts", use_container_width=True):
        st.switch_page("pages/4_📈_Forecast_Eval.py")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
    <p><strong>FAST Dashboard v1.0</strong></p>
    <p>Developed for Public Health Decision Support</p>
    <p><em>⚠️ This system predicts aggregate national trends only, NOT individual risk assessment.</em></p>
</div>
""", unsafe_allow_html=True)
