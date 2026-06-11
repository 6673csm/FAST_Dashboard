"""
Simulator Module for FAST Dashboard
Policy "What-If" scenario simulation
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Tuple


def simulate_intervention(
    model,
    model_name: str,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    interventions: Dict[str, float]
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Simulate the impact of policy interventions.
    
    Args:
        model: Trained model
        model_name: Name of the model
        X_test: Test features
        y_test: Test target (for baseline)
        interventions: Dictionary of {feature_name: percentage_change}
                      e.g., {'me-fea': -20} means reduce fear by 20%
        
    Returns:
        Tuple of (baseline_predictions, simulated_predictions, impact_metrics)
    """
    # Get baseline predictions
    if model_name == 'ARIMA':
        baseline_pred = model.forecast(steps=len(X_test))
    else:
        baseline_pred = model.predict(X_test)
    
    # Create modified features
    X_simulated = X_test.copy()
    
    for feature, pct_change in interventions.items():
        if feature in X_simulated.columns:
            # Apply percentage change
            X_simulated[feature] = X_simulated[feature] * (1 + pct_change / 100)
            
            # Clip to valid ranges (0-1 for mental signals)
            if any(signal in feature.lower() for signal in ['me-fea', 'me-ang', 'me-sad']):
                X_simulated[feature] = X_simulated[feature].clip(0, 1)
    
    # Get simulated predictions
    if model_name == 'ARIMA':
        # ARIMA can't use modified features, use baseline
        simulated_pred = baseline_pred
    else:
        simulated_pred = model.predict(X_simulated)
    
    # Calculate impact metrics
    impact_metrics = calculate_impact_metrics(baseline_pred, simulated_pred, y_test)
    
    return baseline_pred, simulated_pred, impact_metrics


def calculate_impact_metrics(
    baseline_pred: np.ndarray,
    simulated_pred: np.ndarray,
    y_actual: pd.Series
) -> Dict:
    """
    Calculate impact metrics for simulation.
    
    Args:
        baseline_pred: Baseline predictions
        simulated_pred: Simulated predictions
        y_actual: Actual values
        
    Returns:
        Dictionary of impact metrics
    """
    # Average change
    avg_baseline = np.mean(baseline_pred)
    avg_simulated = np.mean(simulated_pred)
    avg_change = avg_simulated - avg_baseline
    pct_change = (avg_change / avg_baseline) * 100 if avg_baseline != 0 else 0
    
    # Total impact (sum of differences)
    total_impact = np.sum(simulated_pred - baseline_pred)
    
    # Cases prevented/increased
    cases_impact = total_impact
    
    # Direction
    direction = "reduction" if avg_change < 0 else "increase"
    
    return {
        'avg_baseline': round(avg_baseline, 2),
        'avg_simulated': round(avg_simulated, 2),
        'avg_change': round(avg_change, 2),
        'pct_change': round(pct_change, 2),
        'total_impact': round(total_impact, 2),
        'cases_impact': round(cases_impact, 2),
        'direction': direction
    }


def plot_simulation_comparison(
    dates: pd.Series,
    baseline_pred: np.ndarray,
    simulated_pred: np.ndarray,
    y_actual: pd.Series = None,
    title: str = "Policy Intervention Simulation"
) -> go.Figure:
    """
    Create comparison plot for simulation results.
    
    Args:
        dates: Date series for x-axis
        baseline_pred: Baseline predictions
        simulated_pred: Simulated predictions
        y_actual: Actual values (optional)
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Actual values (if provided)
    if y_actual is not None:
        fig.add_trace(go.Scatter(
            x=dates,
            y=y_actual,
            mode='lines',
            name='Actual',
            line=dict(color='#6c757d', width=2),
            opacity=0.6
        ))
    
    # Baseline forecast
    fig.add_trace(go.Scatter(
        x=dates,
        y=baseline_pred,
        mode='lines+markers',
        name='Baseline (No Intervention)',
        line=dict(color='#dc3545', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    # Simulated forecast
    fig.add_trace(go.Scatter(
        x=dates,
        y=simulated_pred,
        mode='lines+markers',
        name='With Intervention',
        line=dict(color='#28a745', width=3),
        marker=dict(size=6)
    ))
    
    # Fill area between baseline and simulated
    fig.add_trace(go.Scatter(
        x=dates.tolist() + dates.tolist()[::-1],
        y=baseline_pred.tolist() + simulated_pred.tolist()[::-1],
        fill='toself',
        fillcolor='rgba(40, 167, 69, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Predicted Rate',
        hovermode='x unified',
        font=dict(family='Inter, sans-serif', size=12),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    
    return fig


def generate_intervention_report(
    interventions: Dict[str, float],
    impact_metrics: Dict,
    target_name: str
) -> str:
    """
    Generate text report for intervention simulation.
    
    Args:
        interventions: Dictionary of interventions applied
        impact_metrics: Impact metrics from simulation
        target_name: Name of target variable
        
    Returns:
        Formatted report text
    """
    report = f"### 📊 Policy Intervention Impact Report\n\n"
    report += f"**Target:** {target_name}\n\n"
    
    # Interventions applied
    report += "**Interventions Applied:**\n"
    signal_names = {
        'me-fea': 'Fear Signal',
        'me-ang': 'Anger Signal',
        'me-sad': 'Sadness Signal'
    }
    
    for feature, pct_change in interventions.items():
        feature_display = signal_names.get(feature, feature)
        sign = '+' if pct_change > 0 else ''
        report += f"- {feature_display}: {sign}{pct_change}%\n"
    
    report += "\n**Predicted Impact:**\n\n"
    
    # Impact metrics
    direction_emoji = "📉" if impact_metrics['direction'] == 'reduction' else "📈"
    direction_color = "green" if impact_metrics['direction'] == 'reduction' else "red"
    
    report += f"{direction_emoji} **{abs(impact_metrics['pct_change']):.1f}% {impact_metrics['direction']}** "
    report += f"in predicted {target_name.lower()}\n\n"
    
    report += f"- **Baseline Average:** {impact_metrics['avg_baseline']:.2f}\n"
    report += f"- **Simulated Average:** {impact_metrics['avg_simulated']:.2f}\n"
    report += f"- **Change:** {impact_metrics['avg_change']:.2f}\n\n"
    
    # Interpretation
    if impact_metrics['direction'] == 'reduction':
        report += "✅ **Recommendation:** This intervention shows promise in reducing harm. "
        report += "Consider pilot implementation with careful monitoring.\n"
    else:
        report += "⚠️ **Warning:** This intervention may increase harm. "
        report += "Reconsider the approach or adjust parameters.\n"
    
    return report


def create_intervention_scenarios() -> Dict[str, Dict[str, float]]:
    """
    Create predefined intervention scenarios for quick testing.
    
    Returns:
        Dictionary of scenario names to intervention parameters
    """
    scenarios = {
        "Mental Health Awareness Campaign": {
            'me-fea': -15,
            'me-sad': -10,
            'me-ang': -5
        },
        "Fear Reduction Program": {
            'me-fea': -25,
            'me-sad': -5,
            'me-ang': 0
        },
        "Anger Management Initiative": {
            'me-fea': 0,
            'me-sad': 0,
            'me-ang': -20
        },
        "Comprehensive Support System": {
            'me-fea': -20,
            'me-sad': -20,
            'me-ang': -15
        },
        "Worst Case Scenario": {
            'me-fea': 20,
            'me-sad': 15,
            'me-ang': 25
        }
    }
    
    return scenarios
