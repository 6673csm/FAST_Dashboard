"""
SHAP Explainer Module for FAST Dashboard
Advanced model explainability using SHAP values
"""

import pandas as pd
import numpy as np
import shap
import plotly.graph_objects as go
from typing import Dict, Optional, Tuple
import streamlit as st


def compute_shap_values(
    model,
    model_name: str,
    X_data: pd.DataFrame,
    max_samples: int = 100
) -> Tuple[Optional[shap.Explanation], Optional[object]]:
    """
    Compute SHAP values for model predictions.
    
    Args:
        model: Trained model
        model_name: Name of the model
        X_data: Feature data
        max_samples: Maximum samples for background dataset
        
    Returns:
        Tuple of (SHAP values, explainer object)
    """
    try:
        # ARIMA doesn't support SHAP
        if model_name == 'ARIMA':
            return None, None
        
        # Limit data size for performance
        if len(X_data) > max_samples:
            background_data = X_data.sample(n=max_samples, random_state=42)
        else:
            background_data = X_data
        
        # Choose appropriate explainer
        if model_name in ['Random Forest', 'XGBoost']:
            # Tree-based models use TreeExplainer (fast)
            explainer = shap.TreeExplainer(model)
            shap_values = explainer(X_data)
        else:
            # Other models use KernelExplainer (slower)
            explainer = shap.KernelExplainer(
                model.predict,
                background_data,
                link="identity"
            )
            shap_values = explainer.shap_values(X_data)
            
            # Convert to Explanation object for consistency
            shap_values = shap.Explanation(
                values=shap_values,
                base_values=explainer.expected_value,
                data=X_data.values,
                feature_names=X_data.columns.tolist()
            )
        
        return shap_values, explainer
        
    except Exception as e:
        st.error(f"Error computing SHAP values: {str(e)}")
        return None, None


