"""
AutoML Arena Page - FAST Dashboard
Train and compare multiple ML models
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import time

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.preprocessing import create_features, prepare_train_test_split
from modules.automl import AutoMLEngine
from modules.evaluator import create_leaderboard, get_best_model, compare_models_summary
from modules.explainer import get_feature_importance, plot_feature_importance, interpret_feature_importance
from utils.helpers import inject_custom_css, show_success, show_error, show_warning, show_info

st.set_page_config(
    page_title="AutoML Arena - FAST",
    page_icon="🤖",
    layout="wide"
)

inject_custom_css()

st.title("🤖 AutoML Arena")
st.markdown("Train and compare multiple machine learning models")

st.markdown("---")

# Check if data is loaded
if not st.session_state.get('data_loaded', False):
    show_warning("No data loaded! Please go to Data Explorer first.")
    
    if st.button("📊 Go to Data Explorer"):
        st.switch_page("pages/2_📊_Data_Explorer.py")
    
    st.stop()

df = st.session_state.df

# Target selection
st.markdown("### 🎯 Select Target Variable")

col1, col2 = st.columns(2)

with col1:
    target = st.selectbox(
        "Choose what to predict",
        ["gh-death", "gh-injure"],
        format_func=lambda x: "Death Rate" if x == "gh-death" else "Injury Rate"
    )

with col2:
    test_size = st.slider(
        "Test set size (%)",
        min_value=10,
        max_value=40,
        value=20,
        step=5
    ) / 100

st.markdown("---")

# Feature engineering
st.markdown("### ⚙️ Feature Engineering")

with st.expander("View Feature Engineering Details", expanded=False):
    st.markdown("""
    The system automatically creates the following features:
    
    - **Lag Features**: 1, 7, and 30-day lags for each mental signal
    - **Rolling Statistics**: 7-day and 30-day moving averages and standard deviations
    - **Trend Indicators**: Rate of change over 7 days
    - **Interaction Features**: Combinations of mental signals (e.g., Fear × Sadness)
    - **Temporal Features**: Day of week, month, weekend indicator
    
    All features are normalized using StandardScaler.
    """)

# Train models button
st.markdown("### 🚀 Model Training")

if st.button("🚀 Train & Compare All Models", type="primary", use_container_width=True):
    
    with st.spinner("Preparing data and engineering features..."):
        # Create features
        df_features = create_features(df)
        
        # Prepare train/test split
        X_train, X_test, y_train, y_test, scaler = prepare_train_test_split(
            df_features,
            target,
            test_size=test_size,
            scale=True
        )
        
        # Store in session state
        st.session_state.X_train = X_train
        st.session_state.X_test = X_test
        st.session_state.y_train = y_train
        st.session_state.y_test = y_test
        st.session_state.scaler = scaler
        st.session_state.feature_names = X_train.columns.tolist()
    
    show_success(f"Features created! Training set: {len(X_train)} samples, Test set: {len(X_test)} samples")
    
    # Train models
    st.markdown("#### 🔄 Training Progress")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    engine = AutoMLEngine()
    
    model_names = ['Random Forest', 'XGBoost', 'SVR', 'Bayesian Ridge', 'ARIMA']
    
    for i, model_name in enumerate(model_names):
        status_text.markdown(f"**Training {model_name}...**")
        
        # Train individual model
        if model_name == 'ARIMA':
            result = engine._train_arima(y_train, target)
        else:
            config = engine.model_configs[model_name]
            model = config['model']
            
            start_time = time.time()
            model.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            result = {
                'model': model,
                'training_time': training_time,
                'params': model.get_params(),
                'target': target,
                'status': 'success'
            }
            
            engine.models[f"{model_name}_{target}"] = model
            engine.training_times[f"{model_name}_{target}"] = training_time
        
        progress_bar.progress((i + 1) / len(model_names))
        time.sleep(0.3)  # Visual feedback
    
    status_text.markdown("**✅ All models trained successfully!**")
    
    # Initialize models_trained if not exists
    if 'models_trained' not in st.session_state:
        st.session_state.models_trained = {}
    
    # Store engine in session state
    st.session_state.models_trained[target] = engine
    
    # Create leaderboard
    st.markdown("---")
    st.markdown("### 📊 Model Performance Leaderboard")
    
    # Get all trained models
    all_models = {}
    for model_name in model_names:
        model_key = f"{model_name}_{target}"
        if model_key in engine.models:
            all_models[model_name] = {
                'model': engine.models[model_key],
                'training_time': engine.training_times.get(model_key, 0),
                'status': 'success'
            }
    
    leaderboard_df = create_leaderboard(all_models, X_test, y_test, target)
    
    if not leaderboard_df.empty:
        # Highlight winner
        best_model_name = get_best_model(leaderboard_df)
        
        st.markdown(f"### 🏆 Winner: **{best_model_name}**")
        
        # Display leaderboard with styling
        st.dataframe(
            leaderboard_df.style.background_gradient(
                subset=['MAPE'],
                cmap='RdYlGn_r'
            ).background_gradient(
                subset=['R²'],
                cmap='RdYlGn'
            ),
            use_container_width=True,
            height=250
        )
        
        # Store leaderboard
        st.session_state.leaderboard = leaderboard_df
        st.session_state.best_model_name = best_model_name
        st.session_state.current_target = target
        
        # Download leaderboard
        csv = leaderboard_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Leaderboard",
            data=csv,
            file_name=f"leaderboard_{target}.csv",
            mime="text/csv"
        )
        
        # Model comparison summary
        st.markdown("---")
        st.markdown("### 📈 Performance Summary")
        
        summary = compare_models_summary(leaderboard_df)
        st.markdown(summary)
        
        # Feature importance for best model
        st.markdown("---")
        st.markdown("### 🔍 Feature Importance (Explainable AI)")
        
        best_model = all_models[best_model_name]['model']
        
        importance_df = get_feature_importance(
            best_model,
            best_model_name,
            st.session_state.feature_names,
            top_n=15
        )
        
        if importance_df is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = plot_feature_importance(
                    importance_df,
                    title=f"Top 15 Features - {best_model_name}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(interpret_feature_importance(importance_df, target))
                
                # Store importance
                st.session_state.feature_importance = importance_df
        else:
            show_info(f"Feature importance not available for {best_model_name}")
        
        # Next steps
        st.markdown("---")
        st.markdown("### ⏭️ Next Steps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📈 View Forecasts & Evaluation", use_container_width=True):
                st.switch_page("pages/4_📈_Forecast_Eval.py")
        
        with col2:
            if st.button("🎯 Try Policy Simulator", use_container_width=True):
                st.switch_page("pages/5_🎯_Policy_Simulator.py")
    
    else:
        show_error("Failed to create leaderboard. Please check your data.")

else:
    # Show existing results if available
    if target in st.session_state.get('models_trained', {}):
        show_info(f"Models already trained for {target}. Click the button above to retrain.")
        
        if 'leaderboard' in st.session_state:
            st.markdown("### 📊 Previous Results")
            st.dataframe(st.session_state.leaderboard, use_container_width=True)
    else:
        show_info("Click the button above to start training models!")
        
        st.markdown("""
        ### 🤖 Models to be Trained
        
        The AutoML Arena will train and compare the following models:
        
        1. **ARIMA** - Classical time series model (baseline)
        2. **Random Forest** - Ensemble of decision trees
        3. **XGBoost** - Gradient boosting (usually best performer)
        4. **Support Vector Regression (SVR)** - Kernel-based regression
        5. **Bayesian Ridge** - Probabilistic linear regression
        
        ### 📊 Evaluation Metrics
        
        Models are evaluated using:
        
        - **MAE** (Mean Absolute Error): Average prediction error
        - **RMSE** (Root Mean Squared Error): Penalizes large errors
        - **MAPE** (Mean Absolute Percentage Error): Percentage-based error
        - **R² Score**: Variance explained (0-1, higher is better)
        
        The leaderboard is sorted by **MAPE** (lower is better).
        """)
