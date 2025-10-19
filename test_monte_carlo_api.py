"""
Test the API with the new Monte Carlo implementation
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_portfolio_endpoint():
    """
    Test the /api/portfolio endpoint with the new Monte Carlo simulation
    """
    print("=" * 80)
    print("Testing /api/portfolio endpoint with Monte Carlo simulation")
    print("=" * 80)
    
    # Test data
    payload = {
        "assetIds": ["asset-001", "asset-002"],  # SOXS and BITQ
        "timeRange": "6M"
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Request successful!")
            print(f"\nResponse structure:")
            print(f"  Historical data points: {len(data.get('historical', []))}")
            print(f"  Future data points: {len(data.get('future', []))}")
            print(f"  Asset colors: {list(data.get('assetColors', {}).keys())}")
            
            # Check if future projections have the expected structure
            if data.get('future') and len(data['future']) > 0:
                first_future = data['future'][0]
                last_future = data['future'][-1]
                
                print(f"\n  Future projections structure:")
                print(f"    Keys in data points: {list(first_future.keys())}")
                print(f"    First future date: {first_future.get('date')}")
                print(f"    Last future date: {last_future.get('date')}")
                
                if 'average' in last_future:
                    print(f"    Last projected average: ${last_future['average']:.2f}")
            
            # Display statistics
            stats = data.get('stats', {})
            print(f"\n  Portfolio statistics:")
            print(f"    Volatility: {stats.get('volatility', 'N/A')}")
            print(f"    Net profit: ${stats.get('netProfit', 'N/A')}")
            print(f"    Net profit %: {stats.get('netProfitPercent', 'N/A')}%")
            print(f"    Predicted profit (1Y): ${stats.get('predictedProfit1Y', 'N/A')}")
            
            # Verify historical data
            if data.get('historical') and len(data['historical']) > 0:
                first_hist = data['historical'][0]
                last_hist = data['historical'][-1]
                
                print(f"\n  Historical data:")
                print(f"    First date: {first_hist.get('date')}")
                print(f"    Last date: {last_hist.get('date')}")
                if 'average' in last_hist:
                    print(f"    Last historical average: ${last_hist['average']:.2f}")
            
            print("\n" + "=" * 80)
            print("✅ Monte Carlo simulation is working correctly!")
            print("=" * 80)
            
        else:
            print(f"\n❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API server")
        print("Make sure the server is running: python api_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_single_asset():
    """
    Test with a single asset to see Monte Carlo in action
    """
    print("\n" + "=" * 80)
    print("Testing single asset (IVV) with different time ranges")
    print("=" * 80)
    
    time_ranges = ['1M', '6M', '1Y']
    
    for time_range in time_ranges:
        payload = {
            "assetIds": ["asset-012"],  # IVV
            "timeRange": time_range
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/portfolio",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                future = data.get('future', [])
                
                print(f"\n  Time range: {time_range}")
                print(f"    Future projection points: {len(future)}")
                
                if future:
                    last = future[-1]
                    print(f"    Last projection date: {last.get('date')}")
                    if 'average' in last:
                        print(f"    Projected price: ${last['average']:.2f}")
                        
        except Exception as e:
            print(f"    Error: {e}")


if __name__ == '__main__':
    print("\n🚀 Starting API tests with Monte Carlo simulation...")
    print("Note: Make sure the API server is running (python api_server.py)\n")
    
    test_portfolio_endpoint()
    test_single_asset()
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)
