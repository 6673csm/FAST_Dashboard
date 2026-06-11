"""
Explainer Module for FAST Dashboard
Feature importance and explainable AI functionality
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional


def get_feature_importance(
    model,
    model_name: str,
    feature_names: list,
    top_n: int = 10
) -> Optional[pd.DataFrame]:
    """
    Extract feature importance from model.
    
    Args:
        model: Trained model
        model_name: Name of the model
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        DataFrame with feature importance or None
    """
    try:
        # Get importance based on model type
        if hasattr(model, 'feature_importances_'):
            # Tree-based models (RF, XGBoost)
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # Linear models (Bayesian Ridge, SVR with linear kernel)
            importance = np.abs(model.coef_)
        else:
            return None
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importance
        }).sort_values('Importance', ascending=False)
        
        # Normalize to 0-100 scale
        importance_df['Importance'] = (
            importance_df['Importance'] / importance_df['Importance'].sum() * 100
        )
        
        # Get top N
        importance_df = importance_df.head(top_n)
        
        return importance_df
        
    except Exception as e:
        print(f"Error extracting feature importance: {str(e)}")
        return None


def plot_feature_importance(
    importance_df: pd.DataFrame,
    title: str = "Feature Importance"
) -> go.Figure:
    """
    Create interactive bar chart for feature importance.
    
    Args:
        importance_df: DataFrame with Feature and Importance columns
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = px.bar(
        importance_df,
        x='Importance',
        y='Feature',
        orientation='h',
        title=title,
        color='Importance',
        color_continuous_scale='Viridis',
        labels={'Importance': 'Importance (%)', 'Feature': 'Feature Name'}
    )
    
    fig.update_layout(
        height=max(400, len(importance_df) * 40),
        showlegend=False,
        font=dict(family='Inter, sans-serif', size=13, color='#1a1a1a'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=200, r=40, t=80, b=60),
        title_font=dict(size=18, color='#1a1a1a', family='Inter', weight=700)
    )
    
    fig.update_xaxes(
        title_font=dict(size=14, color='#1a1a1a', family='Inter', weight=600),
        tickfont=dict(size=12, color='#1a1a1a'),
        showgrid=True,
        gridcolor='#e0e0e0',
        showline=True,
        linewidth=2,
        linecolor='#666'
    )
    
    fig.update_yaxes(
        title_font=dict(size=14, color='#1a1a1a', family='Inter', weight=600),
        tickfont=dict(size=12, color='#1a1a1a'),
        showline=True,
        linewidth=2,
        linecolor='#666'
    )
    
    fig.update_traces(
        texttemplate='%{x:.1f}%',
        textposition='outside',
        textfont=dict(size=12, color='#1a1a1a'),
        marker=dict(line=dict(width=1, color='white'))
    )
    
    return fig


def interpret_feature_importance(importance_df: pd.DataFrame, target_name: str) -> str:
    """
    Generate text interpretation of feature importance.
    
    Args:
        importance_df: DataFrame with feature importance
        target_name: Name of target variable
        
    Returns:
        Interpretation text
    """
    if importance_df is None or importance_df.empty:
        return "Feature importance not available for this model."
    
    top_feature = importance_df.iloc[0]
    top_3_features = importance_df.head(3)
    
    interpretation = f"""
    ### 🔍 Feature Importance Analysis for {target_name}
    
    **Top Contributing Factor:**
    - **{top_feature['Feature']}** contributes **{top_feature['Importance']:.1f}%** to predictions
    
    **Top 3 Predictive Features:**
    """
    
    for idx, row in top_3_features.iterrows():
        interpretation += f"\n{idx + 1}. **{row['Feature']}**: {row['Importance']:.1f}%"
    
    # Add interpretation based on feature names
    mental_signals = ['me-fea', 'me-ang', 'me-sad']
    top_signal = None
    
    for signal in mental_signals:
        if signal in top_feature['Feature'].lower():
            top_signal = signal
            break
    
    if top_signal:
        signal_names = {
            'me-fea': 'Fear',
            'me-ang': 'Anger',
            'me-sad': 'Sadness'
        }
        interpretation += f"\n\n**Key Insight:** {signal_names[top_signal]} signals are the strongest predictor of {target_name}. "
        interpretation += "Policy interventions targeting this emotion may have the greatest impact."
    
    return interpretation


def create_correlation_heatmap(df: pd.DataFrame, title: str = "Feature Correlation Matrix") -> go.Figure:
    """
    Create interactive correlation heatmap.
    
    Args:
        df: DataFrame with features
        title: Chart title
        
    Returns:
        Plotly figure
    """
    # Calculate correlation matrix
    corr_matrix = df.corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        title=title,
        labels=dict(color="Correlation"),
        aspect='auto'
    )
    
    fig.update_layout(
        font=dict(family='Inter, sans-serif', size=12, color='#1a1a1a'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600,
        margin=dict(l=60, r=40, t=80, b=60),
        title_font=dict(size=18, color='#1a1a1a', family='Inter', weight=700)
    )
    
    fig.update_xaxes(
        side='bottom',
        tickfont=dict(size=11, color='#1a1a1a')
    )
    
    fig.update_yaxes(
        tickfont=dict(size=11, color='#1a1a1a')
    )
    
    return fig


def identify_key_correlations(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """
    Identify strong correlations in the dataset.
    
    Args:
        df: DataFrame with features
        threshold: Minimum absolute correlation to report
        
    Returns:
        DataFrame with strong correlations
    """
    corr_matrix = df.corr()
    
    # Get upper triangle
    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) >= threshold:
                correlations.append({
                    'Feature 1': corr_matrix.columns[i],
                    'Feature 2': corr_matrix.columns[j],
                    'Correlation': round(corr_value, 3),
                    'Strength': 'Strong' if abs(corr_value) >= 0.7 else 'Moderate'
                })
    
    corr_df = pd.DataFrame(correlations)
    if not corr_df.empty:
        corr_df = corr_df.sort_values('Correlation', key=abs, ascending=False)
    
    return corr_df


def explain_prediction(
    model,
    model_name: str,
    X_sample: pd.DataFrame,
    feature_importance_df: pd.DataFrame
) -> str:
    """
    Explain a specific prediction.
    
    Args:
        model: Trained model
        model_name: Name of the model
        X_sample: Single sample to explain
        feature_importance_df: Feature importance DataFrame
        
    Returns:
        Explanation text
    """
    if model_name == 'ARIMA':
        return "ARIMA predictions are based on historical patterns and trends in the time series."
    
    prediction = model.predict(X_sample)[0]
    
    explanation = f"**Predicted Value:** {prediction:.2f}\n\n"
    explanation += "**Main Contributing Factors:**\n\n"
    
    if feature_importance_df is not None and not feature_importance_df.empty:
        top_features = feature_importance_df.head(5)
        
        for idx, row in top_features.iterrows():
            feature_name = row['Feature']
            if feature_name in X_sample.columns:
                feature_value = X_sample[feature_name].values[0]
                explanation += f"- **{feature_name}**: {feature_value:.3f} (Importance: {row['Importance']:.1f}%)\n"
    
    return explanation
