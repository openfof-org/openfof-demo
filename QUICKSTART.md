# Quick Start Guide - OpenFOF Asset Management API

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python api_server.py
```

The server will start on `http://localhost:5000`

### 3. Test the API

#### Option A: Using curl (Command Line)
```bash
# Search for assets containing "ETF"
curl 'http://localhost:5000/api/assets/search?q=ETF'

# Search for a specific symbol
curl 'http://localhost:5000/api/assets/search?q=SOXS'

# Get all assets
curl 'http://localhost:5000/api/assets'

# Get a specific asset by ID
curl 'http://localhost:5000/api/assets/asset-001'

# Health check
curl 'http://localhost:5000/api/health'
```

#### Option B: Using the Python Test Script
```bash
# In a new terminal (while server is running)
python test_api.py
```

#### Option C: Using a Web Browser
Open your browser and navigate to:
- http://localhost:5000/api/health
- http://localhost:5000/api/assets/search?q=ETF
- http://localhost:5000/api/assets

#### Option D: Demo Without Server
Run the search functionality demo (no server needed):
```bash
python demo_search.py
```

## 📋 Example API Calls

### Search for assets (case-insensitive, partial matching)
```bash
# Find all ETFs
curl 'http://localhost:5000/api/assets/search?q=ETF'

# Find assets with "S" in symbol or name
curl 'http://localhost:5000/api/assets/search?q=S'

# Find semiconductor-related assets
curl 'http://localhost:5000/api/assets/search?q=semiconductor'
```

### Search with Pagination
```bash
# Get first page (2 items per page)
curl 'http://localhost:5000/api/assets/search?q=E&page=1&page_size=2'

# Get second page
curl 'http://localhost:5000/api/assets/search?q=E&page=2&page_size=2'
```

### Get Specific Assets
```bash
# By ID
curl 'http://localhost:5000/api/assets/asset-004'

# By Symbol
curl 'http://localhost:5000/api/assets/symbol/SOXS'
curl 'http://localhost:5000/api/assets/symbol/tlt'  # Case-insensitive
```

## 🎯 Key Features

✅ **Case-Insensitive Search** - Search for "etf", "ETF", or "Etf"  
✅ **Partial Matching** - "SOX" finds "SOXS"  
✅ **Multi-Field Search** - Searches both symbol and name  
✅ **Pagination Support** - Handle large result sets  
✅ **RESTful Design** - Standard HTTP methods and status codes  
✅ **Error Handling** - Clear error messages  

## 📚 Available Assets

The API currently includes 8 assets:

| Symbol | Name | Type |
|--------|------|------|
| BITQ | Bitwise Crypto Industry Innovators ETF | crypto_etf |
| GDX | VanEck Gold Miners ETF | commodity_etf |
| RSBT | RiverNorth Specialty Finance Corporation | closed_end_fund |
| SOXS | Direxion Daily Semiconductor Bear 3X Shares | leveraged_etf |
| SPPIX | SP Funds S&P 500 Sharia Industry Exclusions ETF | equity_etf |
| SQQQ | ProShares UltraPro Short QQQ | leveraged_etf |
| TLT | iShares 20+ Year Treasury Bond ETF | bond_etf |
| S&P500 | S&P 500 Index | index |

## 🔧 Troubleshooting

### Port Already in Use?
If port 5000 is already in use, edit `api_server.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to a different port, e.g., `port=8000`

### Server Not Responding?
Make sure Flask is installed:
```bash
pip install flask
```

### Need More Details?
See `README_API.md` for complete API documentation.

## 📖 Next Steps

- Read the full API documentation: `README_API.md`
- Explore the code: `api_server.py` and `assets_metadata.py`
- Run comprehensive tests: `python test_api.py`
- Add more assets: Edit `assets_metadata.py`

## 💡 Tips

- Use Postman or Insomnia for more advanced API testing
- Enable pretty-printing in curl: `curl ... | python -m json.tool`
- Check server logs for debugging information
- The demo script (`demo_search.py`) shows search logic without needing the server
