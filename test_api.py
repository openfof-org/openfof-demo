"""
Test script for the OpenFOF Asset Management API
This script demonstrates how to test the API endpoints locally.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000"


def print_response(response, title="Response"):
    """Pretty print the API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"{'='*60}\n")


def test_health_check():
    """Test the health check endpoint."""
    print("\n🏥 Testing Health Check Endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response, "Health Check")


def test_search_assets():
    """Test the asset search endpoint."""
    print("\n🔍 Testing Asset Search Endpoint...")
    
    # Test 1: Search for "ETF"
    print("\n1️⃣ Searching for 'ETF'...")
    response = requests.get(f"{BASE_URL}/api/assets/search", params={"q": "ETF"})
    print_response(response, "Search Results for 'ETF'")
    
    # Test 2: Search for "S"
    print("\n2️⃣ Searching for 'S'...")
    response = requests.get(f"{BASE_URL}/api/assets/search", params={"q": "S"})
    print_response(response, "Search Results for 'S'")
    
    # Test 3: Search for "SOXS"
    print("\n3️⃣ Searching for 'SOXS'...")
    response = requests.get(f"{BASE_URL}/api/assets/search", params={"q": "SOXS"})
    print_response(response, "Search Results for 'SOXS'")
    
    # Test 4: Search with pagination
    print("\n4️⃣ Searching for 'E' with pagination (page 1, page_size 2)...")
    response = requests.get(f"{BASE_URL}/api/assets/search", params={
        "q": "E",
        "page": 1,
        "page_size": 2
    })
    print_response(response, "Paginated Search Results")


def test_get_all_assets():
    """Test get all assets endpoint."""
    print("\n📋 Testing Get All Assets Endpoint...")
    response = requests.get(f"{BASE_URL}/api/assets")
    print_response(response, "All Assets")


def test_get_asset_by_id():
    """Test get asset by ID endpoint."""
    print("\n🎯 Testing Get Asset by ID Endpoint...")
    
    # Test 1: Get existing asset
    print("\n1️⃣ Getting asset-001...")
    response = requests.get(f"{BASE_URL}/api/assets/asset-001")
    print_response(response, "Asset Details (asset-001)")
    
    # Test 2: Get non-existent asset
    print("\n2️⃣ Getting non-existent asset-999...")
    response = requests.get(f"{BASE_URL}/api/assets/asset-999")
    print_response(response, "Not Found (asset-999)")


def test_get_asset_by_symbol():
    """Test get asset by symbol endpoint."""
    print("\n🏷️  Testing Get Asset by Symbol Endpoint...")
    
    # Test 1: Get existing asset
    print("\n1️⃣ Getting SOXS...")
    response = requests.get(f"{BASE_URL}/api/assets/symbol/SOXS")
    print_response(response, "Asset Details (SOXS)")
    
    # Test 2: Test case insensitivity
    print("\n2️⃣ Getting tlt (lowercase)...")
    response = requests.get(f"{BASE_URL}/api/assets/symbol/tlt")
    print_response(response, "Asset Details (tlt)")


def test_error_cases():
    """Test error handling."""
    print("\n⚠️  Testing Error Cases...")
    
    # Test 1: Missing query parameter
    print("\n1️⃣ Search without query parameter...")
    response = requests.get(f"{BASE_URL}/api/assets/search")
    print_response(response, "Error: Missing Query Parameter")
    
    # Test 2: Invalid endpoint
    print("\n2️⃣ Invalid endpoint...")
    response = requests.get(f"{BASE_URL}/api/invalid")
    print_response(response, "Error: Invalid Endpoint")


def run_all_tests():
    """Run all test cases."""
    print("\n" + "="*60)
    print("🚀 OpenFOF Asset Management API - Test Suite")
    print("="*60)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ Error: API server is not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("Please make sure the server is running:")
        print("  python api_server.py")
        return
    except requests.exceptions.Timeout:
        print("\n❌ Error: API server is not responding (timeout)")
        return
    
    print("\n✅ API server is running!")
    
    # Run all tests
    test_health_check()
    test_search_assets()
    test_get_all_assets()
    test_get_asset_by_id()
    test_get_asset_by_symbol()
    test_error_cases()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n📝 Note: This script requires the API server to be running.")
    print("Start the server in another terminal with: python api_server.py\n")
    
    input("Press Enter to start testing (or Ctrl+C to cancel)...")
    
    run_all_tests()
