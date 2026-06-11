"""
Home Page - FAST Dashboard
"""

import streamlit as st

st.set_page_config(
    page_title="Home - FAST Dashboard",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Home")
st.markdown("Welcome to the FAST Dashboard!")

st.info("👈 Use the sidebar to navigate to different sections of the dashboard.")

st.markdown("""
### About FAST

**FAST** (Forecasting Aggregate-level Self-harm Trends) is an AI-powered decision support system 
designed to help policymakers predict and prevent self-harm at the national level.

### How It Works

1. **Data Collection**: Mental health signals from social media (Fear, Anger, Sadness)
2. **Machine Learning**: 5 different models analyze patterns
3. **Forecasting**: Predict future trends in self-harm rates
4. **Policy Testing**: Simulate impact of interventions

### Ethical Considerations

⚠️ This system is designed for **aggregate national-level forecasting only**. 
It does NOT assess individual risk and should NOT be used for individual-level predictions.
""")
