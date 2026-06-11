"""
AutoML Module for FAST Dashboard
Multi-model training engine with 5 different algorithms
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import time
import warnings
warnings.filterwarnings('ignore')

# ML Models
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge
from sklearn.svm import SVR
from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA
import joblib


class AutoMLEngine:
    """
    Automated Machine Learning engine for training multiple models.
    """
    
    def __init__(self):
        self.models = {}
        self.training_times = {}
        self.model_configs = {
            'Random Forest': {
                'model': RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    random_state=42,
                    n_jobs=-1
                ),
                'type': 'sklearn'
            },
            'XGBoost': {
                'model': XGBRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42,
                    n_jobs=-1
                ),
                'type': 'sklearn'
            },
            'SVR': {
                'model': SVR(
                    kernel='rbf',
                    C=1.0,
                    gamma='auto'
                ),
                'type': 'sklearn'
            },
            'Bayesian Ridge': {
                'model': BayesianRidge(
                    max_iter=300,
                    alpha_1=1e-6,
                    alpha_2=1e-6
                ),
                'type': 'sklearn'
            }
        }
    
    def train_all_models(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        target_name: str = 'Target'
    ) -> Dict:
        """
        Train all models and return results.
        
        Args:
            X_train: Training features
            y_train: Training target
            target_name: Name of target variable
            
        Returns:
            Dictionary with model results
        """
        results = {}
        
        for model_name, config in self.model_configs.items():
            try:
                start_time = time.time()
                
                model = config['model']
                model.fit(X_train, y_train)
                
                training_time = time.time() - start_time
                
                results[model_name] = {
                    'model': model,
                    'training_time': training_time,
                    'params': model.get_params(),
                    'target': target_name,
                    'status': 'success'
                }
                
                self.models[f"{model_name}_{target_name}"] = model
                self.training_times[f"{model_name}_{target_name}"] = training_time
                
            except Exception as e:
                results[model_name] = {
                    'model': None,
                    'training_time': 0,
                    'params': {},
                    'target': target_name,
                    'status': f'failed: {str(e)}'
                }
        
        # Train ARIMA separately (time series specific)
        try:
            results['ARIMA'] = self._train_arima(y_train, target_name)
        except Exception as e:
            results['ARIMA'] = {
                'model': None,
                'training_time': 0,
                'params': {},
                'target': target_name,
                'status': f'failed: {str(e)}'
            }
        
        return results
    
    def _train_arima(self, y_train: pd.Series, target_name: str) -> Dict:
        """
        Train ARIMA model (time series specific).
        
        Args:
            y_train: Training target
            target_name: Name of target variable
            
        Returns:
            Dictionary with ARIMA results
        """
        start_time = time.time()
        
        # Auto-tune ARIMA order (simple approach)
        # Using (1,1,1) as default - can be improved with auto_arima
        model = ARIMA(y_train, order=(1, 1, 1))
        fitted_model = model.fit()
        
        training_time = time.time() - start_time
        
        self.models[f"ARIMA_{target_name}"] = fitted_model
        self.training_times[f"ARIMA_{target_name}"] = training_time
        
        return {
            'model': fitted_model,
            'training_time': training_time,
            'params': {'order': (1, 1, 1)},
            'target': target_name,
            'status': 'success'
        }
    
    def predict(
        self, 
        model_name: str, 
        X_test: pd.DataFrame,
        target_name: str = 'Target'
    ) -> np.ndarray:
        """
        Make predictions with a specific model.
        
        Args:
            model_name: Name of the model
            X_test: Test features
            target_name: Name of target variable
            
        Returns:
            Predictions array
        """
        model_key = f"{model_name}_{target_name}"
        
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found. Train it first.")
        
        model = self.models[model_key]
        
        # ARIMA predictions are different
        if model_name == 'ARIMA':
            predictions = model.forecast(steps=len(X_test))
            return np.array(predictions)
        else:
            return model.predict(X_test)
    
    def save_model(self, model_name: str, target_name: str, path: str):
        """Save a trained model."""
        model_key = f"{model_name}_{target_name}"
        if model_key in self.models:
            joblib.dump(self.models[model_key], path)
    
    def load_model(self, model_name: str, target_name: str, path: str):
        """Load a saved model."""
        model_key = f"{model_name}_{target_name}"
        self.models[model_key] = joblib.load(path)
    
    def get_feature_importance(
        self, 
        model_name: str, 
        target_name: str,
        feature_names: list
    ) -> pd.DataFrame:
        """
        Get feature importance for tree-based models.
        
        Args:
            model_name: Name of the model
            target_name: Name of target variable
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importance
        """
        model_key = f"{model_name}_{target_name}"
        
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found.")
        
        model = self.models[model_key]
        
        # Get importance based on model type
        if hasattr(model, 'feature_importances_'):
            # Tree-based models (RF, XGBoost)
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # Linear models (Bayesian Ridge)
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
        
        return importance_df


def train_models_for_target(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    target_name: str
) -> Tuple[AutoMLEngine, Dict]:
    """
    Convenience function to train all models for a specific target.
    
    Args:
        X_train: Training features
        X_test: Test features
        y_train: Training target
        y_test: Test target
        target_name: Name of target variable
        
    Returns:
        Tuple of (AutoMLEngine, results_dict)
    """
    engine = AutoMLEngine()
    results = engine.train_all_models(X_train, y_train, target_name)
    
    return engine, results
