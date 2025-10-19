"""
Monte Carlo Simulation Demo
Demonstrates the enhanced Monte Carlo simulation with Geometric Brownian Motion
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


def old_linear_projection(df: pd.DataFrame, num_days: int) -> pd.DataFrame:
    """
    OLD METHOD: Simple linear projection based on average daily returns.
    This is what you might have had before, or a simplistic approach.
    """
    if len(df) < 2:
        return pd.DataFrame()
    
    # Calculate simple daily returns
    returns = df['Close'].pct_change().dropna()
    avg_return = returns.mean()
    
    last_price = df.iloc[-1]['Close']
    last_date = df.iloc[-1]['Date']
    
    future_dates = [last_date + timedelta(days=i+1) for i in range(num_days)]
    future_prices = []
    
    price = last_price
    for _ in range(num_days):
        price = price * (1 + avg_return)
        future_prices.append(price)
    
    return pd.DataFrame({
        'Date': future_dates,
        'Close': future_prices
    })


def monte_carlo_gbm(df: pd.DataFrame, num_days: int, simulations: int = 1000) -> pd.DataFrame:
    """
    NEW METHOD: Monte Carlo simulation with Geometric Brownian Motion.
    This is the enhanced implementation.
    """
    if len(df) < 2:
        return pd.DataFrame()
    
    # Calculate daily log returns (more appropriate for GBM)
    log_returns = (df['Close'] / df['Close'].shift(1)).apply(np.log).dropna()
    
    # Calculate drift (mu) and volatility (sigma) from historical data
    mu = log_returns.mean()
    sigma = log_returns.std()
    
    last_price = df.iloc[-1]['Close']
    last_date = df.iloc[-1]['Date']
    
    future_dates = [last_date + timedelta(days=i+1) for i in range(num_days)]
    
    # Monte Carlo simulation using Geometric Brownian Motion
    simulated_prices = np.zeros((simulations, num_days))
    
    for sim in range(simulations):
        prices = np.zeros(num_days)
        price = last_price
        
        for day in range(num_days):
            random_shock = np.random.standard_normal()
            drift = (mu - 0.5 * sigma ** 2)
            diffusion = sigma * random_shock
            price = price * np.exp(drift + diffusion)
            prices[day] = price
        
        simulated_prices[sim, :] = prices
    
    # Calculate statistics
    mean_prices = np.mean(simulated_prices, axis=0)
    median_prices = np.median(simulated_prices, axis=0)
    std_prices = np.std(simulated_prices, axis=0)
    lower_bound = np.percentile(simulated_prices, 5, axis=0)
    upper_bound = np.percentile(simulated_prices, 95, axis=0)
    
    return pd.DataFrame({
        'Date': future_dates,
        'Close': mean_prices,
        'Median': median_prices,
        'StdDev': std_prices,
        'Lower90': lower_bound,
        'Upper90': upper_bound
    })


def visualize_comparison(df_hist, df_linear, df_mc, symbol, save_path='comparison.png'):
    """
    Create a visualization comparing the two methods.
    """
    plt.figure(figsize=(14, 8))
    
    # Plot historical data
    plt.plot(df_hist['Date'], df_hist['Close'], 
             label='Historical', color='black', linewidth=2)
    
    # Plot linear projection
    plt.plot(df_linear['Date'], df_linear['Close'], 
             label='Old: Linear Projection', color='red', 
             linestyle='--', linewidth=2)
    
    # Plot Monte Carlo mean
    plt.plot(df_mc['Date'], df_mc['Close'], 
             label='New: Monte Carlo Mean', color='blue', linewidth=2)
    
    # Plot Monte Carlo confidence interval
    plt.fill_between(df_mc['Date'], df_mc['Lower90'], df_mc['Upper90'],
                     alpha=0.3, color='blue', label='90% Confidence Interval')
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    plt.title(f'{symbol} - Comparison: Linear vs Monte Carlo Projection', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to: {save_path}")
    plt.close()


def main():
    """
    Main demo function comparing old and new methods.
    """
    print("=" * 80)
    print("MONTE CARLO SIMULATION DEMO")
    print("=" * 80)
    
    # Test with multiple assets
    symbols = ['SOXS', 'IVV', 'TLT']
    
    for symbol in symbols:
        try:
            print(f"\n{'=' * 80}")
            print(f"Testing with {symbol}")
            print("=" * 80)
            
            # Load data
            csv_path = Path('assets') / f'{symbol}.csv'
            if not csv_path.exists():
                print(f"Skipping {symbol} - data file not found")
                continue
            
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Use last 100 days for projection
            df_recent = df.tail(100)
            
            print(f"\nHistorical data:")
            print(f"  Total points: {len(df)}")
            print(f"  Using recent: {len(df_recent)} days")
            print(f"  Date range: {df_recent.iloc[0]['Date'].date()} to {df_recent.iloc[-1]['Date'].date()}")
            print(f"  Last price: ${df_recent.iloc[-1]['Close']:.2f}")
            
            # Calculate historical volatility
            log_returns = (df_recent['Close'] / df_recent['Close'].shift(1)).apply(np.log).dropna()
            volatility_annual = log_returns.std() * np.sqrt(252)
            print(f"  Annualized volatility: {volatility_annual*100:.2f}%")
            
            # Generate projections (30 days)
            num_days = 30
            print(f"\nGenerating {num_days}-day projections...")
            
            # Old method
            df_linear = old_linear_projection(df_recent, num_days)
            
            # New method
            df_mc = monte_carlo_gbm(df_recent, num_days, simulations=1000)
            
            # Compare results
            print("\n" + "-" * 80)
            print("COMPARISON RESULTS (30-day projection)")
            print("-" * 80)
            
            linear_price = df_linear.iloc[-1]['Close']
            mc_mean = df_mc.iloc[-1]['Close']
            mc_median = df_mc.iloc[-1]['Median']
            mc_lower = df_mc.iloc[-1]['Lower90']
            mc_upper = df_mc.iloc[-1]['Upper90']
            mc_std = df_mc.iloc[-1]['StdDev']
            
            current_price = df_recent.iloc[-1]['Close']
            
            print(f"\nCurrent Price:              ${current_price:.2f}")
            print(f"\nOLD METHOD (Linear):")
            print(f"  Projected price:          ${linear_price:.2f}")
            print(f"  Change:                   ${linear_price - current_price:.2f} ({(linear_price/current_price - 1)*100:+.2f}%)")
            
            print(f"\nNEW METHOD (Monte Carlo GBM):")
            print(f"  Mean projected price:     ${mc_mean:.2f}")
            print(f"  Median projected price:   ${mc_median:.2f}")
            print(f"  Change (mean):            ${mc_mean - current_price:.2f} ({(mc_mean/current_price - 1)*100:+.2f}%)")
            print(f"  Standard deviation:       ${mc_std:.2f}")
            print(f"  90% Confidence Interval:  [${mc_lower:.2f}, ${mc_upper:.2f}]")
            print(f"  Range width:              ${mc_upper - mc_lower:.2f}")
            
            # Analyze uncertainty
            uncertainty_pct = ((mc_upper - mc_lower) / mc_mean) * 100
            print(f"\nUncertainty Analysis:")
            print(f"  Confidence interval as % of mean: {uncertainty_pct:.1f}%")
            print(f"  Upside potential:         ${mc_upper - current_price:.2f} ({(mc_upper/current_price - 1)*100:+.2f}%)")
            print(f"  Downside risk:            ${mc_lower - current_price:.2f} ({(mc_lower/current_price - 1)*100:+.2f}%)")
            
            # Create visualization
            print("\nGenerating visualization...")
            save_path = f'monte_carlo_{symbol}.png'
            visualize_comparison(df_recent, df_linear, df_mc, symbol, save_path)
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("KEY ADVANTAGES OF MONTE CARLO SIMULATION:")
    print("=" * 80)
    print("✅ Provides confidence intervals (quantifies uncertainty)")
    print("✅ Uses Geometric Brownian Motion (industry standard)")
    print("✅ Accounts for volatility drag")
    print("✅ Cannot generate negative prices")
    print("✅ More realistic for financial modeling")
    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
