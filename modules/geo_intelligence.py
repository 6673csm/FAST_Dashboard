"""
Geographic Intelligence Module for FAST Dashboard
Regional analysis, risk heatmaps, and location-based insights
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Optional
import json


# India states GeoJSON (simplified coordinates)
INDIA_STATES_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Maharashtra"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[72.6, 15.6], [80.0, 15.6], [80.0, 22.0], [72.6, 22.0], [72.6, 15.6]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Delhi"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[76.8, 28.4], [77.3, 28.4], [77.3, 28.9], [76.8, 28.9], [76.8, 28.4]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Karnataka"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.0, 11.5], [78.5, 11.5], [78.5, 18.5], [74.0, 18.5], [74.0, 11.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Tamil Nadu"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[76.2, 8.0], [80.3, 8.0], [80.3, 13.5], [76.2, 13.5], [76.2, 8.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Uttar Pradesh"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[77.0, 23.8], [84.6, 23.8], [84.6, 30.4], [77.0, 30.4], [77.0, 23.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "West Bengal"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[85.8, 21.5], [89.8, 21.5], [89.8, 27.2], [85.8, 27.2], [85.8, 21.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Gujarat"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[68.1, 20.1], [74.5, 20.1], [74.5, 24.7], [68.1, 24.7], [68.1, 20.1]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Rajasthan"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[69.5, 23.0], [78.2, 23.0], [78.2, 30.2], [69.5, 30.2], [69.5, 23.0]]]
            }
        }
    ]
}


def calculate_regional_risk(
    df: pd.DataFrame,
    target_col: str = 'GH-Death',
    region_col: str = 'region'
) -> pd.DataFrame:
    """
    Calculate risk metrics by region.
    
    Args:
        df: DataFrame with regional data
        target_col: Target variable column name
        region_col: Region column name
        
    Returns:
        DataFrame with regional risk metrics
    """
    regional_stats = df.groupby(region_col).agg({
        target_col: ['mean', 'std', 'max', 'min'],
        'population': 'first'  # Assuming population is constant per region
    }).reset_index()
    
    # Flatten column names
    regional_stats.columns = ['region', 'avg_risk', 'std_risk', 'max_risk', 'min_risk', 'population']
    
    # Calculate per-capita risk (per 100k)
    regional_stats['risk_per_100k'] = (regional_stats['avg_risk'] / regional_stats['population']) * 100000
    
    # Calculate risk score (normalized 0-100)
    max_risk = regional_stats['avg_risk'].max()
    regional_stats['risk_score'] = (regional_stats['avg_risk'] / max_risk * 100) if max_risk > 0 else 0
    
    # Risk category
    regional_stats['risk_category'] = pd.cut(
        regional_stats['risk_score'],
        bins=[0, 33, 66, 100],
        labels=['Low', 'Medium', 'High']
    )
    
    return regional_stats


def create_india_choropleth(
    regional_data: pd.DataFrame,
    value_column: str = 'risk_score',
    title: str = "Risk Heatmap - India"
) -> go.Figure:
    """
    Create an India choropleth map showing regional risk.
    
    Args:
        regional_data: DataFrame with regional statistics
        value_column: Column to visualize
        title: Map title
        
    Returns:
        Plotly figure
    """
    # Create choropleth using scatter_geo for simplicity
    # (Full GeoJSON rendering would require actual India boundary data)
    
    # State center coordinates
    state_coords = {
        'Maharashtra': (19.7515, 75.7139),
        'Delhi': (28.7041, 77.1025),
        'Karnataka': (15.3173, 75.7139),
        'Tamil Nadu': (11.1271, 78.6569),
        'Uttar Pradesh': (26.8467, 80.9462),
        'West Bengal': (22.9868, 87.8550),
        'Gujarat': (22.2587, 71.1924),
        'Rajasthan': (27.0238, 74.2179)
    }
    
    # Add coordinates to data
    regional_data = regional_data.copy()
    regional_data['lat'] = regional_data['region'].map(lambda x: state_coords.get(x, (0, 0))[0])
    regional_data['lon'] = regional_data['region'].map(lambda x: state_coords.get(x, (0, 0))[1])
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter points for states
    fig.add_trace(go.Scattergeo(
        lon=regional_data['lon'],
        lat=regional_data['lat'],
        text=regional_data['region'],
        mode='markers+text',
        marker=dict(
            size=regional_data[value_column] / 2,
            color=regional_data[value_column],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title=value_column.replace('_', ' ').title()),
            line=dict(width=1, color='white')
        ),
        textposition='top center',
        textfont=dict(size=10, color='#1a1a1a', family='Inter, sans-serif'),
        hovertemplate='<b>%{text}</b><br>' +
                      f'{value_column.replace("_", " ").title()}: ' + '%{marker.color:.1f}<br>' +
                      '<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#1a1a1a', family='Inter, sans-serif')),
        geo=dict(
            scope='asia',
            center=dict(lat=20.5937, lon=78.9629),  # India center
            projection_scale=4,
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showlakes=True,
            lakecolor='rgb(200, 230, 255)',
            showcountries=True,
            countrycolor='rgb(204, 204, 204)',
        ),
        height=600,
        font=dict(family='Inter, sans-serif', size=12, color='#1a1a1a'),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def create_regional_comparison(
    regional_data: pd.DataFrame,
    metric: str = 'avg_risk'
) -> go.Figure:
    """
    Create bar chart comparing regions.
    
    Args:
        regional_data: DataFrame with regional statistics
        metric: Metric to compare
        
    Returns:
        Plotly figure
    """
    # Sort by metric
    data_sorted = regional_data.sort_values(metric, ascending=False)
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data_sorted['region'],
        y=data_sorted[metric],
        marker=dict(
            color=data_sorted[metric],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title=metric.replace('_', ' ').title())
        ),
        text=[f"{val:.2f}" for val in data_sorted[metric]],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                      f'{metric.replace("_", " ").title()}: ' + '%{y:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Regional Comparison - {metric.replace('_', ' ').title()}",
            font=dict(size=18, color='#1a1a1a', family='Inter, sans-serif')
        ),
        xaxis_title="Region",
        yaxis_title=metric.replace('_', ' ').title(),
        font=dict(family='Inter, sans-serif', size=13, color='#1a1a1a'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    
    return fig


def generate_regional_alerts(
    regional_data: pd.DataFrame,
    threshold_high: float = 75.0,
    threshold_medium: float = 50.0
) -> List[Dict]:
    """
    Generate alerts for high-risk regions.
    
    Args:
        regional_data: DataFrame with regional statistics
        threshold_high: High risk threshold
        threshold_medium: Medium risk threshold
        
    Returns:
        List of alert dictionaries
    """
    alerts = []
    
    for _, row in regional_data.iterrows():
        risk_score = row['risk_score']
        region = row['region']
        
        if risk_score >= threshold_high:
            alerts.append({
                'region': region,
                'severity': 'HIGH',
                'risk_score': risk_score,
                'message': f"⚠️ HIGH RISK: {region} shows elevated risk levels ({risk_score:.1f}/100). Immediate intervention recommended.",
                'color': '#dc3545'
            })
        elif risk_score >= threshold_medium:
            alerts.append({
                'region': region,
                'severity': 'MEDIUM',
                'risk_score': risk_score,
                'message': f"⚡ MEDIUM RISK: {region} requires monitoring ({risk_score:.1f}/100). Consider preventive measures.",
                'color': '#ffc107'
            })
    
    # Sort by risk score descending
    alerts.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return alerts


def create_trend_by_region(
    df: pd.DataFrame,
    target_col: str = 'GH-Death',
    date_col: str = 'date',
    region_col: str = 'region'
) -> go.Figure:
    """
    Create time series plot showing trends by region.
    
    Args:
        df: DataFrame with time series data
        target_col: Target variable
        date_col: Date column
        region_col: Region column
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Get unique regions
    regions = df[region_col].unique()
    
    # Color palette
    colors = px.colors.qualitative.Set2
    
    for idx, region in enumerate(regions):
        region_data = df[df[region_col] == region].sort_values(date_col)
        
        fig.add_trace(go.Scatter(
            x=region_data[date_col],
            y=region_data[target_col],
            mode='lines',
            name=region,
            line=dict(width=2, color=colors[idx % len(colors)]),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'Date: %{x}<br>' +
                          f'{target_col}: ' + '%{y:.2f}<br>' +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=f"{target_col} Trends by Region",
            font=dict(size=18, color='#1a1a1a', family='Inter, sans-serif')
        ),
        xaxis_title="Date",
        yaxis_title=target_col,
        font=dict(family='Inter, sans-serif', size=13, color='#1a1a1a'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='right',
            x=1.15
        )
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e9ecef')
    
    return fig
