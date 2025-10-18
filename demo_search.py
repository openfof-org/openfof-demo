"""
Quick demonstration of the asset search functionality.
This script shows how the search works without requiring the full REST API.
"""

from assets_metadata import search_assets, get_all_assets, get_asset_by_symbol
import json


def print_assets(assets, title="Results"):
    """Pretty print assets."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    if not assets:
        print("No assets found.")
    else:
        print(f"Found {len(assets)} asset(s):\n")
        for asset in assets:
            print(f"  • {asset['symbol']:10} - {asset['name']}")
            print(f"    ID: {asset['id']}, Type: {asset['type']}")
    print(f"{'='*70}\n")


def demo_search():
    """Demonstrate search functionality."""
    print("\n" + "="*70)
    print("🔍 OpenFOF Asset Search - Demo")
    print("="*70)
    
    # Demo 1: Search for "ETF"
    print("\n1️⃣ Searching for 'ETF'...")
    results = search_assets("ETF")
    print_assets(results, "Assets containing 'ETF'")
    
    # Demo 2: Search for "S"
    print("\n2️⃣ Searching for 'S'...")
    results = search_assets("S")
    print_assets(results, "Assets containing 'S'")
    
    # Demo 3: Search for "SOXS"
    print("\n3️⃣ Searching for 'SOXS' (exact match)...")
    results = search_assets("SOXS")
    print_assets(results, "Assets matching 'SOXS'")
    
    # Demo 4: Search for "semiconductor"
    print("\n4️⃣ Searching for 'semiconductor'...")
    results = search_assets("semiconductor")
    print_assets(results, "Assets related to semiconductors")
    
    # Demo 5: Case insensitive search
    print("\n5️⃣ Searching for 'tlt' (lowercase)...")
    results = search_assets("tlt")
    print_assets(results, "Case-insensitive search for 'tlt'")
    
    # Demo 6: Get specific asset by symbol
    print("\n6️⃣ Getting asset details for 'GDX'...")
    asset = get_asset_by_symbol("GDX")
    if asset:
        print(f"\n{'='*70}")
        print("Asset Details")
        print(f"{'='*70}")
        print(json.dumps(asset, indent=2))
        print(f"{'='*70}\n")
    
    # Demo 7: Show all assets
    print("\n7️⃣ All available assets...")
    all_assets = get_all_assets()
    print_assets(all_assets, f"All Assets ({len(all_assets)} total)")
    
    print("\n" + "="*70)
    print("✅ Demo completed!")
    print("\nTo use the full REST API:")
    print("  1. Start the server: python api_server.py")
    print("  2. Test it: curl 'http://localhost:5000/api/assets/search?q=ETF'")
    print("  3. Or run: python test_api.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_search()
