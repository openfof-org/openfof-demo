# OpenFOF Asset Management REST API

A REST API server for searching and managing asset information (stocks, ETFs, cryptocurrencies, etc.).

## Features

- **Asset Search**: Search for assets by symbol or name with case-insensitive partial matching
- **Pagination**: Support for paginated results to handle large datasets
- **Multiple Endpoints**: Get all assets, search, or retrieve specific assets by ID or symbol
- **Error Handling**: Comprehensive error responses with helpful messages

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the API server:
```bash
python api_server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Search Assets
**Endpoint**: `GET /api/assets/search`

**Description**: Search for available assets by symbol or name.

**Query Parameters**:
- `q` (string, required): Search query string
- `page` (int, optional): Page number for pagination (default: 1)
- `page_size` (int, optional): Number of results per page (default: 10, max: 100)

**Example Requests**:
```bash
# Search for assets containing "ETF"
curl 'http://localhost:5000/api/assets/search?q=ETF'

# Search with pagination
curl 'http://localhost:5000/api/assets/search?q=S&page=1&page_size=3'

# Search for "SOXS"
curl 'http://localhost:5000/api/assets/search?q=SOXS'
```

**Example Response** (without pagination):
```json
[
  {
    "id": "asset-001",
    "symbol": "BITQ",
    "name": "Bitwise Crypto Industry Innovators ETF",
    "type": "crypto_etf",
    "description": "ETF tracking companies that support or benefit from crypto and blockchain technology"
  },
  {
    "id": "asset-002",
    "symbol": "GDX",
    "name": "VanEck Gold Miners ETF",
    "type": "commodity_etf",
    "description": "ETF tracking gold mining companies"
  }
]
```

**Example Response** (with pagination):
```json
{
  "data": [
    {
      "id": "asset-001",
      "symbol": "BITQ",
      "name": "Bitwise Crypto Industry Innovators ETF",
      "type": "crypto_etf",
      "description": "ETF tracking companies that support or benefit from crypto and blockchain technology"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 3,
    "total_items": 8,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2. Get All Assets
**Endpoint**: `GET /api/assets`

**Description**: Retrieve all available assets.

**Query Parameters**:
- `page` (int, optional): Page number for pagination
- `page_size` (int, optional): Number of results per page (default: 10, max: 100)

**Example Request**:
```bash
curl 'http://localhost:5000/api/assets'
```

### 3. Get Asset by ID
**Endpoint**: `GET /api/assets/<asset_id>`

**Description**: Retrieve a specific asset by its unique ID.

**Example Request**:
```bash
curl 'http://localhost:5000/api/assets/asset-001'
```

**Example Response**:
```json
{
  "id": "asset-001",
  "symbol": "BITQ",
  "name": "Bitwise Crypto Industry Innovators ETF",
  "type": "crypto_etf",
  "description": "ETF tracking companies that support or benefit from crypto and blockchain technology"
}
```

### 4. Get Asset by Symbol
**Endpoint**: `GET /api/assets/symbol/<symbol>`

**Description**: Retrieve a specific asset by its ticker symbol.

**Example Request**:
```bash
curl 'http://localhost:5000/api/assets/symbol/SOXS'
```

### 5. Health Check
**Endpoint**: `GET /api/health`

**Description**: Verify the API is running.

**Example Request**:
```bash
curl 'http://localhost:5000/api/health'
```

## Asset Data Model

```typescript
interface Asset {
  id: string;           // Unique identifier (e.g., "asset-001")
  symbol: string;       // Ticker symbol (e.g., "AAPL", "SOXS")
  name: string;         // Full asset name
  type: string;         // Asset type (e.g., "equity_etf", "crypto_etf")
  description: string;  // Brief description of the asset
}
```

## Search Behavior

- **Case-insensitive**: Searches match regardless of case (e.g., "etf", "ETF", "Etf" all work)
- **Partial matching**: Searches match substrings (e.g., "SOX" matches "SOXS")
- **Multi-field**: Searches check both symbol and name fields
- **No wildcards needed**: Just type your search term naturally

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required query parameter 'q'",
  "message": "Please provide a search query using the 'q' parameter"
}
```

### 404 Not Found
```json
{
  "error": "Asset not found",
  "message": "No asset found with ID: asset-999"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Current Assets

The API currently includes the following assets:

1. **BITQ** - Bitwise Crypto Industry Innovators ETF
2. **GDX** - VanEck Gold Miners ETF
3. **RSBT** - RiverNorth Specialty Finance Corporation
4. **SOXS** - Direxion Daily Semiconductor Bear 3X Shares
5. **SPPIX** - SP Funds S&P 500 Sharia Industry Exclusions ETF
6. **SQQQ** - ProShares UltraPro Short QQQ
7. **TLT** - iShares 20+ Year Treasury Bond ETF
8. **S&P500** - S&P 500 Index

## Development

### Adding New Assets

To add new assets, edit `assets_metadata.py` and add entries to the `ASSETS_METADATA` list:

```python
{
    "id": "asset-XXX",
    "symbol": "TICKER",
    "name": "Full Asset Name",
    "type": "asset_type",
    "description": "Brief description"
}
```

### Running in Production

For production deployment, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

## Testing Examples

Here are some test queries to try:

```bash
# Search for semiconductor-related assets
curl 'http://localhost:5000/api/assets/search?q=semiconductor'

# Search for "S" (will match SOXS, SQQQ, SPPIX, S&P500, etc.)
curl 'http://localhost:5000/api/assets/search?q=S'

# Search for ETFs
curl 'http://localhost:5000/api/assets/search?q=ETF'

# Get a specific asset
curl 'http://localhost:5000/api/assets/asset-004'

# Get asset by symbol
curl 'http://localhost:5000/api/assets/symbol/TLT'

# Search with pagination
curl 'http://localhost:5000/api/assets/search?q=E&page=1&page_size=2'
```
