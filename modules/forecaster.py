"""
Future Forecasting Module for FAST Dashboard
Predict death and injury cases for the next 2-3 months
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime, timedelta


def generate_future_dates(last_date: pd.Timestamp, n_days: int = 90) -> pd.DatetimeIndex:
    """
    Generate future dates for forecasting.
    
    Args:
        last_date: Last date in historical data
        n_days: Number of days to forecast (default 90 = ~3 months)
        
    Returns:
        DatetimeIndex with future dates
    """
    return pd.date_range(start=last_date + timedelta(days=1), periods=n_days, freq='D')


def extrapolate_signals(
    df: pd.DataFrame,
    n_days: int = 90,
    method: str = 'last_value'
) -> pd.DataFrame:
    """
    Extrapolate mental health signals for future dates.
    
    Args:
        df: Historical data with mental health signals
        n_days: Number of days to forecast
        method: Extrapolation method ('last_value', 'moving_average', 'trend')
        
    Returns:
        DataFrame with extrapolated signals
    """
    signal_cols = ['me-fea', 'me-ang', 'me-sad']
    
    # Get last date
    if 'date' in df.columns:
        last_date = pd.to_datetime(df['date']).max()
    else:
        last_date = df.index.max()
    
    # Generate future dates
    future_dates = generate_future_dates(last_date, n_days)
    
    # Extrapolate signals
    future_data = {'date': future_dates}
    
    for col in signal_cols:
        if col in df.columns:
            if method == 'last_value':
                # Use last observed value
                future_data[col] = df[col].iloc[-1]
                
            elif method == 'moving_average':
                # Use 30-day moving average
                future_data[col] = df[col].tail(30).mean()
                
            elif method == 'trend':
                # Linear trend extrapolation
                recent_data = df[col].tail(60).values
                x = np.arange(len(recent_data))
                coeffs = np.polyfit(x, recent_data, 1)
                
                # Extrapolate
                future_x = np.arange(len(recent_data), len(recent_data) + n_days)
                future_values = np.polyval(coeffs, future_x)
                
                # Clip to valid range [0, 1]
                future_values = np.clip(future_values, 0, 1)
                future_data[col] = future_values
    
    future_df = pd.DataFrame(future_data)
    return future_df


def create_future_features(
    historical_df: pd.DataFrame,
    future_signals: pd.DataFrame,
    feature_names: list
) -> pd.DataFrame:
    """
    Create features for future forecasting using historical context.
    
    Args:
        historical_df: Historical data with all features
        future_signals: Future mental health signals
        feature_names: List of feature names from training
        
    Returns:
        DataFrame with future features
    """
    from modules.preprocessing import create_features
    
    # Combine historical and future data for lag feature calculation
    combined_df = pd.concat([
        historical_df[['date', 'me-fea', 'me-ang', 'me-sad']].tail(60),
        future_signals
    ], ignore_index=True)
    
    # Create features
    combined_features = create_features(combined_df)
    
    # Extract only future features
    future_features = combined_features.tail(len(future_signals))
    
    # Ensure all required features exist
    for feat in feature_names:
        if feat not in future_features.columns:
            future_features[feat] = 0
    
    # Select only the features used in training
    future_features = future_features[feature_names]
    
    return future_features


def forecast_future(
    model,
    model_name: str,
    historical_df: pd.DataFrame,
    scaler,
    feature_names: list,
    n_days: int = 90,
    extrapolation_method: str = 'moving_average',
    population: int = 1000000
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate future forecasts for death/injury cases.
    
    Args:
        model: Trained model
        model_name: Name of the model
        historical_df: Historical data
        scaler: Fitted scaler
        feature_names: List of feature names
        n_days: Number of days to forecast
        extrapolation_method: Method to extrapolate signals
        population: Population size for converting rates to cases (default 1 million)
        
    Returns:
        Tuple of (future_dates_df, predictions_df)
    """
    # Extrapolate mental health signals
    future_signals = extrapolate_signals(
        historical_df,
        n_days=n_days,
        method=extrapolation_method
    )
    
    # Create features for future dates
    future_features = create_future_features(
        historical_df,
        future_signals,
        feature_names
    )
    
    # Scale features
    future_features_scaled = scaler.transform(future_features)
    
    # Make predictions (rates)
    if model_name == 'ARIMA':
        predicted_rates = model.forecast(steps=n_days)
    else:
        predicted_rates = model.predict(future_features_scaled)
    
    # Convert rates to actual case counts
    # Rate is typically per 100,000 population, so scale accordingly
    predicted_cases = (predicted_rates * population) / 100000
    predicted_cases = np.round(predicted_cases).astype(int)
    
    # Create results DataFrame
    results_df = pd.DataFrame({
        'date': future_signals['date'],
        'predicted_rate': predicted_rates,
        'predicted_cases': predicted_cases,
        'me-fea': future_signals['me-fea'],
        'me-ang': future_signals['me-ang'],
        'me-sad': future_signals['me-sad']
    })
    
    return future_signals, results_df


