"""
REST API Server for OpenFOF Asset Management Demo
Provides endpoints for searching and retrieving asset information.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from assets_metadata import (
    search_assets, get_all_assets, get_asset_by_id, get_asset_by_symbol,
    get_symbol_for_asset_id, generate_color_for_symbol, ASSETS_METADATA
)
from libs.assetstats import get_percentage_change, get_volatility
from libs.correlations import load_prices_from_csvs, returns_corr
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

app = Flask(__name__)

# Time range to days mapping
TIME_RANGE_DAYS = {
    '1D': 1,
    '5D': 5,
    '1M': 30,
    '6M': 180,
    '1Y': 365,
    '5Y': 1825,
    'MAX': 3650
}
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

def paginate_results(results: List[Dict], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    Paginate a list of results.
    
    Args:
        results: List of items to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        Dictionary with paginated data and metadata
    """
    total_items = len(results)
    total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    # Calculate start and end indices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Get the slice of results for this page
    page_results = results[start_idx:end_idx]
    
    return {
        "data": page_results,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


@app.route('/api/assets/search', methods=['GET'])
def search_assets_endpoint():
    """
    Search for available assets by symbol or name.
    
    Query Parameters:
        q (string, required): Search query string
        page (int, optional): Page number for pagination (default: 1)
        page_size (int, optional): Number of results per page (default: 10, max: 100)
    
    Returns:
        JSON response with array of matching Asset objects or paginated results
    
    Example:
        GET /api/assets/search?q=AAPL
        GET /api/assets/search?q=ETF&page=1&page_size=5
    """
    # Get query parameter
    query = request.args.get('q', '').strip()
    
    # Validate required parameter
    if not query:
        return jsonify({
            "error": "Missing required query parameter 'q'",
            "message": "Please provide a search query using the 'q' parameter"
        }), 400
    
    # Get pagination parameters
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100
            
    except ValueError:
        return jsonify({
            "error": "Invalid pagination parameters",
            "message": "Page and page_size must be valid integers"
        }), 400
    
    # Perform the search
    results = search_assets(query)
    
    # Check if pagination is requested (if page or page_size is specified)
    use_pagination = 'page' in request.args or 'page_size' in request.args
    
    if use_pagination:
        # Return paginated results
        return jsonify(paginate_results(results, page, page_size))
    else:
        # Return all results without pagination
        return jsonify(results)


@app.route('/api/assets', methods=['GET'])
def get_all_assets_endpoint():
    """
    Get all available assets.
    
    Query Parameters:
        page (int, optional): Page number for pagination
        page_size (int, optional): Number of results per page (default: 10, max: 100)
    
    Returns:
        JSON response with array of all Asset objects or paginated results
    """
    # Get pagination parameters
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100
            
    except ValueError:
        return jsonify({
            "error": "Invalid pagination parameters",
            "message": "Page and page_size must be valid integers"
        }), 400
    
    results = get_all_assets()
    
    # Check if pagination is requested
    use_pagination = 'page' in request.args or 'page_size' in request.args
    
    if use_pagination:
        return jsonify(paginate_results(results, page, page_size))
    else:
        return jsonify(results)


@app.route('/api/assets/<asset_id>', methods=['GET'])
def get_asset_by_id_endpoint(asset_id: str):
    """
    Get a specific asset by its ID.
    
    Path Parameters:
        asset_id: The unique asset identifier
    
    Returns:
        JSON response with Asset object or 404 if not found
    
    Example:
        GET /api/assets/asset-001
    """
    asset = get_asset_by_id(asset_id)
    
    if asset is None:
        return jsonify({
            "error": "Asset not found",
            "message": f"No asset found with ID: {asset_id}"
        }), 404
    
    return jsonify(asset)


@app.route('/api/assets/symbol/<symbol>', methods=['GET'])
def get_asset_by_symbol_endpoint(symbol: str):
    """
    Get a specific asset by its symbol.
    
    Path Parameters:
        symbol: The asset ticker symbol
    
    Returns:
        JSON response with Asset object or 404 if not found
    
    Example:
        GET /api/assets/symbol/SOXS
    """
    asset = get_asset_by_symbol(symbol)
    
    if asset is None:
        return jsonify({
            "error": "Asset not found",
            "message": f"No asset found with symbol: {symbol}"
        }), 404
    
    return jsonify(asset)


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        JSON response with status information
    """
    return jsonify({
        "status": "healthy",
        "service": "OpenFOF Asset API",
        "version": "1.0.0"
    })


def load_asset_data(symbol: str, days: int) -> pd.DataFrame:
    """
    Load historical price data for an asset.
    
    Args:
        symbol: Asset ticker symbol
        days: Number of days of historical data to load
    
    Returns:
        DataFrame with Date and Close columns
    """
    csv_path = Path('assets') / f'{symbol}.csv'
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found for symbol: {symbol}")
    
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Get the most recent date and filter by days
    if len(df) > 0:
        most_recent = df.iloc[-1]['Date']
        cutoff_date = most_recent - timedelta(days=days)
        df = df[df['Date'] >= cutoff_date]
    
    return df


def generate_future_projections(df: pd.DataFrame, symbol: str, num_days: int, simulations: int = 1000) -> pd.DataFrame:
    """
    Generate future price projections using Monte Carlo simulation.
    
    Args:
        df: Historical price DataFrame
        symbol: Asset symbol
        num_days: Number of days to project
        simulations: Number of Monte Carlo simulations
    
    Returns:
        DataFrame with projected dates and prices
    """
    if len(df) < 2:
        return pd.DataFrame()
    
    # Calculate daily returns
    returns = df['Close'].pct_change().dropna()
    
    # Calculate mean and std of returns
    mu = returns.mean()
    sigma = returns.std()
    
    # Get last price and date
    last_price = df.iloc[-1]['Close']
    last_date = df.iloc[-1]['Date']
    
    # Generate future dates
    future_dates = [last_date + timedelta(days=i+1) for i in range(num_days)]
    
    # Monte Carlo simulation
    simulated_prices = []
    for _ in range(simulations):
        price = last_price
        simulation_prices = []
        for _ in range(num_days):
            # Generate random return
            random_return = np.random.normal(mu, sigma)
            price = price * (1 + random_return)
            simulation_prices.append(price)
        simulated_prices.append(simulation_prices)
    
    # Average across simulations
    avg_prices = np.mean(simulated_prices, axis=0)
    
    return pd.DataFrame({
        'Date': future_dates,
        'Close': avg_prices
    })


@app.route('/api/portfolio', methods=['POST'])
def get_portfolio_data():
    """
    Retrieve historical and projected future performance data for a portfolio of assets.
    
    Request Body:
        {
            "assetIds": ["string"],
            "timeRange": "1D" | "5D" | "1M" | "6M" | "1Y" | "5Y" | "MAX"
        }
    
    Returns:
        JSON response with PortfolioData object
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        asset_ids = data.get('assetIds', [])
        time_range = data.get('timeRange', '1Y')
        
        # Validate inputs
        if not asset_ids or not isinstance(asset_ids, list):
            return jsonify({"error": "assetIds must be a non-empty array"}), 400
        
        if time_range not in TIME_RANGE_DAYS:
            return jsonify({"error": f"Invalid timeRange. Must be one of: {list(TIME_RANGE_DAYS.keys())}"}), 400
        
        # Get symbols for asset IDs
        symbols = []
        for asset_id in asset_ids:
            symbol = get_symbol_for_asset_id(asset_id)
            if not symbol:
                return jsonify({"error": f"Asset not found: {asset_id}"}), 404
            symbols.append(symbol)
        
        days = TIME_RANGE_DAYS[time_range]
        
        # Load historical data for all assets
        historical_data = {}
        all_dates = set()
        
        for symbol in symbols:
            try:
                df = load_asset_data(symbol, days)
                historical_data[symbol] = df
                all_dates.update(df['Date'].tolist())
            except FileNotFoundError:
                return jsonify({"error": f"Data not available for symbol: {symbol}"}), 404
        
        # Create unified timeline
        all_dates = sorted(list(all_dates))
        
        # Build historical DataPoints
        historical = []
        for date in all_dates:
            point = {"date": date.isoformat()}
            values = []
            
            for symbol in symbols:
                df = historical_data[symbol]
                row = df[df['Date'] == date]
                if not row.empty:
                    value = float(row.iloc[0]['Close'])
                    point[symbol] = value
                    values.append(value)
            
            # Calculate average if we have values
            if values:
                point['average'] = sum(values) / len(values)
                historical.append(point)
        
        # Generate future projections
        # Limit to max 90 days or half the selected period (whichever is smaller)
        future_days = min(90, days // 2)
        
        future_data = {}
        for symbol in symbols:
            df = historical_data[symbol]
            future_df = generate_future_projections(df, symbol, future_days)
            future_data[symbol] = future_df
        
        # Build future DataPoints
        future = []
        if future_days > 0 and future_data:
            # Get all future dates
            future_dates = set()
            for df in future_data.values():
                if not df.empty:
                    future_dates.update(df['Date'].tolist())
            
            future_dates = sorted(list(future_dates))
            
            for date in future_dates:
                point = {"date": date.isoformat()}
                values = []
                
                for symbol in symbols:
                    df = future_data[symbol]
                    if not df.empty:
                        row = df[df['Date'] == date]
                        if not row.empty:
                            value = float(row.iloc[0]['Close'])
                            point[symbol] = value
                            values.append(value)
                
                if values:
                    point['average'] = sum(values) / len(values)
                    future.append(point)
        
        # Calculate statistics
        stats = {}
        
        # Calculate volatility (average across assets)
        volatilities = []
        for symbol in symbols:
            try:
                vol = get_volatility(symbol, min(days, 365))
                volatilities.append(vol)
            except:
                pass
        
        stats['volatility'] = sum(volatilities) / len(volatilities) if volatilities else 0.0
        
        # Calculate net profit and percentage
        if historical:
            first_avg = historical[0]['average']
            last_avg = historical[-1]['average']
            stats['netProfit'] = round(last_avg - first_avg, 2)
            stats['netProfitPercent'] = round(((last_avg - first_avg) / first_avg) * 100, 2)
        else:
            stats['netProfit'] = 0.0
            stats['netProfitPercent'] = 0.0
        
        # Calculate predicted profit for 1 year
        if future:
            current_avg = historical[-1]['average'] if historical else 0
            # Find the future point closest to 1 year (365 days)
            future_1y = future[-1] if future else None
            if future_1y:
                predicted_avg = future_1y['average']
                stats['predictedProfit1Y'] = round(predicted_avg - current_avg, 2)
            else:
                stats['predictedProfit1Y'] = 0.0
        else:
            stats['predictedProfit1Y'] = 0.0
        
        # Calculate correlation if multiple assets
        if len(symbols) > 1:
            try:
                csv_files = [Path('assets') / f'{symbol}.csv' for symbol in symbols]
                prices = load_prices_from_csvs(csv_files)
                corr_matrix = returns_corr(prices)
                
                # Calculate average correlation (excluding diagonal)
                n = len(corr_matrix)
                total_corr = 0.0
                count = 0
                for i in range(n):
                    for j in range(i+1, n):
                        try:
                            val = corr_matrix.iloc[i, j]
                            if pd.notna(val):
                                total_corr += float(val)
                                count += 1
                        except:
                            pass
                
                stats['correlation'] = round(total_corr / count if count > 0 else 0.0, 2)
            except:
                stats['correlation'] = 0.0
        
        # Generate asset colors
        asset_colors = {}
        for symbol in symbols:
            asset_colors[symbol] = generate_color_for_symbol(symbol)
        asset_colors['average'] = '#a855f7'  # Purple for average
        
        return jsonify({
            "historical": historical,
            "future": future,
            "stats": stats,
            "assetColors": asset_colors
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/correlation-groups', methods=['POST'])
def get_correlation_groups():
    """
    Retrieve groups of assets that are correlated with the portfolio assets.
    
    Request Body:
        {
            "assetIds": ["string"]
        }
    
    Returns:
        JSON response with array of CorrelationGroupType objects
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        asset_ids = data.get('assetIds', [])
        
        if not asset_ids or not isinstance(asset_ids, list):
            return jsonify({"error": "assetIds must be a non-empty array"}), 400
        
        # Get symbols for asset IDs
        portfolio_symbols = []
        for asset_id in asset_ids:
            symbol = get_symbol_for_asset_id(asset_id)
            if not symbol:
                return jsonify({"error": f"Asset not found: {asset_id}"}), 404
            portfolio_symbols.append(symbol)
        
        # Load all available assets
        all_symbols = [asset['symbol'] for asset in ASSETS_METADATA if asset['type'] != 'index']
        
        # Calculate correlations
        try:
            csv_files = [Path('assets') / f'{symbol}.csv' for symbol in all_symbols if (Path('assets') / f'{symbol}.csv').exists()]
            prices = load_prices_from_csvs(csv_files)
            corr_matrix = returns_corr(prices)
        except Exception as e:
            return jsonify({"error": f"Failed to calculate correlations: {str(e)}"}), 500
        
        # Group assets by type and calculate correlation scores
        groups = {}
        
        for asset in ASSETS_METADATA:
            if asset['type'] == 'index':
                continue
            
            symbol = asset['symbol']
            asset_type = asset['type']
            
            if symbol not in corr_matrix.columns:
                continue
            
            # Calculate average correlation with portfolio
            correlations = []
            for port_symbol in portfolio_symbols:
                if port_symbol in corr_matrix.columns and symbol in corr_matrix.columns:
                    try:
                        corr_val = corr_matrix.loc[symbol, port_symbol]
                        if pd.notna(corr_val):
                            correlations.append(abs(float(corr_val)))
                    except:
                        pass
            
            avg_corr = sum(correlations) / len(correlations) if correlations else 0
            
            # Group by asset type
            if asset_type not in groups:
                groups[asset_type] = {
                    'assets': [],
                    'correlations': []
                }
            
            groups[asset_type]['assets'].append(asset['id'])
            groups[asset_type]['correlations'].append(avg_corr)
        
        # Create correlation groups
        result = []
        group_id = 1
        
        type_names = {
            'equity_etf': 'Equity ETFs',
            'bond_etf': 'Bond ETFs',
            'commodity_etf': 'Commodity ETFs',
            'crypto_etf': 'Crypto ETFs',
            'leveraged_etf': 'Leveraged ETFs',
            'closed_end_fund': 'Closed-End Funds'
        }
        
        for asset_type, group_data in groups.items():
            # Only include groups with at least one portfolio asset
            has_portfolio_asset = any(
                get_symbol_for_asset_id(aid) in portfolio_symbols 
                for aid in group_data['assets']
            )
            
            if has_portfolio_asset and group_data['assets']:
                avg_corr = sum(group_data['correlations']) / len(group_data['correlations'])
                
                result.append({
                    'id': f'group-{group_id:03d}',
                    'name': type_names.get(asset_type, asset_type.replace('_', ' ').title()),
                    'assetIds': group_data['assets'],
                    'correlationScore': round(avg_corr, 2)
                })
                group_id += 1
        
        # Sort by correlation score descending
        result.sort(key=lambda x: x['correlationScore'], reverse=True)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/heatmap', methods=['POST'])
def get_heatmap_data():
    """
    Generate correlation heatmap data showing relationships between portfolio assets.
    
    Request Body:
        {
            "assetIds": ["string"]
        }
    
    Returns:
        JSON response with HeatmapData object
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        asset_ids = data.get('assetIds', [])
        
        if not asset_ids or not isinstance(asset_ids, list):
            return jsonify({"error": "assetIds must be a non-empty array"}), 400
        
        # Get symbols for asset IDs
        symbols = []
        for asset_id in asset_ids:
            symbol = get_symbol_for_asset_id(asset_id)
            if not symbol:
                return jsonify({"error": f"Asset not found: {asset_id}"}), 404
            symbols.append(symbol)
        
        # Load price data and calculate correlation
        try:
            csv_files = [Path('assets') / f'{symbol}.csv' for symbol in symbols]
            prices = load_prices_from_csvs(csv_files)
            corr_matrix = returns_corr(prices)
            
            # Ensure symbols are in the same order
            corr_matrix = corr_matrix.loc[symbols, symbols]
            
            # Convert to 2D array
            data_matrix = corr_matrix.values.tolist()
            
            # Round values
            data_matrix = [[round(val, 2) for val in row] for row in data_matrix]
            
            return jsonify({
                "labels": symbols,
                "data": data_matrix
            })
            
        except Exception as e:
            return jsonify({"error": f"Failed to calculate correlation: {str(e)}"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/diversify', methods=['POST'])
def get_diversification_recommendations():
    """
    Get recommendations for assets that would improve portfolio diversification.
    
    Request Body:
        {
            "assetIds": ["string"]
        }
    
    Returns:
        JSON response with array of DiversifyAsset objects
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        asset_ids = data.get('assetIds', [])
        
        if not asset_ids or not isinstance(asset_ids, list):
            return jsonify({"error": "assetIds must be a non-empty array"}), 400
        
        # Get symbols for asset IDs
        portfolio_symbols = []
        portfolio_types = set()
        
        for asset_id in asset_ids:
            asset = get_asset_by_id(asset_id)
            if not asset:
                return jsonify({"error": f"Asset not found: {asset_id}"}), 404
            portfolio_symbols.append(asset['symbol'])
            portfolio_types.add(asset['type'])
        
        # Load all available assets
        all_symbols = [asset['symbol'] for asset in ASSETS_METADATA if asset['type'] != 'index']
        
        # Calculate correlations
        try:
            csv_files = [Path('assets') / f'{symbol}.csv' for symbol in all_symbols if (Path('assets') / f'{symbol}.csv').exists()]
            prices = load_prices_from_csvs(csv_files)
            corr_matrix = returns_corr(prices)
        except Exception as e:
            return jsonify({"error": f"Failed to calculate correlations: {str(e)}"}), 500
        
        # Find diversification candidates
        candidates = []
        
        for asset in ASSETS_METADATA:
            if asset['type'] == 'index' or asset['symbol'] in portfolio_symbols:
                continue
            
            symbol = asset['symbol']
            
            if symbol not in corr_matrix.columns:
                continue
            
            # Calculate average correlation with portfolio
            correlations = []
            for port_symbol in portfolio_symbols:
                if port_symbol in corr_matrix.columns:
                    try:
                        corr_val = corr_matrix.loc[symbol, port_symbol]
                        if pd.notna(corr_val):
                            correlations.append(float(corr_val))
                    except:
                        pass
            
            if not correlations:
                continue
            
            avg_corr = sum(correlations) / len(correlations)
            
            # Generate reason based on asset type and correlation
            reason = ""
            expected_improvement = 0.0
            
            if asset['type'] not in portfolio_types:
                reason = f"Different asset class ({asset['type'].replace('_', ' ')}), "
                expected_improvement += 15.0
            
            if avg_corr < 0.3:
                reason += "very low correlation with current portfolio provides strong diversification"
                expected_improvement += 20.0
            elif avg_corr < 0.5:
                reason += "low correlation with current portfolio improves diversification"
                expected_improvement += 12.0
            elif avg_corr < 0.7:
                reason += "moderate correlation provides some diversification benefit"
                expected_improvement += 5.0
            else:
                # Skip highly correlated assets
                continue
            
            candidates.append({
                'id': asset['id'],
                'symbol': asset['symbol'],
                'name': asset['name'],
                'reason': reason.strip(),
                'correlationScore': round(avg_corr, 2),
                'expectedImprovement': round(expected_improvement, 1)
            })
        
        # Sort by expected improvement descending, then by correlation ascending
        candidates.sort(key=lambda x: (-x['expectedImprovement'], x['correlationScore']))
        
        # Return top 10 recommendations
        return jsonify(candidates[:10])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with API documentation.
    
    Returns:
        JSON response with available endpoints
    """
    return jsonify({
        "service": "OpenFOF Asset Management API",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/health": "Health check endpoint",
            "GET /api/assets": "Get all available assets (supports pagination)",
            "GET /api/assets/search?q=<query>": "Search assets by symbol or name (supports pagination)",
            "GET /api/assets/<asset_id>": "Get asset by ID",
            "GET /api/assets/symbol/<symbol>": "Get asset by symbol",
            "POST /api/portfolio": "Get portfolio historical and future data",
            "POST /api/correlation-groups": "Get correlation groups for portfolio assets",
            "POST /api/heatmap": "Get correlation heatmap data",
            "POST /api/diversify": "Get diversification recommendations"
        },
        "examples": {
            "search": "/api/assets/search?q=ETF",
            "search_paginated": "/api/assets/search?q=ETF&page=1&page_size=5",
            "get_all": "/api/assets",
            "get_by_id": "/api/assets/asset-001",
            "get_by_symbol": "/api/assets/symbol/SOXS",
            "portfolio": "POST /api/portfolio with body: {\"assetIds\": [\"asset-001\", \"asset-002\"], \"timeRange\": \"1Y\"}",
            "correlation_groups": "POST /api/correlation-groups with body: {\"assetIds\": [\"asset-001\"]}",
            "heatmap": "POST /api/heatmap with body: {\"assetIds\": [\"asset-001\", \"asset-002\"]}",
            "diversify": "POST /api/diversify with body: {\"assetIds\": [\"asset-001\"]}"
        }
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    print("Starting OpenFOF Asset Management API Server...")
    print("API will be available at: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/assets/search?q=<query>")
    print("  GET  /api/assets")
    print("  GET  /api/assets/<asset_id>")
    print("  GET  /api/assets/symbol/<symbol>")
    print("  POST /api/portfolio")
    print("  POST /api/correlation-groups")
    print("  POST /api/heatmap")
    print("  POST /api/diversify")
    print("  GET  /api/health")
    print("\nExample requests:")
    print("  curl 'http://localhost:5000/api/assets/search?q=ETF'")
    print("  curl 'http://localhost:5000/api/assets/asset-001'")
    print("  curl -X POST http://localhost:5000/api/portfolio \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"assetIds\": [\"asset-001\", \"asset-002\"], \"timeRange\": \"1Y\"}'")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
