"""
Data Explorer Page - FAST Dashboard
Upload, clean, and explore data with EDA
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.data_loader import load_data, validate_data, get_data_summary
from modules.explainer import create_correlation_heatmap, identify_key_correlations
from utils.helpers import inject_custom_css, show_success, show_error, show_info

st.set_page_config(
    page_title="Data Explorer - FAST",
    page_icon="📊",
    layout="wide"
)

inject_custom_css()

st.title("📊 Data Explorer")
st.markdown("Upload and explore your mental health signals dataset")

st.markdown("---")

# File upload section
st.markdown("### 📁 Upload Data")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload CSV file with mental health signals",
        type=['csv'],
        help="CSV should contain: date, me-fea, me-ang, me-sad, gh-death, gh-injure"
    )

with col2:
    use_sample = st.checkbox("Use sample dataset", value=True)
    
    if use_sample:
        show_info("Using built-in sample dataset (365 days)")

# Load data
if uploaded_file is not None or use_sample:
    with st.spinner("Loading and cleaning data..."):
        default_path = "data/sample_mental_signals.csv" if use_sample else None
        df, metadata = load_data(uploaded_file, default_path)
    
    if df is not None:
        # Store in session state
        st.session_state.df = df
        st.session_state.metadata = metadata
        st.session_state.data_loaded = True
        
        show_success(f"Data loaded successfully! {metadata['cleaned_rows']} rows, {metadata['cleaned_cols']} columns")
        
        # Data quality metrics
        st.markdown("### 📈 Data Quality Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{metadata['cleaned_rows']:,}")
        
        with col2:
            st.metric("Quality Score", f"{metadata['data_quality_score']:.1f}%")
        
        with col3:
            missing_pct = (metadata['missing_values_after'] / (metadata['cleaned_rows'] * metadata['cleaned_cols'])) * 100
            st.metric("Missing Values", f"{missing_pct:.1f}%")
        
        with col4:
            if metadata['date_range']:
                date_span = (metadata['date_range'][1] - metadata['date_range'][0]).days
                st.metric("Date Range", f"{date_span} days")
        
        st.markdown("---")
        
        # Data validation
        st.markdown("### ✅ Data Validation")
        
        validations = validate_data(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            for key, value in list(validations.items())[:3]:
                status = "✅" if value else "❌"
                st.markdown(f"{status} **{key.replace('_', ' ').title()}**: {'Pass' if value else 'Fail'}")
        
        with col2:
            for key, value in list(validations.items())[3:]:
                status = "✅" if value else "❌"
                st.markdown(f"{status} **{key.replace('_', ' ').title()}**: {'Pass' if value else 'Fail'}")
        
        if all(validations.values()):
            show_success("All validation checks passed!")
        else:
            show_error("Some validation checks failed. Please review your data.")
        
        st.markdown("---")
        
        # Data preview
        st.markdown("### 👀 Data Preview")
        
        st.dataframe(
            df.head(20),
            use_container_width=True,
            height=400
        )
        
        # Download cleaned data
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # Summary statistics
        st.markdown("### 📊 Summary Statistics")
        
        summary = get_data_summary(df)
        st.dataframe(summary, use_container_width=True)
        
        st.markdown("---")
        
        # Correlation heatmap
        st.markdown("### 🔥 Correlation Heatmap")
        
        st.markdown("""
        This heatmap shows correlations between mental signals and self-harm rates.
        **Strong correlations** (closer to 1 or -1) indicate predictive relationships.
        """)
        
        # Select numeric columns only
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        
        if len(numeric_df.columns) > 1:
            fig = create_correlation_heatmap(numeric_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Key correlations
            st.markdown("#### 🔍 Key Correlations")
            
            key_corrs = identify_key_correlations(numeric_df, threshold=0.5)
            
            if not key_corrs.empty:
                st.dataframe(key_corrs, use_container_width=True)
                
                # Interpretation
                st.markdown("**Interpretation:**")
                for idx, row in key_corrs.head(3).iterrows():
                    st.markdown(f"- **{row['Feature 1']}** and **{row['Feature 2']}** have a **{row['Strength'].lower()}** correlation of **{row['Correlation']:.2f}**")
            else:
                show_info("No strong correlations found (threshold: 0.5)")
        
        st.markdown("---")
        
        # Time series plots
        st.markdown("### 📈 Time Series Visualization")
        
        if 'date' in df.columns:
            # Select variable to plot
            signal_cols = ['me-fea', 'me-ang', 'me-sad']
            target_cols = ['gh-death', 'gh-injure']
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_signals = st.multiselect(
                    "Select Mental Signals",
                    signal_cols,
                    default=signal_cols
                )
            
            with col2:
                selected_targets = st.multiselect(
                    "Select Targets",
                    target_cols,
                    default=target_cols
                )
            
            # Plot signals
            if selected_signals:
                st.markdown("#### Mental Health Signals Over Time")
                
                fig = px.line(
                    df.reset_index(),
                    x='date',
                    y=selected_signals,
                    title="Mental Health Signals Trends",
                    labels={'value': 'Signal Strength', 'variable': 'Signal Type'}
                )
                
                fig.update_layout(
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Plot targets
            if selected_targets:
                st.markdown("#### Self-Harm Rates Over Time")
                
                fig = px.line(
                    df.reset_index(),
                    x='date',
                    y=selected_targets,
                    title="Self-Harm Rates Trends",
                    labels={'value': 'Rate', 'variable': 'Type'}
                )
                
                fig.update_layout(
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Next steps
        st.markdown("### ⏭️ Next Steps")
        
        st.markdown("""
        Data is ready! You can now:
        1. Go to **AutoML Arena** to train models
        2. View **Forecast & Evaluation** for predictions
        3. Try the **Policy Simulator** to test interventions
        """)
        
        if st.button("🤖 Go to AutoML Arena", use_container_width=True):
            st.switch_page("pages/3_🤖_AutoML_Arena.py")
    
    else:
        show_error("Failed to load data. Please check your file format.")

else:
    st.info("👆 Please upload a CSV file or use the sample dataset to get started.")
    
    st.markdown("""
    ### 📋 Required Data Format
    
    Your CSV file should contain the following columns:
    
    - **date**: Date in YYYY-MM-DD format
    - **me-fea**: Fear signal (0-1)
    - **me-ang**: Anger signal (0-1)
    - **me-sad**: Sadness signal (0-1)
    - **gh-death**: Death rate (positive number)
    - **gh-injure**: Injury rate (positive number)
    
    ### 📥 Sample Data Template
    
    ```csv
    date,me-fea,me-ang,me-sad,gh-death,gh-injure
    2023-01-01,0.45,0.32,0.56,12.3,145.2
    2023-01-02,0.48,0.35,0.58,13.1,148.5
    ...
    ```
    """)
