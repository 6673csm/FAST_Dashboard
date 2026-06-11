"""
Forecast & Evaluation Page - FAST Dashboard
Interactive forecasting and model evaluation
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.evaluator import calculate_metrics, calculate_residuals
from utils.helpers import inject_custom_css, show_success, show_error, show_warning, show_info

st.set_page_config(
    page_title="Forecast & Evaluation - FAST",
    page_icon="📈",
    layout="wide"
)

inject_custom_css()

st.title("📈 Forecast & Evaluation")
st.markdown("Interactive predictions and performance analysis")

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

# Get data
X_train = st.session_state.X_train
X_test = st.session_state.X_test
y_train = st.session_state.y_train
y_test = st.session_state.y_test

# Model selection
st.markdown("### 🎯 Select Model")

available_models = [name.replace(f"_{current_target}", "") for name in engine.models.keys() if current_target in name]

selected_model = st.selectbox(
    "Choose model to evaluate",
    available_models,
    index=available_models.index(st.session_state.get('best_model_name', available_models[0])) if st.session_state.get('best_model_name') in available_models else 0
)

st.markdown("---")

# Get predictions
model = engine.models[f"{selected_model}_{current_target}"]

if selected_model == 'ARIMA':
    y_train_pred = model.fittedvalues
    y_test_pred = model.forecast(steps=len(y_test))
else:
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

# Calculate metrics
train_metrics = calculate_metrics(y_train, y_train_pred)
test_metrics = calculate_metrics(y_test, y_test_pred)

# Debug: Show actual metric values
with st.expander("🔍 Debug: View Raw Metric Values"):
    st.write("**Training Metrics:**", train_metrics)
    st.write("**Test Metrics:**", test_metrics)
    st.write(f"**Sample Predictions (first 5):**")
    st.write(f"- Actual: {y_test.values[:5]}")
    st.write(f"- Predicted: {y_test_pred[:5]}")

# Display metrics
st.markdown("### 📊 Performance Metrics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Training Set")
    
    # Use custom HTML instead of st.metric to avoid truncation
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">MAE</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{train_metrics['MAE']:.3f}</div>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">RMSE</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{train_metrics['RMSE']:.3f}</div>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">MAPE</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{train_metrics['MAPE']:.1f}%</div>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">R²</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{train_metrics['R²']:.3f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### Test Set")
    
    # Use custom HTML instead of st.metric to avoid truncation
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">MAE</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{test_metrics['MAE']:.3f}</div>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">RMSE</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{test_metrics['RMSE']:.3f}</div>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">MAPE</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{test_metrics['MAPE']:.1f}%</div>
        </div>
        <div style="background: white; padding: 15px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="color: #666; font-size: 12px; font-weight: 600; margin-bottom: 5px;">R²</div>
            <div style="color: #1a1a1a; font-size: 24px; font-weight: 700;">{test_metrics['R²']:.3f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Overfitting check
overfitting_score = train_metrics['R²'] - test_metrics['R²']

if overfitting_score > 0.1:
    show_warning(f"⚠️ Possible overfitting detected! Training R² is {overfitting_score:.2f} higher than test R²")
elif overfitting_score < -0.1:
    show_info("ℹ️ Model generalizes well to unseen data")
else:
    show_success("✅ Good balance between training and test performance")

st.markdown("---")

# Actual vs Predicted
st.markdown("### 📈 Actual vs. Predicted")

# View toggle
view_mode = st.radio(
    "Select view",
    ["Test Data (Forecast)", "Training Data", "Both"],
    horizontal=True
)

# Create figure
fig = go.Figure()

# Get dates
df = st.session_state.df
if 'date' in df.columns:
    df_reset = df.reset_index()
    all_dates = df_reset['date']
    
    # Split dates
    split_idx = len(y_train)
    train_dates = all_dates[:split_idx]
    test_dates = all_dates[split_idx:split_idx + len(y_test)]
else:
    train_dates = pd.Series(range(len(y_train)))
    test_dates = pd.Series(range(len(y_train), len(y_train) + len(y_test)))

# Plot based on view mode
if view_mode in ["Training Data", "Both"]:
    # Training actual
    fig.add_trace(go.Scatter(
        x=train_dates,
        y=y_train,
        mode='lines',
        name='Actual (Train)',
        line=dict(color='#6c757d', width=2),
        opacity=0.7
    ))
    
    # Training predicted
    fig.add_trace(go.Scatter(
        x=train_dates,
        y=y_train_pred,
        mode='lines',
        name=f'{selected_model} (Train)',
        line=dict(color='#007bff', width=2, dash='dot'),
        opacity=0.7
    ))

if view_mode in ["Test Data (Forecast)", "Both"]:
    # Test actual
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=y_test.values,
        mode='lines+markers',
        name='Actual (Test)',
        line=dict(color='#28a745', width=3),
        marker=dict(size=6)
    ))
    
    # Test predicted
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=y_test_pred,
        mode='lines+markers',
        name=f'{selected_model} (Test)',
        line=dict(color='#dc3545', width=3, dash='dash'),
        marker=dict(size=6, symbol='x')
    ))

fig.update_layout(
    title=f"Actual vs. Predicted - {selected_model}",
    xaxis_title='Date' if 'date' in df.columns else 'Time',
    yaxis_title=f'{current_target.upper()} Rate',
    hovermode='x unified',
    height=500,
    font=dict(family='Inter, sans-serif', size=12),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    )
)

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Residual Analysis
st.markdown("### 🔍 Residual Analysis")

st.markdown("""
Residuals show the prediction errors. A good model should have:
- Residuals randomly scattered around zero
- No clear patterns or trends
""")

# Calculate residuals
test_residuals = calculate_residuals(y_test, y_test_pred)

col1, col2 = st.columns(2)

with col1:
    # Residual plot
    fig_residual = px.scatter(
        x=y_test_pred,
        y=test_residuals,
        labels={'x': 'Predicted Values', 'y': 'Residuals'},
        title='Residual Plot',
        trendline='ols'
    )
    
    # Add zero line
    fig_residual.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    fig_residual.update_layout(
        height=400,
        font=dict(family='Inter, sans-serif', size=12),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig_residual, use_container_width=True)

with col2:
    # Residual distribution
    fig_hist = px.histogram(
        x=test_residuals,
        nbins=30,
        labels={'x': 'Residuals'},
        title='Residual Distribution'
    )
    
    fig_hist.update_layout(
        height=400,
        showlegend=False,
        font=dict(family='Inter, sans-serif', size=12),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)

# Residual statistics
st.markdown("#### Residual Statistics")

residual_stats = {
    "Mean": f"{np.mean(test_residuals):.4f}",
    "Std Dev": f"{np.std(test_residuals):.4f}",
    "Min": f"{np.min(test_residuals):.4f}",
    "Max": f"{np.max(test_residuals):.4f}"
}

cols = st.columns(4)
for col, (label, value) in zip(cols, residual_stats.items()):
    col.metric(label, value)

# Interpretation
mean_residual = np.mean(test_residuals)
if abs(mean_residual) < 0.1:
    show_success("✅ Residuals are well-centered around zero (unbiased predictions)")
else:
    show_warning(f"⚠️ Residuals have a mean of {mean_residual:.4f} (slight bias detected)")

st.markdown("---")

# Prediction table
st.markdown("### 📋 Detailed Predictions")

# Create comparison table
comparison_df = pd.DataFrame({
    'Date': test_dates.values if 'date' in df.columns else range(len(y_test)),
    'Actual': y_test.values,
    'Predicted': y_test_pred,
    'Error': test_residuals,
    'Error %': (np.abs(test_residuals) / y_test.values * 100)
})

st.dataframe(
    comparison_df.style.background_gradient(
        subset=['Error %'],
        cmap='RdYlGn_r'
    ),
    use_container_width=True,
    height=400
)

# Download predictions
csv = comparison_df.to_csv(index=False)
st.download_button(
    label="📥 Download Predictions",
    data=csv,
    file_name=f"predictions_{selected_model}_{current_target}.csv",
    mime="text/csv"
)

st.markdown("---")

# Next steps
st.markdown("### ⏭️ Next Steps")

col1, col2 = st.columns(2)

with col1:
    if st.button("🎯 Try Policy Simulator", use_container_width=True):
        st.switch_page("pages/5_🎯_Policy_Simulator.py")

with col2:
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/6_📄_Report_Generator.py")
