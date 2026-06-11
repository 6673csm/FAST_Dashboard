"""
Utility functions for FAST Dashboard
"""

import streamlit as st
import plotly.graph_objects as go


def inject_custom_css():
    """Inject custom CSS for modern "Cyber-Healthcare" styling."""
    st.markdown("""
    <style>
        /* Main container */
        .main {
            background-color: #121212 !important;
            padding: 2rem;
        }
        
        /* Modern Glassmorphism for Cards and Metrics */
        [data-testid="stMetric"], .card, [data-testid="stExpander"], div[data-testid="stVerticalBlock"] > div[style*="border"] {
            background: rgba(30, 30, 30, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* Metric text colors */
        .stMetric label {
            color: #40C4FF !important; /* Electric Blue */
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #121212 0%, #1e1e1e 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Headers */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important;
            font-weight: 800;
            background: linear-gradient(90deg, #FFFFFF, #40C4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #40C4FF 0%, #7C4DFF 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2.5rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 4px 15px rgba(64, 196, 255, 0.3);
        }
        
        .stButton>button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(124, 77, 255, 0.5);
            color: white !important;
        }

        /* Input fields */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_plotly_theme(fig: go.Figure) -> go.Figure:
    """
    Apply custom "Cyber-Healthcare" theme to Plotly figures.
    """
    fig.update_layout(
        font=dict(family='Inter, sans-serif', size=13, color='#FFFFFF'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=40, t=80, b=60),
        title_font=dict(size=20, color='#FFFFFF', family='Inter', weight=700),
        colorway=['#40C4FF', '#7C4DFF', '#00E676', '#FF5252', '#FFD740'], # Blue, Purple, Green, Red, Amber
        hoverlabel=dict(
            bgcolor="#1E1E1E",
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="#FFFFFF",
            bordercolor="#40C4FF"
        ),
        legend=dict(
            bgcolor="rgba(30, 30, 30, 0.8)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(size=12, color='#FFFFFF')
        )
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.05)',
        showline=True,
        linewidth=1,
        linecolor='rgba(255, 255, 255, 0.2)',
        title_font=dict(size=14, color='#40C4FF', family='Inter', weight=600),
        tickfont=dict(size=12, color='#AAAAAA')
    )
    
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.05)',
        showline=True,
        linewidth=1,
        linecolor='rgba(255, 255, 255, 0.2)',
        title_font=dict(size=14, color='#40C4FF', family='Inter', weight=600),
        tickfont=dict(size=12, color='#AAAAAA')
    )
    
    return fig


def format_metric(value: float, decimals: int = 2) -> str:
    """
    Format metric for display.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{value:,.{decimals}f}"


def create_info_card(title: str, content: str, icon: str = "ℹ️"):
    """
    Create an info card with custom styling.
    
    Args:
        title: Card title
        content: Card content
        icon: Emoji icon
    """
    st.markdown(f"""
    <div class="card">
        <h3>{icon} {title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def show_loading_animation(message: str = "Processing..."):
    """Show loading animation."""
    return st.spinner(message)


def display_metric_cards(metrics: dict):
    """
    Display metrics in a grid layout.
    
    Args:
        metrics: Dictionary of {label: (value, delta)}
    """
    cols = st.columns(len(metrics))
    
    for col, (label, data) in zip(cols, metrics.items()):
        value, delta = data if isinstance(data, tuple) else (data, None)
        
        with col:
            if delta is not None:
                st.metric(label, value, delta)
            else:
                st.metric(label, value)


def create_download_button(data, filename: str, label: str = "Download"):
    """
    Create a download button for data.
    
    Args:
        data: Data to download (string or bytes)
        filename: Name of file
        label: Button label
    """
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime='text/csv' if filename.endswith('.csv') else 'application/octet-stream'
    )


def show_success(message: str):
    """Show success message."""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message."""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """Show warning message."""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Show info message."""
    st.info(f"ℹ️ {message}")
