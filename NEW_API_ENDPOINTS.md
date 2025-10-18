# New API Endpoints Documentation

This document describes the newly implemented API endpoints for portfolio analysis, correlation groups, heatmaps, and diversification recommendations.

## Table of Contents
- [Portfolio Data](#1-portfolio-data)
- [Correlation Groups](#2-correlation-groups)
- [Heatmap Data](#3-heatmap-data)
- [Diversification Recommendations](#4-diversification-recommendations)

---

## 1. Portfolio Data

### Endpoint
```
POST /api/portfolio
```

### Description
Retrieve historical and projected future performance data for a portfolio of assets.

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "assetIds": ["string"],      // Array of asset IDs
  "timeRange": "TimeRange"     // Time period for historical data
}
```

**TimeRange Options:**
- `1D`: 1 day
- `5D`: 5 days
- `1M`: 30 days
- `6M`: 180 days
- `1Y`: 365 days
- `5Y`: 1825 days
- `MAX`: 3650 days (10 years)

### Response
```typescript
interface PortfolioData {
  historical: DataPoint[];
  future: DataPoint[];
  stats: {
    volatility: number;
    netProfit: number;
    netProfitPercent: number;
    predictedProfit1Y: number;
    correlation?: number;  // Only present if multiple assets
  };
  assetColors: Record<string, string>;  // Map of symbol to color hex code
}

interface DataPoint {
  date: string;              // ISO date string
  [assetSymbol: string]: number | string;  // Dynamic keys for each asset
  average?: number;          // Average value across all assets
}
```

### Example Request
```bash
curl -X POST http://localhost:5000/api/portfolio \
  -H 'Content-Type: application/json' \
  -d '{
    "assetIds": ["asset-002", "asset-011"],
    "timeRange": "1Y"
  }'
```

### Example Response
```json
{
  "historical": [
    {
      "date": "2024-10-18T16:00:00",
      "BITQ": 15.47,
      "IVV": 587.46,
      "average": 301.465
    },
    {
      "date": "2024-10-21T16:00:00",
      "BITQ": 15.7,
      "IVV": 588.12,
      "average": 301.91
    }
  ],
  "future": [
    {
      "date": "2025-10-18T16:00:00",
      "BITQ": 16.23,
      "IVV": 612.45,
      "average": 314.34
    }
  ],
  "stats": {
    "volatility": 0.4107,
    "netProfit": -559.43,
    "netProfitPercent": -95.23,
    "predictedProfit1Y": 10.07,
    "correlation": 0.61
  },
  "assetColors": {
    "BITQ": "#ef4444",
    "IVV": "#06b6d4",
    "average": "#a855f7"
  }
}
```

### Implementation Details
- Historical data is loaded from CSV files in the `assets/` directory
- Future projections use Monte Carlo simulation (1000 simulations by default)
- Future projections are limited to max 90 days or half the selected period (whichever is smaller)
- Volatility is calculated using annualized standard deviation
- Correlation is only calculated when multiple assets are present
- Colors are generated deterministically based on symbol hash (ensures consistency)
- Purple (#a855f7) is reserved for the average line

---

## 2. Correlation Groups

### Endpoint
```
POST /api/correlation-groups
```

### Description
Retrieve groups of assets that are correlated with the portfolio assets, grouped by asset type.

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "assetIds": ["string"]  // Array of asset IDs from the portfolio
}
```

### Response
```typescript
interface CorrelationGroupType {
  id: string;
  name: string;
  assetIds: string[];
  correlationScore: number;  // Value between 0 and 1
}
```

### Example Request
```bash
curl -X POST http://localhost:5000/api/correlation-groups \
  -H 'Content-Type: application/json' \
  -d '{
    "assetIds": ["asset-002", "asset-011"]
  }'
```

### Example Response
```json
[
  {
    "id": "group-001",
    "name": "Equity ETFs",
    "assetIds": ["asset-001", "asset-005", "asset-009", "asset-011", "asset-013", "asset-016", "asset-018", "asset-019", "asset-020", "asset-022", "asset-028"],
    "correlationScore": 0.64
  },
  {
    "id": "group-002",
    "name": "Crypto ETFs",
    "assetIds": ["asset-002"],
    "correlationScore": 0.8
  }
]
```

### Implementation Details
- Groups assets by type (equity_etf, bond_etf, commodity_etf, etc.)
- Only includes groups containing at least one portfolio asset
- Correlation scores are calculated as average correlation with portfolio assets
- Groups are sorted by correlation score (descending)
- Uses Pearson correlation coefficient on historical returns

---

## 3. Heatmap Data

### Endpoint
```
POST /api/heatmap
```

### Description
Generate correlation heatmap data showing relationships between portfolio assets.

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "assetIds": ["string"]  // Array of asset IDs
}
```

### Response
```typescript
interface HeatmapData {
  labels: string[];          // Asset symbols
  data: number[][];         // 2D correlation matrix
}
```

### Example Request
```bash
curl -X POST http://localhost:5000/api/heatmap \
  -H 'Content-Type: application/json' \
  -d '{
    "assetIds": ["asset-002", "asset-011", "asset-025"]
  }'
