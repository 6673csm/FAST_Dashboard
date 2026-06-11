"""
Geographic Intelligence Page - FAST Dashboard
Regional risk analysis and geographic visualizations
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from modules import geo_intelligence
from utils.helpers import inject_custom_css, show_success, show_error, show_warning, show_info

st.set_page_config(
    page_title="Geographic Intelligence - FAST",
    page_icon="🗺️",
    layout="wide"
)

inject_custom_css()

st.title("🗺️ Geographic Intelligence Dashboard")
st.markdown("**Regional risk analysis and location-based insights for India**")

st.markdown("---")

# Check if regional data is loaded
if not st.session_state.get('data_loaded', False):
    show_warning("⚠️ No data loaded! Please go to Data Explorer first.")
    if st.button("📊 Go to Data Explorer"):
        st.switch_page("pages/2_📊_Data_Explorer.py")
    st.stop()

df = st.session_state.df

# Check if data has regional columns
required_cols = ['region', 'population']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    show_error(f"❌ Regional data not found! Missing columns: {', '.join(missing_cols)}")
    st.info("""
    ### 📍 How to Load Regional Data
    
    The geographic features require data with regional information. Your dataset needs:
    - **region**: State/region name (e.g., "Maharashtra", "Delhi")
    - **population**: Population of the region
    
    **Option 1**: Use the pre-generated regional dataset:
    - File: `data/sample_mental_signals_regional.csv`
    - This file was generated with 8 Indian states and 32 districts
    
    **Option 2**: Add regional columns to your existing data
    """)
    
    # Offer to load the regional dataset
    if st.button("📥 Load Regional Dataset", type="primary"):
        try:
            regional_df = pd.read_csv('data/sample_mental_signals_regional.csv')
            regional_df['date'] = pd.to_datetime(regional_df['date'])
            st.session_state.df = regional_df
            st.session_state.data_loaded = True
            show_success("✅ Regional dataset loaded successfully!")
            st.rerun()
        except Exception as e:
            show_error(f"❌ Error loading regional dataset: {str(e)}")
    
    st.stop()

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")

# Target selection
target = st.sidebar.selectbox(
    "Select Risk Metric",
    ["GH-Death", "GH-Injure"],
    format_func=lambda x: "Death Rate" if x == "GH-Death" else "Injury Rate"
)

# Date range filter
if 'date' in df.columns:
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )
    
    # Filter data by date
    if len(date_range) == 2:
        mask = (df['date'] >= pd.Timestamp(date_range[0])) & (df['date'] <= pd.Timestamp(date_range[1]))
        df_filtered = df[mask]
    else:
        df_filtered = df
else:
    df_filtered = df

# Calculate regional statistics
regional_stats = geo_intelligence.calculate_regional_risk(
    df_filtered,
    target_col=target,
    region_col='region'
)

# Main content
st.markdown("### 📊 Regional Risk Overview")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Regions", len(regional_stats))

with col2:
    high_risk_count = len(regional_stats[regional_stats['risk_category'] == 'High'])
    st.metric("High Risk Regions", high_risk_count, delta=None if high_risk_count == 0 else f"{high_risk_count} alerts")

with col3:
    avg_risk = regional_stats['avg_risk'].mean()
    st.metric("Average Risk", f"{avg_risk:.2f}")

with col4:
    max_risk_region = regional_stats.loc[regional_stats['avg_risk'].idxmax(), 'region']
    st.metric("Highest Risk Region", max_risk_region)

st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Risk Map", "📊 Regional Comparison", "⚠️ Alerts", "📈 Trends"])

with tab1:
    st.subheader("🗺️ India Risk Heatmap")
    st.markdown("""
    This map shows risk levels across different regions of India. 
    Larger and redder circles indicate higher risk areas.
    """)
    
    # Create choropleth map
    map_fig = geo_intelligence.create_india_choropleth(
        regional_stats,
        value_column='risk_score',
        title=f"{target} Risk Heatmap - India"
    )
    st.plotly_chart(map_fig, use_container_width=True)
    
    # Regional statistics table
    st.subheader("📋 Regional Statistics")
    
    display_df = regional_stats[['region', 'avg_risk', 'risk_per_100k', 'risk_score', 'risk_category', 'population']].copy()
    display_df.columns = ['Region', 'Avg Risk', 'Per 100k', 'Risk Score', 'Category', 'Population']
    
    st.dataframe(
        display_df.style.background_gradient(
            subset=['Risk Score'],
            cmap='Reds'
        ).format({
            'Avg Risk': '{:.2f}',
            'Per 100k': '{:.2f}',
            'Risk Score': '{:.1f}',
            'Population': '{:,.0f}'
        }),
        use_container_width=True,
        height=400
    )

with tab2:
    st.subheader("📊 Regional Comparison")
    
    # Metric selector
    comparison_metric = st.selectbox(
        "Select Metric to Compare",
        ['avg_risk', 'risk_per_100k', 'max_risk', 'std_risk'],
        format_func=lambda x: {
            'avg_risk': 'Average Risk',
            'risk_per_100k': 'Risk per 100,000 Population',
            'max_risk': 'Maximum Risk',
            'std_risk': 'Risk Variability (Std Dev)'
        }[x]
    )
    
    # Create comparison chart
    comparison_fig = geo_intelligence.create_regional_comparison(
        regional_stats,
        metric=comparison_metric
    )
    st.plotly_chart(comparison_fig, use_container_width=True)
    
    # Top/Bottom regions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Top 5 Highest Risk")
        top_5 = regional_stats.nlargest(5, comparison_metric)[['region', comparison_metric]]
        top_5.columns = ['Region', comparison_metric.replace('_', ' ').title()]
        st.dataframe(
            top_5.style.format({comparison_metric.replace('_', ' ').title(): '{:.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("#### 🟢 Top 5 Lowest Risk")
        bottom_5 = regional_stats.nsmallest(5, comparison_metric)[['region', comparison_metric]]
        bottom_5.columns = ['Region', comparison_metric.replace('_', ' ').title()]
        st.dataframe(
            bottom_5.style.format({comparison_metric.replace('_', ' ').title(): '{:.2f}'}),
            use_container_width=True,
            hide_index=True
        )

with tab3:
    st.subheader("⚠️ Regional Alerts")
    st.markdown("Automated alerts for regions requiring attention")
    
    # Alert threshold configuration
    col1, col2 = st.columns(2)
    with col1:
        high_threshold = st.slider("High Risk Threshold", 50, 100, 75, 5)
    with col2:
        medium_threshold = st.slider("Medium Risk Threshold", 0, 75, 50, 5)
    
    # Generate alerts
    alerts = geo_intelligence.generate_regional_alerts(
        regional_stats,
        threshold_high=high_threshold,
        threshold_medium=medium_threshold
    )
    
    if len(alerts) == 0:
        show_success("✅ No alerts! All regions are within acceptable risk levels.")
    else:
        st.markdown(f"**{len(alerts)} Alert(s) Generated**")
        
        for alert in alerts:
            if alert['severity'] == 'HIGH':
                st.error(alert['message'])
            else:
                st.warning(alert['message'])
        
        # Alert summary table
        st.markdown("#### Alert Summary")
        alert_df = pd.DataFrame(alerts)[['region', 'severity', 'risk_score']]
        alert_df.columns = ['Region', 'Severity', 'Risk Score']
        st.dataframe(
            alert_df.style.format({'Risk Score': '{:.1f}'}),
            use_container_width=True,
            hide_index=True
        )

with tab4:
    st.subheader("📈 Regional Trends Over Time")
    
    if 'date' in df_filtered.columns:
        st.markdown("Track how risk levels change across regions over time")
        
        # Create trend chart
        trend_fig = geo_intelligence.create_trend_by_region(
            df_filtered,
            target_col=target,
            date_col='date',
            region_col='region'
        )
        st.plotly_chart(trend_fig, use_container_width=True)
        
        # Trend analysis
        st.markdown("#### 📊 Trend Analysis")
        
        # Calculate trend direction for each region
        trend_analysis = []
        for region in df_filtered['region'].unique():
            region_data = df_filtered[df_filtered['region'] == region].sort_values('date')
            if len(region_data) >= 2:
                first_half = region_data[target].iloc[:len(region_data)//2].mean()
                second_half = region_data[target].iloc[len(region_data)//2:].mean()
                change = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
                
                trend_analysis.append({
                    'Region': region,
                    'Trend': 'Increasing ↗️' if change > 5 else 'Decreasing ↘️' if change < -5 else 'Stable →',
                    'Change %': change
                })
        
        trend_df = pd.DataFrame(trend_analysis)
        st.dataframe(
            trend_df.style.format({'Change %': '{:.1f}%'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Time series data not available. Please ensure your dataset has a 'date' column.")

st.markdown("---")

# Export functionality
st.markdown("### 📥 Export Regional Analysis")

col1, col2 = st.columns(2)

with col1:
    # Export regional statistics
    csv = regional_stats.to_csv(index=False)
    st.download_button(
        label="📊 Download Regional Statistics",
        data=csv,
        file_name=f"regional_statistics_{target}.csv",
        mime="text/csv"
    )

with col2:
    # Export alerts
    if len(alerts) > 0:
        alerts_csv = pd.DataFrame(alerts).to_csv(index=False)
        st.download_button(
            label="⚠️ Download Alerts",
            data=alerts_csv,
            file_name=f"regional_alerts_{target}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
### 📚 About Geographic Intelligence

This dashboard provides location-based insights for mental health risk assessment:
- **Risk Heatmaps**: Visualize risk distribution across India
- **Regional Comparison**: Compare metrics across different states
- **Automated Alerts**: Get notified about high-risk regions
- **Trend Analysis**: Track changes over time by location

Use these insights for targeted interventions and resource allocation.
""")
