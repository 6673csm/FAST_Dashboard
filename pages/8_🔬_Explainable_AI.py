"""
Explainable AI Dashboard Page
SHAP-based model explanations and interpretability
"""

import streamlit as st
import pandas as pd
import numpy as np
from modules import shap_explainer
from utils.helpers import inject_custom_css, show_info, show_warning, show_error

# Page config
st.set_page_config(
    page_title="Explainable AI - FAST",
    page_icon="🔬",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Header
st.title("🔬 Explainable AI Dashboard")
st.markdown("**Understand model predictions with SHAP (SHapley Additive exPlanations)**")

st.markdown("---")

# Check if models are trained
if not st.session_state.get('models_trained', False):
    show_warning("⚠️ No models trained yet! Please go to AutoML Arena first.")
    if st.button("🤖 Go to AutoML Arena"):
        st.switch_page("pages/3_🤖_AutoML_Arena.py")
    st.stop()

# Get data from session state with safe defaults
X_test = st.session_state.get('X_test')
y_test = st.session_state.get('y_test')
current_target = st.session_state.get('current_target', 'gh-death')

# Get the engine for the current target
models_trained_dict = st.session_state.get('models_trained', {})
engine = models_trained_dict.get(current_target)

# Check if we have the required data
if X_test is None or y_test is None:
    show_error("❌ Test data not found. Please go to AutoML Arena and train models first.")
    if st.button("🤖 Go to AutoML Arena", key="goto_automl_2"):
        st.switch_page("pages/3_🤖_AutoML_Arena.py")
    st.stop()

if engine is None or not hasattr(engine, 'models') or len(engine.models) == 0:
    show_error("❌ No trained models found. Please train models in AutoML Arena first.")
    if st.button("🤖 Go to AutoML Arena", key="goto_automl_3"):
        st.switch_page("pages/3_🤖_AutoML_Arena.py")
    st.stop()

# Get models from engine
models = engine.models
available_model_names = [name.replace(f"_{current_target}", "") for name in models.keys() if current_target in name]

# Filter out ARIMA for SHAP (not compatible)
shap_compatible_models = [name for name in available_model_names if name != 'ARIMA']

if len(shap_compatible_models) == 0:
    show_warning("⚠️ No SHAP-compatible models found. Please train Random Forest or XGBoost.")
    st.stop()

# Sidebar - Model Selection
st.sidebar.header("⚙️ Configuration")

selected_model_name = st.sidebar.selectbox(
    "Select Model",
    shap_compatible_models,
    help="ARIMA doesn't support SHAP explanations"
)

# Get the full model key
model_key = f"{selected_model_name}_{current_target}"

# Sample selection
sample_idx = st.sidebar.slider(
    "Select Sample to Explain",
    0,
    len(X_test) - 1,
    0,
    help="Choose which prediction to explain in detail"
)

# Compute SHAP values button
compute_shap = st.sidebar.button("🔬 Compute SHAP Values", type="primary")

# Initialize SHAP values in session state
if 'shap_values' not in st.session_state:
    st.session_state.shap_values = {}

# Compute SHAP values
if compute_shap or selected_model_name in st.session_state.shap_values:
    if compute_shap:
        with st.spinner(f"Computing SHAP values for {selected_model_name}... This may take a minute."):
            model = models[model_key]
            shap_values, explainer = shap_explainer.compute_shap_values(
                model,
                selected_model_name,
                X_test,
                max_samples=100
            )
            
            if shap_values is not None:
                st.session_state.shap_values[selected_model_name] = shap_values
                show_info("✅ SHAP values computed successfully!")
            else:
                show_error("❌ Failed to compute SHAP values.")
                st.stop()
    
    # Get SHAP values from session state
    shap_values = st.session_state.shap_values.get(selected_model_name)
    
    if shap_values is None:
        show_warning("⚠️ Click 'Compute SHAP Values' to generate explanations.")
        st.stop()
    
    # Main content
    st.markdown("---")
    
    # Tab layout
    tab1, tab2, tab3 = st.tabs(["📊 Summary", "💧 Individual Explanation", "📈 Feature Importance"])
    
    with tab1:
        st.subheader("📊 SHAP Summary - Overall Feature Importance")
        st.markdown("""
        This chart shows which features are most important across **all predictions**.
        Features at the top have the highest impact on model predictions.
        """)
        
        # Create summary plot
        summary_fig = shap_explainer.plot_shap_summary(
            shap_values,
            title=f"SHAP Feature Importance - {selected_model_name}"
        )
        st.plotly_chart(summary_fig, use_container_width=True)
        
        # Feature importance table
        st.subheader("📋 Feature Importance Ranking")
        importance_df = shap_explainer.get_shap_feature_importance(shap_values)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                importance_df.head(10).style.format({
                    'Importance': '{:.4f}',
                    'Importance %': '{:.2f}%'
                }),
                use_container_width=True,
                height=400
            )
        
        with col2:
            st.metric("Total Features", len(importance_df))
            st.metric("Top Feature", importance_df.iloc[0]['Feature'])
            st.metric("Top Importance", f"{importance_df.iloc[0]['Importance %']:.1f}%")
    
    with tab2:
        st.subheader(f"💧 Waterfall Explanation - Sample #{sample_idx}")
        st.markdown("""
        This waterfall chart shows how each feature **pushes the prediction** up (green) or down (red) 
        from the base value (average prediction).
        """)
        
        # Get prediction for this sample
        pred_value = models[model_key].predict(X_test.iloc[[sample_idx]])[0]
        
        # Create waterfall plot
        waterfall_fig = shap_explainer.plot_shap_waterfall(
            shap_values,
            sample_idx=sample_idx,
            title=f"SHAP Waterfall - {selected_model_name} (Sample #{sample_idx})"
        )
        st.plotly_chart(waterfall_fig, use_container_width=True)
        
        # Natural language explanation
        st.subheader("📝 Natural Language Explanation")
        explanation_text = shap_explainer.explain_prediction_shap(
            shap_values,
            sample_idx=sample_idx,
            prediction_value=pred_value,
            target_name="gh-death"
        )
        st.markdown(explanation_text)
        
        # Show actual feature values
        st.subheader("📊 Feature Values for This Sample")
        sample_data = X_test.iloc[sample_idx].to_frame(name='Value')
        sample_data['SHAP Impact'] = shap_values[sample_idx].values
        sample_data = sample_data.sort_values('SHAP Impact', key=abs, ascending=False)
        
        st.dataframe(
            sample_data.head(15).style.format({
                'Value': '{:.3f}',
                'SHAP Impact': '{:.4f}'
            }).background_gradient(subset=['SHAP Impact'], cmap='RdYlGn_r'),
            use_container_width=True,
            height=500
        )
    
    with tab3:
        st.subheader("📈 SHAP Feature Importance vs Traditional")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### SHAP-based Importance")
            st.markdown("*Based on actual impact on predictions*")
            shap_imp = shap_explainer.get_shap_feature_importance(shap_values)
            st.dataframe(
                shap_imp.head(10).style.format({
                    'Importance': '{:.4f}',
                    'Importance %': '{:.2f}%'
                }),
                use_container_width=True,
                height=400
            )
        
        with col2:
            st.markdown("#### Traditional Importance")
            st.markdown("*Based on model coefficients/splits*")
            
            # Get traditional feature importance
            model = models[model_key]
            if hasattr(model, 'feature_importances_'):
                trad_imp = pd.DataFrame({
                    'Feature': X_test.columns,
                    'Importance': model.feature_importances_
                }).sort_values('Importance', ascending=False)
                trad_imp['Importance %'] = (trad_imp['Importance'] / trad_imp['Importance'].sum() * 100)
                
                st.dataframe(
                    trad_imp.head(10).style.format({
                        'Importance': '{:.4f}',
                        'Importance %': '{:.2f}%'
                    }),
                    use_container_width=True,
                    height=400
                )
            elif hasattr(model, 'coef_'):
                trad_imp = pd.DataFrame({
                    'Feature': X_test.columns,
                    'Importance': np.abs(model.coef_)
                }).sort_values('Importance', ascending=False)
                trad_imp['Importance %'] = (trad_imp['Importance'] / trad_imp['Importance'].sum() * 100)
                
                st.dataframe(
                    trad_imp.head(10).style.format({
                        'Importance': '{:.4f}',
                        'Importance %': '{:.2f}%'
                    }),
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("Traditional feature importance not available for this model.")
        
        st.markdown("---")
        st.markdown("""
        ### 🔍 Key Differences:
        
        - **SHAP Importance**: Shows the actual average impact of each feature on predictions
        - **Traditional Importance**: Shows how often features are used in the model structure
        
        SHAP values are generally more reliable for understanding **true feature impact**.
        """)

else:
    # Initial state - show instructions
    st.info("""
    ### 🔬 How to Use Explainable AI
    
    1. **Select a model** from the sidebar (tree-based models work best)
    2. **Click "Compute SHAP Values"** to generate explanations
    3. **Explore the tabs**:
       - **Summary**: See overall feature importance
       - **Individual Explanation**: Understand specific predictions
       - **Feature Importance**: Compare SHAP vs traditional methods
    
    **Note**: SHAP computation may take 30-60 seconds for the first time.
    """)
    
    st.markdown("---")
    
    # Show model info
    st.subheader("📊 Available Models")
    
    cols = st.columns(len(shap_compatible_models))
    for idx, model_name in enumerate(shap_compatible_models):
        with cols[idx]:
            st.metric(model_name, "Ready")

# Footer
st.markdown("---")
st.markdown("""
### 📚 About SHAP

**SHAP (SHapley Additive exPlanations)** is a game-theoretic approach to explain machine learning predictions.
It provides:
- **Consistent** explanations across all models
- **Local** explanations for individual predictions
- **Global** feature importance rankings
- **Theoretically sound** based on Shapley values from cooperative game theory

Learn more: [SHAP Documentation](https://shap.readthedocs.io/)
""")
