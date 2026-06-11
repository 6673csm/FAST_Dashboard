"""
Evaluation Module for FAST Dashboard
Performance metrics and leaderboard generation
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, List


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate all performance metrics.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        Dictionary of metrics
    """
    # Ensure arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Calculate metrics
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # MAPE (handle division by zero)
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.any() else 0
    
    return {
        'MAE': round(mae, 4),
        'RMSE': round(rmse, 4),
        'MAPE': round(mape, 4),
        'R²': round(r2, 4)
    }


def create_leaderboard(
    models: Dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    target_name: str
) -> pd.DataFrame:
    """
    Create performance leaderboard for all models.
    
    Args:
        models: Dictionary of trained models from AutoMLEngine
        X_test: Test features
        y_test: Test target
        target_name: Name of target variable
        
    Returns:
        DataFrame with sorted leaderboard
    """
    leaderboard_data = []
    
    for model_name, model_info in models.items():
        if model_info['status'] != 'success':
            continue
        
        try:
            model = model_info['model']
            
            # Make predictions
            if model_name == 'ARIMA':
                y_pred = model.forecast(steps=len(y_test))
            else:
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = calculate_metrics(y_test, y_pred)
            
            leaderboard_data.append({
                'Model': model_name,
                'MAE': metrics['MAE'],
                'RMSE': metrics['RMSE'],
                'MAPE': metrics['MAPE'],
                'R²': metrics['R²'],
                'Training Time (s)': round(model_info['training_time'], 2)
            })
            
        except Exception as e:
            print(f"Error evaluating {model_name}: {str(e)}")
            continue
    
    # Create DataFrame and sort by MAPE (lower is better)
    leaderboard_df = pd.DataFrame(leaderboard_data)
    
    if not leaderboard_df.empty:
        leaderboard_df = leaderboard_df.sort_values('MAPE', ascending=True).reset_index(drop=True)
        
        # Add rank
        leaderboard_df.insert(0, 'Rank', range(1, len(leaderboard_df) + 1))
    
    return leaderboard_df


def get_best_model(leaderboard_df: pd.DataFrame) -> str:
    """
    Get the name of the best performing model.
    
    Args:
        leaderboard_df: Leaderboard DataFrame
        
    Returns:
        Name of best model
    """
    if leaderboard_df.empty:
        return None
    
    return leaderboard_df.iloc[0]['Model']


def calculate_residuals(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Calculate residuals (errors).
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        Array of residuals
    """
    return np.array(y_true) - np.array(y_pred)


def evaluate_model_performance(
    model,
    model_name: str,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series
) -> Dict:
    """
    Comprehensive model evaluation.
    
    Args:
        model: Trained model
        model_name: Name of the model
        X_train: Training features
        X_test: Test features
        y_train: Training target
        y_test: Test target
        
    Returns:
        Dictionary with comprehensive evaluation results
    """
    results = {}
    
    # Training set performance
    if model_name == 'ARIMA':
        y_train_pred = model.fittedvalues
        y_test_pred = model.forecast(steps=len(y_test))
    else:
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
    
    results['train_metrics'] = calculate_metrics(y_train, y_train_pred)
    results['test_metrics'] = calculate_metrics(y_test, y_test_pred)
    
    # Predictions
    results['y_train_pred'] = y_train_pred
    results['y_test_pred'] = y_test_pred
    
    # Residuals
    results['train_residuals'] = calculate_residuals(y_train, y_train_pred)
    results['test_residuals'] = calculate_residuals(y_test, y_test_pred)
    
    # Overfitting check
    train_r2 = results['train_metrics']['R²']
    test_r2 = results['test_metrics']['R²']
    results['overfitting_score'] = train_r2 - test_r2
    results['is_overfitting'] = results['overfitting_score'] > 0.1
    
    return results


def compare_models_summary(leaderboard_df: pd.DataFrame) -> str:
    """
    Generate a text summary comparing models.
    
    Args:
        leaderboard_df: Leaderboard DataFrame
        
    Returns:
        Text summary
    """
    if leaderboard_df.empty:
        return "No models to compare."
    
    best_model = leaderboard_df.iloc[0]
    worst_model = leaderboard_df.iloc[-1]
    
    summary = f"""
    **Model Comparison Summary**
    
    🏆 **Best Model:** {best_model['Model']}
    - MAPE: {best_model['MAPE']:.2f}%
    - RMSE: {best_model['RMSE']:.4f}
    - R²: {best_model['R²']:.4f}
    - Training Time: {best_model['Training Time (s)']:.2f}s
    
    📉 **Baseline Model:** {worst_model['Model']}
    - MAPE: {worst_model['MAPE']:.2f}%
    
    **Improvement:** {((worst_model['MAPE'] - best_model['MAPE']) / worst_model['MAPE'] * 100):.1f}% better than baseline
    
    **Total Models Trained:** {len(leaderboard_df)}
    """
    
    return summary
