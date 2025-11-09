"""
Simple test script to verify the API is working.
"""

import requests
import json

def test_api():
    """Test the API endpoints."""
    
    print("Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8081/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test pending items
    try:
        headers = {"Authorization": "Bearer test-token"}
        response = requests.get("http://localhost:8081/review/pending", headers=headers, timeout=5)
        print(f"Pending items: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Pending items failed: {e}")

if __name__ == "__main__":
    test_api()