"""
Asset metadata definitions for the OpenFOF demo application.
This module contains information about available assets including their symbols, names, and types.
"""

import hashlib# Asset metadata - in a production system, this would come from a database
ASSETS_METADATA = [
    {"id": "asset-001", "symbol": "BBUS", "name": "JPMorgan BetaBuilders U.S. Equity ETF", "type": "equity_etf", "description": "Broad U.S. equity market exposure"},
    {"id": "asset-002", "symbol": "BITQ", "name": "Bitwise Crypto Industry Innovators ETF", "type": "crypto_etf", "description": "ETF tracking companies in crypto and blockchain"},
    {"id": "asset-003", "symbol": "BIV", "name": "Vanguard Intermediate-Term Bond ETF", "type": "bond_etf", "description": "Intermediate-term investment-grade bonds"},
    {"id": "asset-004", "symbol": "GDX", "name": "VanEck Gold Miners ETF", "type": "commodity_etf", "description": "Gold mining companies"},
    {"id": "asset-005", "symbol": "IDEV", "name": "iShares Core MSCI International Developed Markets ETF", "type": "equity_etf", "description": "International developed markets equity"},
    {"id": "asset-006", "symbol": "IGIB", "name": "iShares Intermediate-Term Corporate Bond ETF", "type": "bond_etf", "description": "Intermediate-term corporate bonds"},
    {"id": "asset-007", "symbol": "IGLB", "name": "iShares Long-Term Corporate Bond ETF", "type": "bond_etf", "description": "Long-term corporate bonds"},
    {"id": "asset-008", "symbol": "ILCB", "name": "iShares Morningstar U.S. Equity ETF", "type": "equity_etf", "description": "U.S. equity exposure"},
    {"id": "asset-009", "symbol": "ITOT", "name": "iShares Core S&P Total U.S. Stock Market ETF", "type": "equity_etf", "description": "Total U.S. stock market"},
    {"id": "asset-010", "symbol": "IVOV", "name": "Vanguard S&P Mid-Cap 400 Value ETF", "type": "equity_etf", "description": "Mid-cap value stocks"},
    {"id": "asset-011", "symbol": "IVV", "name": "iShares Core S&P 500 ETF", "type": "equity_etf", "description": "S&P 500 index tracking"},
    {"id": "asset-012", "symbol": "RSBT", "name": "RiverNorth Specialty Finance Corporation", "type": "closed_end_fund", "description": "Specialty finance corporation"},
    {"id": "asset-013", "symbol": "SCHF", "name": "Schwab International Equity ETF", "type": "equity_etf", "description": "International equity exposure"},
    {"id": "asset-014", "symbol": "SCHP", "name": "Schwab U.S. TIPS ETF", "type": "bond_etf", "description": "U.S. Treasury Inflation-Protected Securities"},
    {"id": "asset-015", "symbol": "SCHR", "name": "Schwab Intermediate-Term U.S. Treasury ETF", "type": "bond_etf", "description": "Intermediate-term U.S. Treasury bonds"},
    {"id": "asset-016", "symbol": "SCHX", "name": "Schwab U.S. Large-Cap ETF", "type": "equity_etf", "description": "U.S. large-cap stocks"},
    {"id": "asset-017", "symbol": "SOXS", "name": "Direxion Daily Semiconductor Bear 3X Shares", "type": "leveraged_etf", "description": "3x inverse leveraged semiconductor ETF"},
    {"id": "asset-018", "symbol": "SPDW", "name": "SPDR Portfolio Developed World ex-US ETF", "type": "equity_etf", "description": "Developed markets excluding U.S."},
    {"id": "asset-019", "symbol": "SPLG", "name": "SPDR Portfolio S&P 500 ETF", "type": "equity_etf", "description": "S&P 500 exposure"},
    {"id": "asset-020", "symbol": "SPPIX", "name": "SP Funds S&P 500 Sharia Industry Exclusions ETF", "type": "equity_etf", "description": "Shariah-compliant S&P 500"},
    {"id": "asset-021", "symbol": "SPTI", "name": "SPDR Portfolio Intermediate Term Treasury ETF", "type": "bond_etf", "description": "Intermediate-term Treasury bonds"},
    {"id": "asset-022", "symbol": "SPTM", "name": "SPDR Portfolio S&P 1500 Composite Stock Market ETF", "type": "equity_etf", "description": "Total U.S. stock market"},
    {"id": "asset-023", "symbol": "SQQQ", "name": "ProShares UltraPro Short QQQ", "type": "leveraged_etf", "description": "3x inverse leveraged Nasdaq-100"},
    {"id": "asset-024", "symbol": "STIP", "name": "iShares 0-5 Year TIPS Bond ETF", "type": "bond_etf", "description": "Short-term TIPS"},
    {"id": "asset-025", "symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "type": "bond_etf", "description": "Long-term U.S. Treasury bonds"},
    {"id": "asset-026", "symbol": "VCLT", "name": "Vanguard Long-Term Corporate Bond ETF", "type": "bond_etf", "description": "Long-term corporate bonds"},
    {"id": "asset-027", "symbol": "VCSH", "name": "Vanguard Short-Term Corporate Bond ETF", "type": "bond_etf", "description": "Short-term corporate bonds"},
    {"id": "asset-028", "symbol": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "type": "equity_etf", "description": "International developed markets"},
    {"id": "asset-029", "symbol": "VGIT", "name": "Vanguard Intermediate-Term Treasury ETF", "type": "bond_etf", "description": "Intermediate-term Treasury bonds"},
    {"id": "asset-030", "symbol": "VGLT", "name": "Vanguard Long-Term Treasury ETF", "type": "bond_etf", "description": "Long-term Treasury bonds"},
    {"id": "asset-031", "symbol": "VGSH", "name": "Vanguard Short-Term Treasury ETF", "type": "bond_etf", "description": "Short-term Treasury bonds"},
    {"id": "asset-032", "symbol": "VMBS", "name": "Vanguard Mortgage-Backed Securities ETF", "type": "bond_etf", "description": "Mortgage-backed securities"},
]


def get_all_assets():
    """Return all available assets."""
    return ASSETS_METADATA


def search_assets(query: str, case_sensitive: bool = False):
    if not query:
        return []

    norm = (lambda s: s if case_sensitive else s.casefold())
    q = norm(query)

    ranked = []
    for a in ASSETS_METADATA:
        sym_raw = a["symbol"]; name_raw = a["name"]; desc_raw = a.get("description", "")

        sym = norm(sym_raw)
        name = norm(name_raw)
        desc = norm(desc_raw)

        # must match in symbol or name
        in_sym = q in sym
        in_name = q in name
        if not (in_sym or in_name):
            continue

        # --- relevance rank: smaller tuple sorts earlier ---
        exact_sym   = 0 if sym == q else 1
        starts_sym  = 0 if sym.startswith(q) else 1
        pos_sym     = sym.find(q) if in_sym else 10_000
        starts_name = 0 if name.startswith(q) else 1
        pos_name    = name.find(q) if in_name else 10_000

        rank = (
            exact_sym,
            starts_sym,
            pos_sym,
            starts_name,
            pos_name,
            sym,            # tie-breakers (stable, case-insensitive)
            name,
            desc,
        )
        ranked.append((rank, a))

    ranked.sort(key=lambda x: x[0])
    return [a for _, a in ranked]


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


def get_symbol_for_asset_id(asset_id: str):
    """
    Get the symbol for an asset ID.
    
    Args:
        asset_id: The unique asset identifier
    
    Returns:
        Symbol string if found, None otherwise
    """
    asset = get_asset_by_id(asset_id)
    return asset["symbol"] if asset else None


def generate_color_for_symbol(symbol: str) -> str:
    """
    Generate a consistent color hex code for a given symbol.
    Uses hash function to ensure same symbol always gets same color.
    
    Args:
        symbol: The asset ticker symbol
    
    Returns:
        Hex color code (e.g., '#3b82f6')
    """
    # Reserved color for average
    if symbol.lower() == 'average':
        return '#a855f7'
    
    # Color palette for assets (excluding purple which is reserved for average)
    colors = [
        '#3b82f6',  # blue
        '#10b981',  # green
        '#f59e0b',  # amber
        '#ef4444',  # red
        '#8b5cf6',  # violet
        '#ec4899',  # pink
        '#06b6d4',  # cyan
        '#84cc16',  # lime
        '#f97316',  # orange
        '#6366f1',  # indigo
        '#14b8a6',  # teal
        '#eab308',  # yellow
    ]
    
    # Use hash to deterministically select a color
    hash_value = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return colors[hash_value % len(colors)]
