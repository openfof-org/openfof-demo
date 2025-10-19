# Quick Start: Monte Carlo Simulation

## What Changed?

The API now uses **Monte Carlo simulation with Geometric Brownian Motion** for future price projections instead of simple linear trends.

## What This Means

- ✅ **More accurate**: Uses industry-standard financial modeling
- ✅ **Shows uncertainty**: Provides confidence intervals
- ✅ **Realistic**: Accounts for volatility and cannot produce negative prices
- ✅ **Professional**: Same technique used by quant finance firms

## How to Use

### 1. Standard API Usage (No Changes Required!)

The API endpoints work exactly the same way. The Monte Carlo simulation is automatically applied:

```bash
curl -X POST http://localhost:5000/api/portfolio \
  -H 'Content-Type: application/json' \
  -d '{
    "assetIds": ["asset-001", "asset-002"],
    "timeRange": "1Y"
  }'
```

### 2. Response Structure

The response is the same, but the `future` array now contains more sophisticated Monte Carlo-generated predictions:

```json
{
  "historical": [...],
  "future": [
    {
      "date": "2025-11-01",
      "SOXS": 3.45,
      "BITQ": 12.34,
      "average": 7.90
    },
    ...
  ],
  "stats": {
    "volatility": 0.45,
    "netProfit": 123.45,
    "netProfitPercent": 12.34,
    "predictedProfit1Y": 45.67
  },
  "assetColors": {...}
}
```

## Testing the Implementation

### Quick Test

```bash
# 1. Start the server
python api_server.py

# 2. In another terminal, test it
python test_monte_carlo_api.py
```

### See the Comparison

Run the demo to compare old linear method vs new Monte Carlo:

```bash
python demo_monte_carlo.py
```

This will:
- Test with SOXS, IVV, and TLT
- Show confidence intervals
- Generate comparison charts (PNG files)
- Display uncertainty analysis

### Example Output

```
Testing with SOXS
--------------------------------------------------------------------------------
Current Price:              $4.06

NEW METHOD (Monte Carlo GBM):
  Mean projected price:     $2.90
  Median projected price:   $2.76
  Standard deviation:       $0.81
  90% Confidence Interval:  [$1.79, $4.32]

Uncertainty Analysis:
  Upside potential:         $0.26 (+6.47%)
  Downside risk:            $-2.27 (-55.96%)
```

## Key Features

### 1. Geometric Brownian Motion (GBM)
- Mathematical formula: `S(t+1) = S(t) × exp((μ - 0.5σ²) + σZ)`
- Prevents negative prices
- Accounts for volatility drag

### 2. Monte Carlo Simulation
- Runs 1,000 independent simulations
- Each starts from last known price
- Uses random shocks to model uncertainty
- Aggregates results for mean, median, and confidence intervals

### 3. Confidence Intervals
- 90% confidence interval (5th to 95th percentile)
- Shows range where price is expected to fall 90% of the time
- Wider for high-volatility assets, narrower for stable assets

## Technical Details

### Parameters
- **Simulations**: 1,000 (provides good statistical stability)
- **Model**: Geometric Brownian Motion
- **Returns**: Log returns (mathematically correct)
- **Drift adjustment**: Includes volatility drag (0.5σ²)

### Performance
- Typical runtime: 0.1-0.5 seconds for 1000 simulations × 90 days
- Memory efficient: Uses numpy arrays
- No external API calls

## Understanding the Results

### Volatility Impact

**Low volatility asset** (e.g., IVV - S&P 500 ETF):
- Narrow confidence interval (~10% of mean)
- More predictable
- Smaller price swings

**High volatility asset** (e.g., SOXS - Leveraged ETF):
- Wide confidence interval (~87% of mean)
- Less predictable
- Larger potential swings

### Interpreting Predictions

The projection is a **probability distribution**, not a single answer:

- **Mean**: Average outcome across all simulations
- **Median**: Middle value (50th percentile)
- **90% CI**: Where the price will likely be 90% of the time
- **Upside/Downside**: Potential gains and losses

## Documentation

- **`MONTE_CARLO_IMPLEMENTATION.md`**: Full technical documentation
- **`MONTE_CARLO_SUMMARY.md`**: Complete implementation summary
- **`demo_monte_carlo.py`**: Comparison demo script
- **`test_monte_carlo_api.py`**: API integration tests

## Troubleshooting

### "Module not found" errors
Make sure you're in the virtual environment:
```bash
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Need help?
Check the detailed documentation in `MONTE_CARLO_IMPLEMENTATION.md`

## Summary

🎯 **The Bottom Line**: Your API now uses professional-grade financial modeling for predictions, with confidence intervals that show the range of possible outcomes. No changes needed to your API calls - it just works better!