```

### Example Response
```json
{
  "labels": ["BITQ", "IVV", "TLT"],
  "data": [
    [1.00, 0.61, -0.06],
    [0.61, 1.00, 0.08],
    [-0.06, 0.08, 1.00]
  ]
}
```

### Implementation Details
- Correlation matrix is symmetric: `data[i][j] === data[j][i]`
- Diagonal values are always 1.00 (perfect correlation with itself)
- Values range from -1 (perfect negative correlation) to 1 (perfect positive correlation)
- Uses Pearson correlation coefficient on historical returns
- Order of labels matches the order of rows/columns in the data matrix

---

## 4. Diversification Recommendations

### Endpoint
```
POST /api/diversify
```

### Description
Get recommendations for assets that would improve portfolio diversification.

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "assetIds": ["string"]  // Current portfolio asset IDs
}
```

### Response
```typescript
interface DiversifyAsset {
  id: string;
  symbol: string;
  name: string;
  reason: string;           // Why this asset would improve diversification
  correlationScore: number; // How correlated it is with current portfolio
  expectedImprovement: number;  // Estimated improvement metric (percentage)
}
```

### Example Request
```bash
curl -X POST http://localhost:5000/api/diversify \
  -H 'Content-Type: application/json' \
  -d '{
    "assetIds": ["asset-011", "asset-016"]
  }'
```

### Example Response
```json
[
  {
    "id": "asset-023",
    "symbol": "SQQQ",
    "name": "ProShares UltraPro Short QQQ",
    "reason": "Different asset class (leveraged etf), very low correlation with current portfolio provides strong diversification",
    "correlationScore": -0.97,
    "expectedImprovement": 35.0
  },
  {
    "id": "asset-017",
    "symbol": "SOXS",
    "name": "Direxion Daily Semiconductor Bear 3X Shares",
    "reason": "Different asset class (leveraged etf), very low correlation with current portfolio provides strong diversification",
    "correlationScore": -0.86,
    "expectedImprovement": 35.0
  },
  {
    "id": "asset-031",
    "symbol": "VGSH",
    "name": "Vanguard Short-Term Treasury ETF",
    "reason": "Different asset class (bond etf), very low correlation with current portfolio provides strong diversification",
    "correlationScore": -0.22,
    "expectedImprovement": 35.0
  }
]
```

### Implementation Details
- Recommends assets with low correlation to existing portfolio
- Considers different asset classes, sectors, and types
- Provides clear explanations for each recommendation
- Limited to top 10 recommendations
- Excludes assets already in the portfolio
- Scoring criteria:
  - Different asset type: +15% expected improvement
  - Correlation < 0.3: +20% expected improvement
  - Correlation < 0.5: +12% expected improvement
  - Correlation < 0.7: +5% expected improvement
- Sorted by expected improvement (descending), then by correlation (ascending)
- Response time typically < 1 second

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Asset not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### Common Errors

**Missing Request Body**
```json
{
  "error": "Request body is required"
}
```

**Invalid Asset ID**
```json
{
  "error": "Asset not found: asset-999"
}
```

**Invalid Time Range**
```json
{
  "error": "Invalid timeRange. Must be one of: ['1D', '5D', '1M', '6M', '1Y', '5Y', 'MAX']"
}
```

---

## Testing

A test script is provided to verify all endpoints:

```bash
python test_new_apis.py
```

This will test:
- Portfolio data retrieval
- Correlation groups
- Heatmap generation
- Diversification recommendations
- Error handling

---

## Technical Notes

### Dependencies
- Flask: Web framework
- pandas: Data manipulation
- numpy: Numerical operations
- Custom modules:
  - `assets_metadata`: Asset information
  - `libs/assetstats`: Statistical calculations
  - `libs/correlations`: Correlation analysis

### Data Sources
- Historical price data: CSV files in `assets/` directory
- Asset metadata: `assets_metadata.py`

### Performance Considerations
- Correlation calculations are cached during request processing
- Monte Carlo simulations use 1000 iterations by default
- Future projections are limited to prevent excessive computation
- All responses are JSON-encoded for efficient transfer

### Color Scheme
The API uses a consistent color palette for asset visualization:
- Assets: Generated using MD5 hash of symbol (12 colors in rotation)
- Average: Reserved purple (#a855f7)
- Colors are deterministic (same symbol always gets same color)