def calculate_monthly_aggregates(forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly aggregates from daily forecasts.
    
    Args:
        forecast_df: DataFrame with daily forecasts
        
    Returns:
        DataFrame with monthly aggregates
    """
    forecast_df['month'] = pd.to_datetime(forecast_df['date']).dt.to_period('M')
    
    agg_dict = {
        'predicted_cases': ['mean', 'min', 'max', 'sum'],
        'me-fea': 'mean',
        'me-ang': 'mean',
        'me-sad': 'mean'
    }
    
    # Only include predicted_rate if it exists
    if 'predicted_rate' in forecast_df.columns:
        agg_dict['predicted_rate'] = 'mean'
    
    monthly_agg = forecast_df.groupby('month').agg(agg_dict).round(0)
    
    monthly_agg.columns = ['_'.join(col).strip() for col in monthly_agg.columns.values]
    monthly_agg = monthly_agg.reset_index()
    monthly_agg['month'] = monthly_agg['month'].astype(str)
    
    return monthly_agg


def generate_forecast_summary(
    forecast_df: pd.DataFrame,
    target_name: str,
    historical_avg_cases: float
) -> str:
    """
    Generate a summary report of the forecast.
    
    Args:
        forecast_df: DataFrame with forecasts
        target_name: Name of target variable
        historical_avg_cases: Historical average cases for comparison
        
    Returns:
        Markdown formatted summary
    """
    forecast_avg = forecast_df['predicted_cases'].mean()
    forecast_min = forecast_df['predicted_cases'].min()
    forecast_max = forecast_df['predicted_cases'].max()
    forecast_total = forecast_df['predicted_cases'].sum()
    
    change_pct = ((forecast_avg - historical_avg_cases) / historical_avg_cases) * 100
    
    trend = "increase" if change_pct > 0 else "decrease"
    trend_emoji = "📈" if change_pct > 0 else "📉"
    
    # Determine case type label
    case_type = "Deaths" if "death" in target_name.lower() else "Injuries"
    
    summary = f"""
## 📊 Forecast Summary for {target_name.replace('-', ' ').title()}

### Overall Predictions (Next {len(forecast_df)} Days)

- **Average Daily Cases**: {forecast_avg:.0f} {case_type.lower()}
- **Daily Range**: {forecast_min:.0f} - {forecast_max:.0f} {case_type.lower()}
- **Total Predicted Cases**: {forecast_total:,.0f} {case_type.lower()}
- **Historical Daily Average**: {historical_avg_cases:.0f} {case_type.lower()}
- **Trend**: {trend_emoji} {abs(change_pct):.1f}% {trend} compared to historical average

### Key Insights

"""
    
    if abs(change_pct) > 10:
        if change_pct > 0:
            additional_cases = (forecast_avg - historical_avg_cases) * len(forecast_df)
            summary += f"⚠️ **Warning**: Model predicts a significant **{change_pct:.1f}% increase** in {case_type.lower()}. This means approximately **{additional_cases:,.0f} additional {case_type.lower()}** over the forecast period. Consider preventive interventions.\n\n"
        else:
            prevented_cases = (historical_avg_cases - forecast_avg) * len(forecast_df)
            summary += f"✅ **Positive**: Model predicts a **{abs(change_pct):.1f}% decrease** in {case_type.lower()}. This could prevent approximately **{prevented_cases:,.0f} {case_type.lower()}** over the forecast period. Current trends appear favorable.\n\n"
    else:
        summary += f"📊 **Stable**: Model predicts relatively stable {case_type.lower()} (±{abs(change_pct):.1f}% change).\n\n"
    
    # Monthly breakdown
    monthly_agg = calculate_monthly_aggregates(forecast_df)
    
    summary += "### Monthly Breakdown\n\n"
    for _, row in monthly_agg.iterrows():
        summary += f"- **{row['month']}**: Total {row['predicted_cases_sum']:,.0f} {case_type.lower()} (Avg {row['predicted_cases_mean']:.0f}/day, Range {row['predicted_cases_min']:.0f}-{row['predicted_cases_max']:.0f})\n"
    
    return summary
