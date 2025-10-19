# Monte Carlo Simulation Implementation

## Overview

The future price projection system has been upgraded from a simple linear model to a sophisticated **Monte Carlo simulation using Geometric Brownian Motion (GBM)**. This provides more realistic and statistically sound forecasts for asset prices.

## What Changed

### Previous Implementation (Simple Normal Distribution)
The old implementation used a basic approach:
- Calculated mean and standard deviation of daily percentage returns
- Generated random returns from a normal distribution
- Applied returns sequentially: `price = price * (1 + random_return)`
- **Problems:**
  - Could generate negative prices
  - Didn't account for volatility drag
  - Oversimplified the stochastic nature of asset prices

### New Implementation (Geometric Brownian Motion)
The enhanced implementation uses GBM, the industry-standard model for asset prices:
- Uses **log returns** instead of simple returns (more mathematically appropriate)
- Implements the GBM formula: `S(t) = S(0) * exp((μ - 0.5σ²)t + σ√t·Z)`
- Where:
  - μ (mu) = drift (expected return)
  - σ (sigma) = volatility (standard deviation of log returns)
  - Z = random shock from standard normal distribution
  - The term `(μ - 0.5σ²)` is the **risk-neutral drift** that accounts for volatility drag

**Advantages:**
- ✅ Prices are always positive (due to exponential function)
- ✅ Captures the multiplicative nature of returns
- ✅ Accounts for volatility drag (higher volatility reduces expected returns)
- ✅ Standard model used in quantitative finance (Black-Scholes, etc.)

## Monte Carlo Simulation Features

### 1. Multiple Simulations (Default: 1000)
- Runs 1,000 independent price path simulations
- Each simulation starts from the last historical price
- Uses random shocks to model uncertainty
- Provides statistical distribution of possible outcomes

### 2. Confidence Intervals
The simulation now returns:
- **Mean price**: Average across all simulations
- **Median price**: Middle value (50th percentile)
- **Standard deviation**: Measure of uncertainty
- **90% confidence interval**: Range where the price is expected to fall 90% of the time
  - Lower bound: 5th percentile
  - Upper bound: 95th percentile

### 3. Enhanced Output
```python
{
    'Date': future_dates,           # Array of future dates
    'Close': mean_prices,            # Mean projected price (average)
    'Median': median_prices,         # Median projected price
    'StdDev': std_prices,            # Standard deviation at each point
    'Lower90': lower_bound,          # Lower 90% confidence bound (5th percentile)
    'Upper90': upper_bound           # Upper 90% confidence bound (95th percentile)
}
```

## Mathematical Details

### Geometric Brownian Motion Formula
For each day in the simulation:

```
price(t+1) = price(t) * exp(drift + diffusion)
```

Where:
- **drift** = (μ - 0.5σ²)
  - μ = mean of log returns
  - σ² = variance of log returns
  - The 0.5σ² term is the **Itô correction** (volatility drag)
  
- **diffusion** = σ * Z
  - σ = standard deviation of log returns
  - Z = random value from standard normal distribution N(0,1)

### Why Log Returns?
Log returns have several advantages:
1. **Symmetry**: A +10% return followed by -10% return results in a net loss with simple returns, but log returns are symmetric
2. **Additivity**: Log returns can be summed: log(P₂/P₀) = log(P₂/P₁) + log(P₁/P₀)
3. **Normality**: Log returns are more likely to be normally distributed than simple returns
4. **Mathematical convenience**: Works naturally with exponential growth models

### Volatility Drag
The term `0.5σ²` in the drift adjustment represents volatility drag:
- Higher volatility leads to lower geometric mean returns
- This is a mathematical consequence of Jensen's inequality
- Example: If you lose 50% one day and gain 50% the next, you end up with less than you started (not break-even)

## Code Example

```python
# Historical log returns
log_returns = (df['Close'] / df['Close'].shift(1)).apply(np.log).dropna()

# Calculate parameters
mu = log_returns.mean()      # Drift
sigma = log_returns.std()    # Volatility

# Monte Carlo simulation
for sim in range(1000):
    price = last_price
    for day in range(num_days):
        # Generate random shock
        Z = np.random.standard_normal()
        
        # Apply GBM formula
        drift = (mu - 0.5 * sigma ** 2)
        diffusion = sigma * Z
        price = price * np.exp(drift + diffusion)
```

## API Integration

The enhanced simulation is automatically used in the `/api/portfolio` endpoint:

```bash
curl -X POST http://localhost:5000/api/portfolio \
  -H 'Content-Type: application/json' \
  -d '{
    "assetIds": ["asset-001", "asset-002"],
    "timeRange": "1Y"
  }'
```

The response includes:
- `historical`: Historical price data
- `future`: Projected future prices (using Monte Carlo simulation)
- `stats`: Portfolio statistics including predicted profit based on simulations

## Performance Characteristics

### Simulation Parameters
- **Default simulations**: 1,000 paths
- **Typical projection period**: 30-90 days
- **Performance**: ~0.1-0.5 seconds for 1000 simulations × 90 days

### Accuracy Considerations
- More simulations → More accurate statistics (but slower)
- 1,000 simulations provides good balance of speed and accuracy
- Confidence intervals widen as projection period increases (reflects growing uncertainty)

## Comparison: Old vs New

| Aspect | Old Method | New Method (GBM) |
|--------|-----------|------------------|
| Model | Simple normal returns | Geometric Brownian Motion |
| Can generate negative prices? | Yes ❌ | No ✅ |
| Accounts for volatility drag? | No ❌ | Yes ✅ |
| Industry standard? | No ❌ | Yes ✅ |
| Confidence intervals? | No ❌ | Yes (5th-95th percentile) ✅ |
| Statistical rigor | Low | High |
| Suitable for finance? | No | Yes ✅ |

## Limitations & Considerations

While this implementation is significantly more robust, it's important to understand its limitations:

1. **Assumes constant volatility**: GBM assumes σ is constant, but real markets have time-varying volatility
2. **Assumes log-normal returns**: Real returns may have fat tails and skewness
3. **No structural breaks**: Doesn't account for regime changes, black swan events
4. **No mean reversion**: Asset prices can trend away from fundamentals
5. **Historical parameters**: Uses historical μ and σ, which may not predict future behavior

## Best Practices

1. **Use for relative comparison**: Better for comparing scenarios than absolute predictions
2. **Consider confidence intervals**: Don't rely solely on mean projections
3. **Shorter horizons more reliable**: Uncertainty grows with time
4. **Complement with other analysis**: Use alongside fundamental and technical analysis
5. **Regular recalibration**: Update projections as new data arrives

## References

- Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
- Hull, J. C. (2018). "Options, Futures, and Other Derivatives"
- Wilmott, P. (2006). "Paul Wilmott on Quantitative Finance"

## Future Enhancements

Potential improvements to consider:
- **GARCH models**: Time-varying volatility
- **Jump-diffusion**: Account for sudden price movements
- **Mean reversion**: For assets that tend to revert to a mean
- **Correlated simulations**: Simulate multiple assets with correlation
- **Historical simulation**: Bootstrap from actual historical scenarios
- **Stochastic volatility**: Models like Heston where volatility itself is random
