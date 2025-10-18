import pandas as pd
import os
from datetime import datetime, timedelta


def get_percentage_change(ticker: str, days: int) -> float:
    """
    Calculate the percentage change in ETF value over the specified number of calendar days.
    
    Args:
        ticker: The ETF ticker code (e.g., 'SOXS')
        days: The number of calendar days to look back from the most recent date
        
    Returns:
        The percentage change in value over the specified period
        
    Raises:
        FileNotFoundError: If the CSV file for the ticker doesn't exist
        ValueError: If the number of days is invalid or no data available for the target date
    """
    # Construct the file path
    csv_path = os.path.join('assets', f'{ticker}.csv')
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found for ticker: {ticker}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    if days < 1:
        raise ValueError("Number of days must be at least 1")
    
    # Parse the Date column as datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Get the most recent date (this is 'today')
    today_date = df.iloc[-1]['Date']
    today_price = df.iloc[-1]['Close']
    
    # Calculate the target date (days ago from today)
    target_date = today_date - timedelta(days=days)
    
    # Find the closest date on or before the target date
    past_data = df[df['Date'] <= target_date]
    
    if len(past_data) == 0:
        raise ValueError(f"No data available for {days} days ago (target date: {target_date.date()})")
    
    # Get the price from the closest available date
    past_price = past_data.iloc[-1]['Close']
    
    # Calculate percentage change
    percentage_change = ((today_price - past_price) / past_price) * 100

    return round(percentage_change, 2)

print(get_percentage_change("SOXS", 364))