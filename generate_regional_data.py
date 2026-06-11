"""
Script to generate enhanced dataset with Indian state/district data
Run this to create sample_mental_signals_regional.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Indian states and major districts
REGIONS = {
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Thane'],
    'Delhi': ['Central Delhi', 'South Delhi', 'North Delhi', 'East Delhi'],
    'Karnataka': ['Bangalore', 'Mysore', 'Mangalore', 'Hubli'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Salem'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi'],
    'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol'],
    'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
    'Rajasthan': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota']
}

# Population data (in thousands)
POPULATION = {
    'Maharashtra': {'Mumbai': 12500, 'Pune': 3100, 'Nagpur': 2400, 'Thane': 1850},
    'Delhi': {'Central Delhi': 1800, 'South Delhi': 2700, 'North Delhi': 3600, 'East Delhi': 1700},
    'Karnataka': {'Bangalore': 8400, 'Mysore': 900, 'Mangalore': 500, 'Hubli': 950},
    'Tamil Nadu': {'Chennai': 7100, 'Coimbatore': 1600, 'Madurai': 1500, 'Salem': 900},
    'Uttar Pradesh': {'Lucknow': 2800, 'Kanpur': 2700, 'Agra': 1600, 'Varanasi': 1200},
    'West Bengal': {'Kolkata': 4500, 'Howrah': 1100, 'Durgapur': 600, 'Asansol': 550},
    'Gujarat': {'Ahmedabad': 5600, 'Surat': 4500, 'Vadodara': 1700, 'Rajkot': 1300},
    'Rajasthan': {'Jaipur': 3100, 'Jodhpur': 1000, 'Udaipur': 450, 'Kota': 1000}
}

# Regional variation factors (multipliers for mental health signals)
REGIONAL_FACTORS = {
    'Maharashtra': {'ME-Fea': 1.1, 'ME-Ang': 1.0, 'ME-Sad': 1.15, 'GH-Death': 1.2},
    'Delhi': {'ME-Fea': 1.2, 'ME-Ang': 1.15, 'ME-Sad': 1.25, 'GH-Death': 1.3},
    'Karnataka': {'ME-Fea': 0.95, 'ME-Ang': 0.9, 'ME-Sad': 1.0, 'GH-Death': 1.0},
    'Tamil Nadu': {'ME-Fea': 0.9, 'ME-Ang': 0.85, 'ME-Sad': 0.95, 'GH-Death': 0.9},
    'Uttar Pradesh': {'ME-Fea': 1.05, 'ME-Ang': 1.1, 'ME-Sad': 1.1, 'GH-Death': 1.15},
    'West Bengal': {'ME-Fea': 1.0, 'ME-Ang': 0.95, 'ME-Sad': 1.05, 'GH-Death': 1.05},
    'Gujarat': {'ME-Fea': 0.85, 'ME-Ang': 0.8, 'ME-Sad': 0.9, 'GH-Death': 0.85},
    'Rajasthan': {'ME-Fea': 0.95, 'ME-Ang': 1.0, 'ME-Sad': 1.0, 'GH-Death': 0.95}
}

def generate_regional_dataset():
    """Generate dataset with regional data"""
    
    # Start date
    start_date = datetime(2023, 1, 1)
    
    # Generate data for each region
    all_data = []
    
    for state, districts in REGIONS.items():
        for district in districts:
            # Generate 365 days of data for this region
            for day in range(365):
                current_date = start_date + timedelta(days=day)
                
                # Base values with trend
                base_fea = 0.45 + (day / 365) * 0.12 + np.random.normal(0, 0.02)
                base_ang = 0.32 + (day / 365) * 0.13 + np.random.normal(0, 0.02)
                base_sad = 0.56 + (day / 365) * 0.11 + np.random.normal(0, 0.02)
                base_death = 12.3 + (day / 365) * 8.8 + np.random.normal(0, 0.5)
                
                # Apply regional factors
                factors = REGIONAL_FACTORS[state]
                me_fea = max(0, min(1, base_fea * factors['ME-Fea']))
                me_ang = max(0, min(1, base_ang * factors['ME-Ang']))
                me_sad = max(0, min(1, base_sad * factors['ME-Sad']))
                gh_death = max(0, base_death * factors['GH-Death'])
                
                # Get population
                population = POPULATION[state][district]
                
                # Create row
                row = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'region': state,
                    'district': district,
                    'population': population,
                    'ME-Fea': round(me_fea, 2),
                    'ME-Ang': round(me_ang, 2),
                    'ME-Sad': round(me_sad, 2),
                    'GH-Death': round(gh_death, 1)
                }
                
                all_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Sort by date and region
    df = df.sort_values(['date', 'region', 'district']).reset_index(drop=True)
    
    return df

if __name__ == '__main__':
    print("Generating regional dataset...")
    df = generate_regional_dataset()
    
    # Save to CSV
    output_path = 'data/sample_mental_signals_regional.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✅ Dataset generated successfully!")
    print(f"📊 Total rows: {len(df)}")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"🗺️ Regions: {df['region'].nunique()}")
    print(f"🏙️ Districts: {df['district'].nunique()}")
    print(f"💾 Saved to: {output_path}")
    
    # Show sample
    print("\n📋 Sample data:")
    print(df.head(10))
    
    # Show summary by region
    print("\n📊 Summary by Region:")
    summary = df.groupby('region').agg({
        'GH-Death': 'mean',
        'ME-Sad': 'mean',
        'population': 'first'
    }).round(2)
    print(summary)
