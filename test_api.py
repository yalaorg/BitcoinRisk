# test_api.py
import requests
import json
from datetime import datetime
import pandas as pd

def test_api():
    """Test the Bitcoin Risk Analysis API"""
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    print("Testing root endpoint...")
    response = requests.get(base_url)
    print(response.json())
    print()
    
    # Test risk prediction
    print("Testing risk prediction...")
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "open": 45000.0,
        "high": 46000.0,
        "low": 44000.0,
        "close": 45500.0,
        "volume": 1000000.0
    }
    
    response = requests.post(f"{base_url}/predict/risk", json=test_data)
    print(json.dumps(response.json(), indent=2))
    print()
    
    # Get model info
    print("Getting model information...")
    response = requests.get(f"{base_url}/model/info")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_api()