def plot_shap_summary(
    shap_values: shap.Explanation,
    title: str = "SHAP Feature Importance Summary"
) -> go.Figure:
    """
    Create SHAP summary plot (beeswarm) as Plotly figure.
    
    Args:
        shap_values: SHAP explanation object
        title: Chart title
        
    Returns:
        Plotly figure
    """
    try:
        # Get feature importance (mean absolute SHAP values)
        feature_importance = np.abs(shap_values.values).mean(axis=0)
        feature_names = shap_values.feature_names
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': feature_importance
        }).sort_values('Importance', ascending=True)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=importance_df['Importance'],
            y=importance_df['Feature'],
            orientation='h',
            marker=dict(
                color=importance_df['Importance'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Mean |SHAP|")
            ),
            text=[f"{val:.3f}" for val in importance_df['Importance']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, color='#1a1a1a', weight=700)),
            xaxis_title="Mean |SHAP Value|",
            yaxis_title="Feature",
            font=dict(family='Inter, sans-serif', size=13, color='#1a1a1a'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=max(400, len(importance_df) * 30),
            margin=dict(l=200, r=40, t=80, b=60),
            showlegend=False
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridcolor='#e0e0e0',
            showline=True,
            linewidth=2,
            linecolor='#666',
            tickfont=dict(size=12, color='#1a1a1a')
        )
        
        fig.update_yaxes(
            showline=True,
            linewidth=2,
            linecolor='#666',
            tickfont=dict(size=12, color='#1a1a1a')
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating SHAP summary plot: {str(e)}")
        return go.Figure()


def plot_shap_waterfall(
    shap_values: shap.Explanation,
    sample_idx: int = 0,
    title: str = "SHAP Waterfall Plot"
) -> go.Figure:
    """
    Create SHAP waterfall plot for individual prediction.
    
    Args:
        shap_values: SHAP explanation object
        sample_idx: Index of sample to explain
        title: Chart title
        
    Returns:
        Plotly figure
    """
    try:
        # Get SHAP values for single prediction
        single_shap = shap_values[sample_idx]
        
        # Get feature contributions
        feature_names = single_shap.feature_names
        shap_vals = single_shap.values
        base_value = single_shap.base_values
        
        # Sort by absolute SHAP value
        indices = np.argsort(np.abs(shap_vals))[::-1][:15]  # Top 15
        
        sorted_features = [feature_names[i] for i in indices]
        sorted_values = [shap_vals[i] for i in indices]
        
        # Calculate cumulative sum
        cumsum = np.cumsum([base_value] + sorted_values)
        
        # Create waterfall chart
        fig = go.Figure()
        
        # Add bars
        colors = ['red' if v < 0 else 'green' for v in sorted_values]
        
        fig.add_trace(go.Waterfall(
            name="SHAP",
            orientation="h",
            y=sorted_features,
            x=sorted_values,
            connector={"line": {"color": "#666", "width": 1}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#667eea"}}
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, color='#1a1a1a', weight=700)),
            xaxis_title="SHAP Value (Impact on Prediction)",
            yaxis_title="Feature",
            font=dict(family='Inter, sans-serif', size=13, color='#1a1a1a'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=max(500, len(sorted_features) * 35),
            margin=dict(l=200, r=40, t=80, b=60),
            showlegend=False
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridcolor='#e0e0e0',
            showline=True,
            linewidth=2,
            linecolor='#666',
            tickfont=dict(size=12, color='#1a1a1a'),
            zeroline=True,
            zerolinecolor='#666',
            zerolinewidth=2
        )
        
        fig.update_yaxes(
            showline=True,
            linewidth=2,
            linecolor='#666',
            tickfont=dict(size=12, color='#1a1a1a')
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating waterfall plot: {str(e)}")
        return go.Figure()


def get_shap_feature_importance(shap_values: shap.Explanation) -> pd.DataFrame:
    """
    Extract feature importance from SHAP values.
    
    Args:
        shap_values: SHAP explanation object
        
    Returns:
        DataFrame with feature importance
    """
    try:
        # Calculate mean absolute SHAP value for each feature
        importance = np.abs(shap_values.values).mean(axis=0)
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'Feature': shap_values.feature_names,
            'Importance': importance
        }).sort_values('Importance', ascending=False)
        
        # Normalize to percentage
        importance_df['Importance %'] = (
            importance_df['Importance'] / importance_df['Importance'].sum() * 100
        )
        
        return importance_df
        
    except Exception as e:
        st.error(f"Error extracting SHAP importance: {str(e)}")
        return pd.DataFrame()


def explain_prediction_shap(
    shap_values: shap.Explanation,
    sample_idx: int,
    prediction_value: float,
    target_name: str = "gh-death"
) -> str:
    """
    Generate natural language explanation using SHAP values.
    
    Args:
        shap_values: SHAP explanation object
        sample_idx: Index of sample to explain
        prediction_value: Predicted value
        target_name: Name of target variable
        
    Returns:
        Explanation text in markdown
    """
    try:
        # Get SHAP values for single prediction
        single_shap = shap_values[sample_idx]
        
        feature_names = single_shap.feature_names
        shap_vals = single_shap.values
        feature_values = single_shap.data
        base_value = single_shap.base_values
        
        # Get top positive and negative contributors
        pos_indices = np.where(shap_vals > 0)[0]
        neg_indices = np.where(shap_vals < 0)[0]
        
        pos_sorted = sorted(pos_indices, key=lambda i: shap_vals[i], reverse=True)[:3]
        neg_sorted = sorted(neg_indices, key=lambda i: shap_vals[i])[:3]
        
        explanation = f"""
### 🔍 SHAP Explanation for Prediction

**Predicted {target_name}:** {prediction_value:.2f}

**Base Value (Average Prediction):** {base_value:.2f}

---

#### 📈 Top Factors Increasing Risk:
"""
        
        if len(pos_sorted) > 0:
            for rank, idx in enumerate(pos_sorted, 1):
                feat_name = feature_names[idx]
                feat_val = feature_values[idx]
                shap_val = shap_vals[idx]
                explanation += f"\n{rank}. **{feat_name}** = {feat_val:.2f} → +{shap_val:.3f} impact"
        else:
            explanation += "\n*No factors significantly increasing risk*"
        
        explanation += "\n\n#### 📉 Top Factors Decreasing Risk:\n"
        
        if len(neg_sorted) > 0:
            for rank, idx in enumerate(neg_sorted, 1):
                feat_name = feature_names[idx]
                feat_val = feature_values[idx]
                shap_val = shap_vals[idx]
                explanation += f"\n{rank}. **{feat_name}** = {feat_val:.2f} → {shap_val:.3f} impact"
        else:
            explanation += "\n*No factors significantly decreasing risk*"
        
        # Add interpretation
        if len(pos_sorted) > 0:
            top_feature = feature_names[pos_sorted[0]]
            explanation += f"\n\n---\n\n**Key Insight:** The feature **{top_feature}** has the strongest positive impact on this prediction. "
            explanation += "Interventions targeting this factor could be most effective in reducing risk."
        
        return explanation
        
    except Exception as e:
        return f"Error generating explanation: {str(e)}"
