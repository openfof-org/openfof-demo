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
    percentage_change = ((today_price - past_price) / past_price)

    return round(percentage_change, 4)

def get_volatility(ticker: str, days: int) -> float:
    """
    Calculate the volatility (Annualized Standard Deviation) of the ETF over the specified number of calendar days.
    
    Args:
        ticker: The ETF ticker code (e.g., 'SOXS')
        days: The number of calendar days to look back from the most recent date
        
    Returns:
        The volatility (standard deviation of daily returns) over the specified period
        
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
    
    # Calculate the target date (days ago from today)
    target_date = today_date - timedelta(days=days)
    
    # Filter data for the specified period
    period_data = df[df['Date'] >= target_date]
    
    if len(period_data) < 2:
        raise ValueError(f"Not enough data available for volatility calculation over {days} days")
    
    # Calculate daily returns
    period_data['Daily Return'] = period_data['Close'].pct_change()
    
    # Calculate volatility (standard deviation of daily returns)
    volatility = period_data['Daily Return'].std() * (252 ** 0.5)  # Annualized volatility
    
    return round(volatility, 4)

def calculate_sharpe_ratio(return_aer: float, volatility: float, risk_free_rate: float = 0.00) -> float:
    """
    Calculate the Sharpe Ratio given the annualized return, volatility, and risk-free rate.
    Sharpe Ratio = (Return_AER - Risk_Free_Rate) / Volatility

    It is a measure of return per unit of risk.
    """
    if volatility == 0:
        raise ValueError("Volatility is zero, cannot calculate Sharpe Ratio!")
    excess_return = return_aer - risk_free_rate
    output = excess_return / volatility  # Assuming volatility is not zero
    return round(output, 4)

if __name__ == "__main__":
    print(get_percentage_change("SOXS", 364))
    print(get_volatility("SOXS", 364))
    print(calculate_sharpe_ratio(get_percentage_change("SOXS", 364), get_volatility("SOXS", 364)))