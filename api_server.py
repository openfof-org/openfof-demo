"""
REST API Server for OpenFOF Asset Management Demo
Provides endpoints for searching and retrieving asset information.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from assets_metadata import search_assets, get_all_assets, get_asset_by_id, get_asset_by_symbol
from typing import Dict, List, Any

app = Flask(__name__)
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
            "GET /api/assets/symbol/<symbol>": "Get asset by symbol"
        },
        "examples": {
            "search": "/api/assets/search?q=ETF",
            "search_paginated": "/api/assets/search?q=ETF&page=1&page_size=5",
            "get_all": "/api/assets",
            "get_by_id": "/api/assets/asset-001",
            "get_by_symbol": "/api/assets/symbol/SOXS"
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
    print("  - GET /api/assets/search?q=<query>")
    print("  - GET /api/assets")
    print("  - GET /api/assets/<asset_id>")
    print("  - GET /api/assets/symbol/<symbol>")
    print("  - GET /api/health")
    print("\nExample requests:")
    print("  curl 'http://localhost:5000/api/assets/search?q=ETF'")
    print("  curl 'http://localhost:5000/api/assets/search?q=S&page=1&page_size=3'")
    print("  curl 'http://localhost:5000/api/assets/asset-001'")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
