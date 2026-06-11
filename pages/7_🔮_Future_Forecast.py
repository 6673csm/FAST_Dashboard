"""
Future Forecast Page - FAST Dashboard
Predict death and injury cases for the next 2-3 months
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.forecaster import (
    forecast_future,
    calculate_monthly_aggregates,
    generate_forecast_summary
)
from utils.helpers import inject_custom_css, show_success, show_error, show_warning, show_info

st.set_page_config(
    page_title="Future Forecast - FAST",
    page_icon="🔮",
    layout="wide"
)

inject_custom_css()

st.title("🔮 Future Forecast")
st.markdown("Predict death and injury cases for the next 2-3 months based on current trends")

st.markdown("---")

# Check if models are trained
if not st.session_state.get('models_trained', {}):
    show_warning("No models trained yet! Please go to AutoML Arena first.")
    
    if st.button("🤖 Go to AutoML Arena"):
        st.switch_page("pages/3_🤖_AutoML_Arena.py")
    
    st.stop()

# Get current target and models
current_target = st.session_state.get('current_target', 'gh-death')
engine = st.session_state.models_trained.get(current_target)

if engine is None:
    show_error(f"No models trained for {current_target}")
    st.stop()

# Get best model
best_model_name = st.session_state.get('best_model_name', 'XGBoost')
model = engine.models.get(f"{best_model_name}_{current_target}")

if model is None:
    show_error("Best model not found")
    st.stop()

# Get data
df = st.session_state.df
scaler = st.session_state.scaler
feature_names = st.session_state.feature_names

st.markdown(f"""
### 🎯 Current Configuration

