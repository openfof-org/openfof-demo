"""
Asset metadata definitions for the OpenFOF demo application.
This module contains information about available assets including their symbols, names, and types.
"""

# Asset metadata - in a production system, this would come from a database
ASSETS_METADATA = [
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
    },
    {
        "id": "asset-003",
        "symbol": "RSBT",
        "name": "RiverNorth Specialty Finance Corporation",
        "type": "closed_end_fund",
        "description": "Specialty finance corporation focused on income generation"
    },
    {
        "id": "asset-004",
        "symbol": "SOXS",
        "name": "Direxion Daily Semiconductor Bear 3X Shares",
        "type": "leveraged_etf",
        "description": "3x inverse leveraged ETF for semiconductor sector"
    },
    {
        "id": "asset-005",
        "symbol": "SPPIX",
        "name": "SP Funds S&P 500 Sharia Industry Exclusions ETF",
        "type": "equity_etf",
        "description": "Shariah-compliant S&P 500 ETF"
    },
    {
        "id": "asset-006",
        "symbol": "SQQQ",
        "name": "ProShares UltraPro Short QQQ",
        "type": "leveraged_etf",
        "description": "3x inverse leveraged ETF for Nasdaq-100"
    },
    {
        "id": "asset-007",
        "symbol": "TLT",
        "name": "iShares 20+ Year Treasury Bond ETF",
        "type": "bond_etf",
        "description": "ETF tracking long-term U.S. Treasury bonds"
    },
    {
        "id": "index-001",
        "symbol": "S&P500",
        "name": "S&P 500 Index",
        "type": "index",
        "description": "Standard & Poor's 500 Index - broad U.S. equity market benchmark"
    }
]


def get_all_assets():
    """Return all available assets."""
    return ASSETS_METADATA


def search_assets(query: str, case_sensitive: bool = False):
    """
    Search for assets by symbol or name.
    
    Args:
        query: Search query string
        case_sensitive: Whether to perform case-sensitive search (default: False)
    
    Returns:
        List of matching asset dictionaries
    """
    if not query:
        return []
    
    search_term = query if case_sensitive else query.lower()
    results = []
    
    for asset in ASSETS_METADATA:
        symbol = asset["symbol"] if case_sensitive else asset["symbol"].lower()
        name = asset["name"] if case_sensitive else asset["name"].lower()
        
        # Check for partial matches in symbol or name
        if search_term in symbol or search_term in name:
            results.append(asset)
    
    return results


def get_asset_by_id(asset_id: str):
    """
    Get a specific asset by its ID.
    
    Args:
        asset_id: The unique asset identifier
    
    Returns:
        Asset dictionary if found, None otherwise
    """
    for asset in ASSETS_METADATA:
        if asset["id"] == asset_id:
            return asset
    return None


def get_asset_by_symbol(symbol: str):
    """
    Get a specific asset by its symbol.
    
    Args:
        symbol: The asset ticker symbol
    
    Returns:
        Asset dictionary if found, None otherwise
    """
    for asset in ASSETS_METADATA:
        if asset["symbol"].upper() == symbol.upper():
            return asset
    return None
