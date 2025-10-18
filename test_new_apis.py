"""
Test script for new API endpoints: portfolio, correlation-groups, heatmap, and diversify.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_portfolio_api():
    """Test the portfolio endpoint."""
    print("\n=== Testing POST /api/portfolio ===")
    
    payload = {
        "assetIds": ["asset-002", "asset-011"],
        "timeRange": "1Y"
    }
    
    response = requests.post(f"{BASE_URL}/api/portfolio", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Historical data points: {len(data.get('historical', []))}")
        print(f"Future data points: {len(data.get('future', []))}")
        print(f"Stats: {json.dumps(data.get('stats', {}), indent=2)}")
        print(f"Asset Colors: {json.dumps(data.get('assetColors', {}), indent=2)}")
        
        # Show sample historical data
        if data.get('historical'):
            print(f"\nSample historical point:")
            print(json.dumps(data['historical'][0], indent=2))
        
        # Show sample future data
        if data.get('future'):
            print(f"\nSample future point:")
            print(json.dumps(data['future'][0], indent=2))
    else:
        print(f"Error: {response.text}")


def test_correlation_groups_api():
    """Test the correlation groups endpoint."""
    print("\n=== Testing POST /api/correlation-groups ===")
    
    payload = {
        "assetIds": ["asset-002", "asset-011"]
    }
    
    response = requests.post(f"{BASE_URL}/api/correlation-groups", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Number of correlation groups: {len(data)}")
        
        for group in data[:3]:  # Show first 3 groups
            print(f"\nGroup: {group['name']}")
            print(f"  ID: {group['id']}")
            print(f"  Correlation Score: {group['correlationScore']}")
            print(f"  Number of assets: {len(group['assetIds'])}")
    else:
        print(f"Error: {response.text}")


def test_heatmap_api():
    """Test the heatmap endpoint."""
    print("\n=== Testing POST /api/heatmap ===")
    
    payload = {
        "assetIds": ["asset-002", "asset-011", "asset-025"]
    }
    
    response = requests.post(f"{BASE_URL}/api/heatmap", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Labels: {data.get('labels', [])}")
        print(f"Correlation Matrix:")
        
        matrix = data.get('data', [])
        labels = data.get('labels', [])
        
        # Print header
        print(f"{'':8}", end='')
        for label in labels:
            print(f"{label:>8}", end='')
        print()
        
        # Print rows
        for i, row in enumerate(matrix):
            print(f"{labels[i]:8}", end='')
            for val in row:
                print(f"{val:>8.2f}", end='')
            print()
    else:
        print(f"Error: {response.text}")


def test_diversify_api():
    """Test the diversification recommendations endpoint."""
    print("\n=== Testing POST /api/diversify ===")
    
    payload = {
        "assetIds": ["asset-011", "asset-016"]  # IVV and SCHX (both S&P 500 ETFs)
    }
    
    response = requests.post(f"{BASE_URL}/api/diversify", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Number of recommendations: {len(data)}")
        
        for i, rec in enumerate(data[:5], 1):  # Show top 5 recommendations
            print(f"\n{i}. {rec['symbol']} - {rec['name']}")
            print(f"   Correlation Score: {rec['correlationScore']}")
            print(f"   Expected Improvement: {rec['expectedImprovement']}%")
            print(f"   Reason: {rec['reason']}")
    else:
        print(f"Error: {response.text}")


def test_error_cases():
    """Test error handling."""
    print("\n=== Testing Error Cases ===")
    
    # Test missing assetIds
    print("\n1. Missing assetIds:")
    response = requests.post(f"{BASE_URL}/api/portfolio", json={})
    print(f"Status: {response.status_code}, Response: {response.json()}")
    
    # Test invalid timeRange
    print("\n2. Invalid timeRange:")
    response = requests.post(
        f"{BASE_URL}/api/portfolio",
        json={"assetIds": ["asset-001"], "timeRange": "INVALID"}
    )
    print(f"Status: {response.status_code}, Response: {response.json()}")
    
    # Test non-existent asset
    print("\n3. Non-existent asset:")
    response = requests.post(
        f"{BASE_URL}/api/portfolio",
        json={"assetIds": ["asset-999"], "timeRange": "1Y"}
    )
    print(f"Status: {response.status_code}, Response: {response.json()}")


if __name__ == "__main__":
    print("Testing New OpenFOF API Endpoints")
    print("=" * 50)
    print("Make sure the API server is running on http://localhost:5000")
    print("=" * 50)
    
    try:
        # Test health first
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("Error: API server is not responding. Please start the server first.")
            exit(1)
        
        print("API server is healthy. Running tests...\n")
        
        test_portfolio_api()
        test_correlation_groups_api()
        test_heatmap_api()
        test_diversify_api()
        test_error_cases()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Please start the server with: python api_server.py")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
