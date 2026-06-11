"""
Preprocessing Module for FAST Dashboard
Feature engineering and data preparation for ML models
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List
import joblib


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features from raw data.
    
    Args:
        df: Raw DataFrame with mental signals
        
    Returns:
        DataFrame with additional features
    """
    df = df.copy()
    
    # Ensure date is index for time series operations
    if 'date' in df.columns:
        df = df.set_index('date')
    
    feature_cols = ['me-fea', 'me-ang', 'me-sad']
    
    # 1. Lag Features (1, 7, 30 days)
    for col in feature_cols:
        df[f'{col}_lag1'] = df[col].shift(1)
        df[f'{col}_lag7'] = df[col].shift(7)
        df[f'{col}_lag30'] = df[col].shift(30)
    
    # 2. Rolling Statistics (7-day and 30-day windows)
    for col in feature_cols:
        df[f'{col}_ma7'] = df[col].rolling(window=7, min_periods=1).mean()
        df[f'{col}_ma30'] = df[col].rolling(window=30, min_periods=1).mean()
        df[f'{col}_std7'] = df[col].rolling(window=7, min_periods=1).std()
    
    # 3. Trend Indicators (rate of change)
    for col in feature_cols:
        df[f'{col}_roc'] = df[col].pct_change(periods=7)
    
    # 4. Interaction Features
    df['fea_sad_interaction'] = df['me-fea'] * df['me-sad']
    df['ang_sad_interaction'] = df['me-ang'] * df['me-sad']
    df['total_negative_emotion'] = df['me-fea'] + df['me-ang'] + df['me-sad']
    
    # 5. Temporal Features
    if isinstance(df.index, pd.DatetimeIndex):
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        df['day_of_month'] = df.index.day
        df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
    
    # Fill NaN values created by lag/rolling operations
    df = df.fillna(method='bfill').fillna(0)
    
    return df


def prepare_train_test_split(
    df: pd.DataFrame, 
    target_col: str,
    test_size: float = 0.2,
    scale: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    """
    Prepare train/test split with temporal ordering preserved.
    
    Args:
        df: DataFrame with features
        target_col: Name of target column ('gh-death' or 'gh-injure')
        test_size: Proportion of data for testing
        scale: Whether to apply StandardScaler
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, scaler)
    """
    # Separate features and target
    feature_cols = [col for col in df.columns if col not in ['gh-death', 'gh-injure']]
    
    # Reset index to get date as column
    df_reset = df.reset_index()
    
    # Temporal split (no shuffling for time series)
    split_idx = int(len(df_reset) * (1 - test_size))
    
    train_df = df_reset.iloc[:split_idx]
    test_df = df_reset.iloc[split_idx:]
    
    # Separate X and y
    X_train = train_df[feature_cols]
    X_test = test_df[feature_cols]
    y_train = train_df[target_col]
    y_test = test_df[target_col]
    
    # Remove date column if present
    if 'date' in X_train.columns:
        X_train = X_train.drop('date', axis=1)
        X_test = X_test.drop('date', axis=1)
    
    # Scale features
    scaler = None
    if scale:
        scaler = StandardScaler()
        X_train = pd.DataFrame(
            scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        X_test = pd.DataFrame(
            scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )
    
    return X_train, X_test, y_train, y_test, scaler


def select_features_by_correlation(
    X: pd.DataFrame, 
    y: pd.Series, 
    threshold: float = 0.05
) -> List[str]:
    """
    Select features based on correlation with target.
    
    Args:
        X: Feature DataFrame
        y: Target Series
        threshold: Minimum absolute correlation to keep feature
        
    Returns:
        List of selected feature names
    """
    correlations = X.corrwith(y).abs()
    selected = correlations[correlations > threshold].index.tolist()
    
    return selected if selected else X.columns.tolist()


def remove_correlated_features(
    X: pd.DataFrame, 
    threshold: float = 0.95
) -> pd.DataFrame:
    """
    Remove highly correlated features to reduce multicollinearity.
    
    Args:
        X: Feature DataFrame
        threshold: Correlation threshold above which to remove features
        
    Returns:
        DataFrame with reduced features
    """
    corr_matrix = X.corr().abs()
    upper_triangle = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )
    
    to_drop = [column for column in upper_triangle.columns 
               if any(upper_triangle[column] > threshold)]
    
    return X.drop(columns=to_drop)


def save_preprocessor(scaler: StandardScaler, path: str):
    """Save scaler for later use."""
    joblib.dump(scaler, path)


def load_preprocessor(path: str) -> StandardScaler:
    """Load saved scaler."""
    return joblib.load(path)
