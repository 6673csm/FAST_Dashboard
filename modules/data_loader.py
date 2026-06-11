"""
Data Loader Module for FAST Dashboard
Handles CSV upload, auto-cleaning, and validation
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import streamlit as st


def load_data(uploaded_file=None, default_path: str = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Smart data loader with auto-cleaning capabilities.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        default_path: Path to default CSV file
        
    Returns:
        Tuple of (cleaned_dataframe, metadata_dict)
    """
    try:
        # Load data
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            source = uploaded_file.name
        elif default_path:
            df = pd.read_csv(default_path)
            source = default_path
        else:
            raise ValueError("No data source provided")
        
        original_rows = len(df)
        original_cols = len(df.columns)
        
        # Auto-clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Parse date column
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            df = df.sort_values(date_cols[0]).reset_index(drop=True)
        
        # Handle missing values
        missing_before = df.isnull().sum().sum()
        
        # Strategy: Forward fill for time series, then mean for remaining
        df = df.fillna(method='ffill')
        
        # For numeric columns, fill remaining with mean
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].mean(), inplace=True)
        
        # Drop rows with >30% missing values
        threshold = len(df.columns) * 0.7
        df = df.dropna(thresh=threshold)
        
        missing_after = df.isnull().sum().sum()
        
        # Validate required columns
        required_cols = ['date', 'me-fea', 'me-ang', 'me-sad', 'gh-death', 'gh-injure']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        # Create metadata
        metadata = {
            'source': source,
            'original_rows': original_rows,
            'original_cols': original_cols,
            'cleaned_rows': len(df),
            'cleaned_cols': len(df.columns),
            'missing_values_before': missing_before,
            'missing_values_after': missing_after,
            'missing_required_cols': missing_cols,
            'date_range': (df[date_cols[0]].min(), df[date_cols[0]].max()) if date_cols else None,
            'data_quality_score': calculate_quality_score(df, missing_cols)
        }
        
        return df, metadata
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None


def calculate_quality_score(df: pd.DataFrame, missing_cols: list) -> float:
    """
    Calculate data quality score (0-100).
    
    Args:
        df: DataFrame to evaluate
        missing_cols: List of missing required columns
        
    Returns:
        Quality score as percentage
    """
    score = 100.0
    
    # Deduct for missing required columns
    score -= len(missing_cols) * 15
    
    # Deduct for missing values
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    score -= missing_pct * 2
    
    # Deduct for duplicate rows
    duplicate_pct = (df.duplicated().sum() / len(df)) * 100
    score -= duplicate_pct * 1.5
    
    return max(0, min(100, score))


def validate_data(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate data meets requirements.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary of validation results
    """
    validations = {}
    
    # Check required columns
    required_cols = ['date', 'me-fea', 'me-ang', 'me-sad', 'gh-death', 'gh-injure']
    validations['has_required_cols'] = all(col in df.columns for col in required_cols)
    
    # Check minimum rows
    validations['sufficient_data'] = len(df) >= 30
    
    # Check date column is datetime
    if 'date' in df.columns:
        validations['valid_dates'] = pd.api.types.is_datetime64_any_dtype(df['date'])
    else:
        validations['valid_dates'] = False
    
    # Check numeric columns are numeric
    numeric_cols = ['me-fea', 'me-ang', 'me-sad', 'gh-death', 'gh-injure']
    validations['valid_numeric'] = all(
        pd.api.types.is_numeric_dtype(df[col]) 
        for col in numeric_cols if col in df.columns
    )
    
    # Check for reasonable value ranges (0-1 for signals, positive for targets)
    if validations['has_required_cols']:
        signal_cols = ['me-fea', 'me-ang', 'me-sad']
        validations['valid_signal_range'] = all(
            (df[col] >= 0).all() and (df[col] <= 1).all() 
            for col in signal_cols
        )
        
        target_cols = ['gh-death', 'gh-injure']
        validations['valid_target_range'] = all(
            (df[col] >= 0).all() 
            for col in target_cols
        )
    else:
        validations['valid_signal_range'] = False
        validations['valid_target_range'] = False
    
    return validations


def get_data_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics for the dataset.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Summary DataFrame
    """
    summary = df.describe().T
    summary['missing'] = df.isnull().sum()
    summary['missing_pct'] = (df.isnull().sum() / len(df) * 100).round(2)
    
    return summary