- **Target Variable**: {current_target.upper().replace('-', ' ').title()}
- **Model Used**: {best_model_name}
- **Historical Data**: {len(df)} days
""")

st.markdown("---")

# Forecast settings
st.markdown("### ⚙️ Forecast Settings")

col1, col2, col3 = st.columns(3)

with col1:
    forecast_days = st.slider(
        "Forecast Period (days)",
        min_value=30,
        max_value=180,
        value=90,
        step=30,
        help="Number of days to forecast into the future"
    )
    
    forecast_months = forecast_days // 30
    st.info(f"📅 Forecasting approximately **{forecast_months} months** ahead")

with col2:
    extrapolation_method = st.selectbox(
        "Signal Extrapolation Method",
        ["moving_average", "last_value", "trend"],
        format_func=lambda x: {
            "moving_average": "30-Day Moving Average (Recommended)",
            "last_value": "Last Observed Value",
            "trend": "Linear Trend Extrapolation"
        }[x],
        help="Method to project mental health signals into the future"
    )

with col3:
    population = st.number_input(
        "Population Size",
        min_value=100000,
        max_value=10000000,
        value=1000000,
        step=100000,
        help="Population size for converting rates to actual case counts"
    )
    st.info(f"👥 {population/1000000:.1f}M population")

st.markdown("---")

# Generate forecast button
if st.button("🔮 Generate Future Forecast", type="primary", use_container_width=True):
    
    with st.spinner(f"Generating {forecast_days}-day forecast..."):
        try:
            # Generate forecast
            future_signals, forecast_df = forecast_future(
                model=model,
                model_name=best_model_name,
                historical_df=df,
                scaler=scaler,
                feature_names=feature_names,
                n_days=forecast_days,
                extrapolation_method=extrapolation_method,
                population=population
            )
            
            # Store results
            st.session_state.future_forecast = {
                'forecast_df': forecast_df,
                'future_signals': future_signals,
                'forecast_days': forecast_days,
                'target': current_target,
                'model': best_model_name
            }
            
            show_success(f"✅ Successfully generated {forecast_days}-day forecast!")
            
        except Exception as e:
            show_error(f"Error generating forecast: {str(e)}")
            st.stop()

# Display results if available
if 'future_forecast' in st.session_state:
    results = st.session_state.future_forecast
    forecast_df = results['forecast_df']
    future_signals = results['future_signals']
    
    st.markdown("---")
    
    # Calculate historical average cases for comparison
    # Convert historical rates to cases
    historical_rates = df[current_target].values
    historical_cases = (historical_rates * population) / 100000
    historical_avg_cases = historical_cases.mean()
    
    # Generate summary
    summary = generate_forecast_summary(forecast_df, current_target, historical_avg_cases)
    st.markdown(summary)
    
    st.markdown("---")
    
    # Visualization
    st.markdown("### 📈 Forecast Visualization")
    
    # Create combined historical + forecast plot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f"Predicted {current_target.upper().replace('-', ' ').title()} - Next {forecast_days} Days",
            "Mental Health Signals (Extrapolated)"
        ),
        vertical_spacing=0.12,
        row_heights=[0.6, 0.4]
    )
    
    # Historical data (last 90 days)
    historical_recent = df.tail(90)
    if 'date' in historical_recent.columns:
        hist_dates = pd.to_datetime(historical_recent['date'])
    else:
        hist_dates = historical_recent.index
    
    # Add historical data
    fig.add_trace(
        go.Scatter(
            x=hist_dates,
            y=historical_recent[current_target],
            mode='lines',
            name='Historical',
            line=dict(color='#636EFA', width=2),
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Add forecast
    fig.add_trace(
        go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_cases'],
            mode='lines',
            name='Forecast',
            line=dict(color='#EF553B', width=2, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Add confidence band (simple ±10% for illustration)
    upper_bound = forecast_df['predicted_cases'] * 1.1
    lower_bound = forecast_df['predicted_cases'] * 0.9
    
    fig.add_trace(
        go.Scatter(
            x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
            y=upper_bound.tolist() + lower_bound.tolist()[::-1],
            fill='toself',
            fillcolor='rgba(239, 85, 59, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Band (±10%)',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Add mental health signals
    colors = {'me-fea': '#FFA15A', 'me-ang': '#FF6692', 'me-sad': '#AB63FA'}
    names = {'me-fea': 'Fear', 'me-ang': 'Anger', 'me-sad': 'Sadness'}
    
    for signal in ['me-fea', 'me-ang', 'me-sad']:
        fig.add_trace(
            go.Scatter(
                x=forecast_df['date'],
                y=forecast_df[signal],
                mode='lines',
                name=names[signal],
                line=dict(color=colors[signal], width=2),
                showlegend=True
            ),
            row=2, col=1
        )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    case_label = "Deaths" if "death" in current_target else "Injuries"
    fig.update_yaxes(title_text=f"Number of {case_label}", row=1, col=1)
    fig.update_yaxes(title_text="Signal Intensity (0-1)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Monthly aggregates
    st.markdown("### 📅 Monthly Predictions")
    
    monthly_agg = calculate_monthly_aggregates(forecast_df)
    
    # Rename columns for display
    display_monthly = monthly_agg.copy()
    case_label = "Deaths" if "death" in current_target else "Injuries"
    
    column_rename = {
        'month': 'Month',
        'predicted_cases_mean': f'Avg Daily {case_label}',
        'predicted_cases_min': f'Min Daily {case_label}',
        'predicted_cases_max': f'Max Daily {case_label}',
        'predicted_cases_sum': f'Total {case_label}',
        'me-fea_mean': 'Avg Fear',
        'me-ang_mean': 'Avg Anger',
        'me-sad_mean': 'Avg Sadness'
    }
    
    display_monthly = display_monthly.rename(columns=column_rename)
    
    st.dataframe(
        display_monthly.style.background_gradient(
            subset=[f'Total {case_label}'],
            cmap='RdYlGn_r'
        ).format({
            f'Avg Daily {case_label}': '{:.0f}',
            f'Min Daily {case_label}': '{:.0f}',
            f'Max Daily {case_label}': '{:.0f}',
            f'Total {case_label}': '{:,.0f}'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Detailed forecast table
    st.markdown("### 📋 Detailed Daily Forecast")
    
    
    display_df = forecast_df[['date', 'predicted_cases', 'me-fea', 'me-ang', 'me-sad']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    
    case_label = "Deaths" if "death" in current_target else "Injuries"
    
    display_df = display_df.rename(columns={
        'date': 'Date',
        'predicted_cases': f'Predicted {case_label}',
        'me-fea': 'Fear Signal',
        'me-ang': 'Anger Signal',
        'me-sad': 'Sadness Signal'
    })
    
    st.dataframe(
        display_df.style.background_gradient(
            subset=[f'Predicted {case_label}'],
            cmap='RdYlGn_r'
        ).format({
            f'Predicted {case_label}': '{:.0f}'
        }),
        use_container_width=True,
        height=400
    )
    
    # Download forecast
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Forecast CSV",
        data=csv,
        file_name=f"future_forecast_{current_target}_{forecast_days}days.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    forecast_avg = forecast_df['predicted_cases'].mean()
    change_pct = ((forecast_avg - historical_avg_cases) / historical_avg_cases) * 100
    
    if change_pct > 10:
        st.markdown("""
        #### ⚠️ Increasing Trend Detected
        
        The model predicts a significant increase in cases. Consider:
        
        1. **Immediate Action**: Implement preventive interventions now
        2. **Resource Allocation**: Increase mental health support services
        3. **Public Awareness**: Launch awareness campaigns
        4. **Monitoring**: Set up real-time monitoring systems
        5. **Policy Simulator**: Test intervention strategies to reduce predicted rates
        """)
    elif change_pct < -10:
        st.markdown("""
        #### ✅ Decreasing Trend Detected
        
        The model predicts a decrease in cases. Recommendations:
        
        1. **Maintain Efforts**: Continue current successful interventions
        2. **Document Success**: Record what's working for future reference
        3. **Stay Vigilant**: Monitor for any trend reversals
        4. **Optimize Resources**: Reallocate resources to other priorities
        """)
    else:
        st.markdown("""
        #### 📊 Stable Trend Detected
        
        The model predicts relatively stable rates. Recommendations:
        
        1. **Maintain Status Quo**: Current strategies appear effective
        2. **Continuous Monitoring**: Watch for emerging patterns
        3. **Proactive Planning**: Prepare for potential future changes
        4. **Test Interventions**: Use Policy Simulator to explore improvements
        """)
    
    st.markdown("---")
    
    # Important notes
    st.markdown("""
    ### ⚠️ Important Notes
    
    - **Uncertainty**: Forecasts become less reliable further into the future
    - **Assumptions**: Based on extrapolated mental health signals - actual signals may differ
    - **External Factors**: Cannot account for unforeseen events (policy changes, major incidents)
    - **Decision Support**: Use as one input among many for decision-making
    - **Update Regularly**: Re-run forecasts as new data becomes available
    """)

else:
    st.info("👆 Configure settings above and click 'Generate Future Forecast' to predict future cases!")
    
    st.markdown("""
    ### 🔮 How Future Forecasting Works
    
    1. **Signal Extrapolation**: Projects mental health signals (Fear, Anger, Sadness) into the future
       - **Moving Average**: Uses 30-day average (smooths volatility) ✅ Recommended
       - **Last Value**: Assumes signals stay constant
       - **Trend**: Extrapolates recent trends linearly
    
    2. **Feature Engineering**: Creates same features used in training (lags, rolling stats, etc.)
    
    3. **Model Prediction**: Best-performing model predicts death/injury rates
    
    4. **Monthly Aggregation**: Summarizes daily predictions into monthly estimates
    
    ### 📊 Use Cases
    
    - **Budget Planning**: Estimate resource needs for next quarter
    - **Policy Planning**: Decide when to implement interventions
    - **Capacity Planning**: Prepare mental health services
    - **Early Warning**: Detect concerning trends before they escalate
    
    ### 🎯 Best Practices
    
    - Use **90 days (3 months)** for reliable forecasts
    - Choose **Moving Average** for stable predictions
    - Update forecasts **monthly** with new data
    - Combine with **Policy Simulator** to test interventions
    - Always validate predictions with domain experts
    """)

st.markdown("---")

# Next steps
st.markdown("### ⏭️ Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎯 Test Interventions", use_container_width=True):
        st.switch_page("pages/5_🎯_Policy_Simulator.py")

with col2:
    if st.button("📈 View Past Forecasts", use_container_width=True):
        st.switch_page("pages/4_📈_Forecast_Eval.py")

with col3:
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/6_📄_Report_Generator.py")
