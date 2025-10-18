"""
Example: How to use the OpenFOF Asset Search API from Python code
This shows how to integrate the API into your own applications.
"""

import requests
import json


class AssetAPIClient:
    """
    Client for interacting with the OpenFOF Asset Management API.
    """
    
    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize the API client.
        
        Args:
            base_url: The base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
    
    def search_assets(self, query, page=None, page_size=None):
        """
        Search for assets by symbol or name.
        
        Args:
            query: Search query string
            page: Optional page number for pagination
            page_size: Optional number of results per page
        
        Returns:
            List of matching assets or paginated response
        """
        params = {"q": query}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        
        response = requests.get(f"{self.base_url}/api/assets/search", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_all_assets(self, page=None, page_size=None):
        """
        Get all available assets.
        
        Args:
            page: Optional page number for pagination
            page_size: Optional number of results per page
        
        Returns:
            List of all assets or paginated response
        """
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        
        response = requests.get(f"{self.base_url}/api/assets", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_asset_by_id(self, asset_id):
        """
        Get a specific asset by its ID.
        
        Args:
            asset_id: The unique asset identifier
        
        Returns:
            Asset object or None if not found
        """
        try:
            response = requests.get(f"{self.base_url}/api/assets/{asset_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def get_asset_by_symbol(self, symbol):
        """
        Get a specific asset by its symbol.
        
        Args:
            symbol: The asset ticker symbol
        
        Returns:
            Asset object or None if not found
        """
        try:
            response = requests.get(f"{self.base_url}/api/assets/symbol/{symbol}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def health_check(self):
        """
        Check if the API server is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def example_usage():
    """
    Example showing how to use the API client.
    """
    # Initialize the client
    client = AssetAPIClient("http://localhost:5000")
    
    print("="*70)
    print("Example: Using the Asset API Client")
    print("="*70)
    
    # Check if server is running
    print("\n1️⃣ Checking server health...")
    if client.health_check():
        print("   ✅ API server is healthy!")
    else:
        print("   ❌ API server is not responding")
        print("   Please start the server: python api_server.py")
        return
    
    # Search for ETFs
    print("\n2️⃣ Searching for ETFs...")
    results = client.search_assets("ETF")
    print(f"   Found {len(results)} ETFs:")
    for asset in results:
        print(f"   • {asset['symbol']:10} - {asset['name']}")
    
    # Search with pagination
    print("\n3️⃣ Searching for 'S' with pagination (2 per page)...")
    paginated = client.search_assets("S", page=1, page_size=2)
    print(f"   Page {paginated['pagination']['page']} of {paginated['pagination']['total_pages']}")
    print(f"   Total items: {paginated['pagination']['total_items']}")
    print(f"   Results on this page:")
    for asset in paginated['data']:
        print(f"   • {asset['symbol']:10} - {asset['name']}")
    
    # Get specific asset by symbol
    print("\n4️⃣ Getting details for SOXS...")
    asset = client.get_asset_by_symbol("SOXS")
    if asset:
        print(f"   Symbol: {asset['symbol']}")
        print(f"   Name: {asset['name']}")
        print(f"   Type: {asset['type']}")
        print(f"   Description: {asset['description']}")
    
    # Get asset by ID
    print("\n5️⃣ Getting asset by ID (asset-001)...")
    asset = client.get_asset_by_id("asset-001")
    if asset:
        print(f"   {asset['symbol']} - {asset['name']}")
    
    # Try to get non-existent asset
    print("\n6️⃣ Trying to get non-existent asset...")
    asset = client.get_asset_by_id("asset-999")
    if asset is None:
        print("   ✅ Correctly returned None for non-existent asset")
    
    # Get all assets
    print("\n7️⃣ Getting all assets...")
    all_assets = client.get_all_assets()
    print(f"   Total assets available: {len(all_assets)}")
    
    print("\n" + "="*70)
    print("✅ Example completed successfully!")
    print("="*70 + "\n")


def example_integration():
    """
    Example showing how to integrate the API into your application.
    """
    print("\n" + "="*70)
    print("Example: Integration Pattern")
    print("="*70 + "\n")
    
    print("# In your application code:")
    print("""
from asset_api_client import AssetAPIClient

# Initialize the client
api = AssetAPIClient("http://localhost:5000")

# Search for assets
results = api.search_assets("semiconductor")
for asset in results:
    print(f"Found: {asset['symbol']} - {asset['name']}")

# Get specific asset
asset = api.get_asset_by_symbol("SOXS")
if asset:
    print(f"Asset type: {asset['type']}")
    print(f"Description: {asset['description']}")

# Handle pagination for large result sets
page = 1
while True:
    response = api.search_assets("ETF", page=page, page_size=10)
    
    # Process results
    for asset in response['data']:
        process_asset(asset)
    
    # Check if there are more pages
    if not response['pagination']['has_next']:
        break
    page += 1
""")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n📚 This example demonstrates how to use the Asset API from Python code.\n")
    
    choice = input("Choose example:\n  1 = Run live examples (server must be running)\n  2 = Show integration patterns\n  > ")
    
    if choice == "1":
        example_usage()
    elif choice == "2":
        example_integration()
    else:
        print("\nShowing integration patterns...\n")
        example_integration()
        print("\nNote: To run live examples, restart and choose option 1")
        print("      (Make sure the server is running: python api_server.py)\n")
