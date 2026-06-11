"""
Policy Simulator Page - FAST Dashboard
"What-If" scenario testing for policy interventions
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.simulator import (
    simulate_intervention,
    plot_simulation_comparison,
    generate_intervention_report,
    create_intervention_scenarios
)
from utils.helpers import inject_custom_css, show_success, show_error, show_warning, show_info

st.set_page_config(
    page_title="Policy Simulator - FAST",
    page_icon="🎯",
    layout="wide"
)

inject_custom_css()

st.title("🎯 Policy Simulator")
st.markdown("Test 'What-If' intervention scenarios to predict policy impact")

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
X_test = st.session_state.X_test
y_test = st.session_state.y_test
df = st.session_state.df

st.markdown(f"""
### 🎯 Current Configuration

- **Target Variable**: {current_target.upper().replace('-', ' ').title()}
- **Model Used**: {best_model_name}
- **Test Period**: {len(y_test)} time points
""")

st.markdown("---")

# Intervention controls
st.markdown("### 🎛️ Intervention Controls")

st.markdown("""
Adjust the sliders below to simulate the impact of policy interventions on mental health signals.
**Negative values** represent reductions (e.g., -20% means reducing the signal by 20%).
""")

# Scenario presets
st.markdown("#### 📋 Quick Scenarios")

scenarios = create_intervention_scenarios()
scenario_names = list(scenarios.keys())

selected_scenario = st.selectbox(
    "Choose a preset scenario (or create custom below)",
    ["Custom"] + scenario_names
)

# Initialize interventions
if selected_scenario != "Custom":
    preset_interventions = scenarios[selected_scenario]
else:
    preset_interventions = {'me-fea': 0, 'me-ang': 0, 'me-sad': 0}

# Custom intervention sliders
st.markdown("#### 🎚️ Custom Intervention Settings")

col1, col2, col3 = st.columns(3)

with col1:
    fear_change = st.slider(
        "😨 Fear Signal Change (%)",
        min_value=-50,
        max_value=50,
        value=int(preset_interventions.get('me-fea', 0)),
        step=5,
        help="Negative values reduce fear, positive values increase it"
    )

with col2:
    anger_change = st.slider(
        "😠 Anger Signal Change (%)",
        min_value=-50,
        max_value=50,
        value=int(preset_interventions.get('me-ang', 0)),
        step=5,
        help="Negative values reduce anger, positive values increase it"
    )

with col3:
    sadness_change = st.slider(
        "😢 Sadness Signal Change (%)",
        min_value=-50,
        max_value=50,
        value=int(preset_interventions.get('me-sad', 0)),
        step=5,
        help="Negative values reduce sadness, positive values increase it"
    )

# Compile interventions
interventions = {
    'me-fea': fear_change,
    'me-ang': anger_change,
    'me-sad': sadness_change
}

st.markdown("---")

# Run simulation button
if st.button("🔮 Run Simulation", type="primary", use_container_width=True):
    
    with st.spinner("Running simulation..."):
        # Run simulation
        baseline_pred, simulated_pred, impact_metrics = simulate_intervention(
            model,
            best_model_name,
            X_test,
            y_test,
            interventions
        )
        
        # Store results
        st.session_state.simulation_results = {
            'baseline_pred': baseline_pred,
            'simulated_pred': simulated_pred,
            'impact_metrics': impact_metrics,
            'interventions': interventions
        }
    
    show_success("Simulation complete!")

# Display results if available
if 'simulation_results' in st.session_state:
    results = st.session_state.simulation_results
    baseline_pred = results['baseline_pred']
    simulated_pred = results['simulated_pred']
    impact_metrics = results['impact_metrics']
    
    st.markdown("---")
    st.markdown("### 📊 Simulation Results")
    
    # Impact metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Baseline Average",
            f"{impact_metrics['avg_baseline']:.2f}"
        )
    
    with col2:
        st.metric(
            "Simulated Average",
            f"{impact_metrics['avg_simulated']:.2f}",
            delta=f"{impact_metrics['avg_change']:.2f}"
        )
    
    with col3:
        delta_color = "inverse" if impact_metrics['direction'] == 'reduction' else "normal"
        st.metric(
            "Percentage Change",
            f"{abs(impact_metrics['pct_change']):.1f}%",
            delta=impact_metrics['direction'].title(),
            delta_color=delta_color
        )
    
    with col4:
        st.metric(
            "Total Impact",
            f"{impact_metrics['total_impact']:.2f}",
            delta=f"{impact_metrics['cases_impact']:.0f} cases"
        )
    
    # Impact interpretation
    if impact_metrics['direction'] == 'reduction':
        show_success(f"✅ This intervention could reduce {current_target} by {abs(impact_metrics['pct_change']):.1f}%!")
    else:
        show_warning(f"⚠️ Warning: This intervention may increase {current_target} by {abs(impact_metrics['pct_change']):.1f}%")
    
    st.markdown("---")
    
    # Visualization
    st.markdown("### 📈 Baseline vs. Intervention Forecast")
    
    # Get dates
    if 'date' in df.columns:
        df_reset = df.reset_index()
        all_dates = df_reset['date']
        split_idx = len(st.session_state.y_train)
        test_dates = all_dates[split_idx:split_idx + len(y_test)]
    else:
        test_dates = pd.Series(range(len(y_test)))
    
    fig = plot_simulation_comparison(
        test_dates,
        baseline_pred,
        simulated_pred,
        y_test,
        title=f"Policy Impact Simulation - {current_target.upper()}"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed report
    st.markdown("### 📄 Impact Report")
    
    report = generate_intervention_report(
        interventions,
        impact_metrics,
        current_target.replace('-', ' ').title()
    )
    
    st.markdown(report)
    
    st.markdown("---")
    
    # Comparison table
    st.markdown("### 📋 Detailed Comparison")
    
    comparison_df = pd.DataFrame({
        'Date': test_dates.values if 'date' in df.columns else range(len(y_test)),
        'Actual': y_test.values,
        'Baseline Forecast': baseline_pred,
        'With Intervention': simulated_pred,
        'Impact': simulated_pred - baseline_pred,
        'Impact %': ((simulated_pred - baseline_pred) / baseline_pred * 100)
    })
    
    st.dataframe(
        comparison_df.style.background_gradient(
            subset=['Impact %'],
            cmap='RdYlGn_r'
        ),
        use_container_width=True,
        height=400
    )
    
    # Download results
    csv = comparison_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Simulation Results",
        data=csv,
        file_name=f"simulation_{current_target}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Policy recommendations
    st.markdown("### 💡 Policy Recommendations")
    
    if impact_metrics['direction'] == 'reduction':
        if abs(impact_metrics['pct_change']) > 15:
            st.markdown("""
            #### ✅ High Impact Intervention
            
            This simulation shows **significant potential** for reducing harm:
            
            1. **Pilot Program**: Consider implementing a pilot program in select regions
            2. **Monitoring**: Establish real-time monitoring systems to track actual impact
            3. **Scaling**: If successful, scale gradually to national level
            4. **Evaluation**: Conduct rigorous evaluation to validate predictions
            """)
        elif abs(impact_metrics['pct_change']) > 5:
            st.markdown("""
            #### ✅ Moderate Impact Intervention
            
            This simulation shows **moderate potential** for reducing harm:
            
            1. **Cost-Benefit Analysis**: Evaluate if the expected reduction justifies the cost
            2. **Complementary Measures**: Consider combining with other interventions
            3. **Targeted Approach**: Focus on high-risk populations or regions
            """)
        else:
            st.markdown("""
            #### ⚠️ Low Impact Intervention
            
            This simulation shows **limited potential** for reducing harm:
            
            1. **Reconsider Approach**: Explore alternative intervention strategies
            2. **Increase Intensity**: Consider more aggressive parameter changes
            3. **Multi-Factor Approach**: Combine multiple interventions for greater impact
            """)
    else:
        st.markdown("""
        #### ❌ Counterproductive Intervention
        
        **Warning**: This simulation suggests the intervention may **increase harm**:
        
        1. **Do Not Implement**: Avoid this intervention strategy
        2. **Reverse Direction**: Consider interventions that move in the opposite direction
        3. **Root Cause Analysis**: Investigate why this approach may be harmful
        4. **Alternative Strategies**: Explore fundamentally different approaches
        """)

else:
    st.info("👆 Adjust the intervention sliders above and click 'Run Simulation' to see the predicted impact!")
    
    st.markdown("""
    ### 🎯 How It Works
    
    The Policy Simulator allows you to test "What-If" scenarios:
    
    1. **Adjust Sliders**: Change mental health signals by percentage
    2. **Run Simulation**: The best-performing model predicts the impact
    3. **View Results**: See how the intervention affects predicted rates
    4. **Make Decisions**: Use insights to inform policy choices
    
    ### 📋 Example Scenarios
    
    - **Mental Health Awareness Campaign**: Reduce fear (-15%), sadness (-10%), anger (-5%)
    - **Fear Reduction Program**: Focus on reducing fear (-25%)
    - **Comprehensive Support**: Reduce all signals significantly
    - **Worst Case**: Test what happens if signals increase
    
    ### ⚠️ Important Notes
    
    - Predictions are based on historical patterns and may not capture all real-world complexities
    - Use simulations as **decision support**, not definitive predictions
    - Always validate with pilot programs and real-world monitoring
    - Consider ethical implications and unintended consequences
    """)

st.markdown("---")

# Next steps
st.markdown("### ⏭️ Next Steps")

col1, col2 = st.columns(2)

with col1:
    if st.button("📈 View Forecasts", use_container_width=True):
        st.switch_page("pages/4_📈_Forecast_Eval.py")

with col2:
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/6_📄_Report_Generator.py")
