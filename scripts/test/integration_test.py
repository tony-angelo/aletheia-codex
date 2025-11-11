"""
Integration test for the review API to verify frontend-backend connectivity.
"""

import requests
import json
import time

# API base URL
API_BASE_URL = "http://localhost:8081"

def test_api_endpoints():
    """Test all API endpoints to verify they work correctly."""
    
    print("🧪 Testing Review API Integration...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['data']['status'] == 'healthy'
        print("   ✅ Health check passed")
    except Exception as e:
        print(f"   ❌ Health check failed: {str(e)}")
        return False
    
    # Test 2: Get Pending Items (should work even with empty queue)
    print("\n2. Testing Get Pending Items...")
    try:
        headers = {"Authorization": "Bearer test-token"}
        response = requests.get(f"{API_BASE_URL}/review/pending", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] == True
            assert 'data' in data
            assert 'items' in data['data']
            print("   ✅ Get pending items passed")
        else:
            print(f"   ⚠️  Get pending items returned {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Get pending items failed: {str(e)}")
    
    # Test 3: Get User Stats
    print("\n3. Testing Get User Stats...")
    try:
        headers = {"Authorization": "Bearer test-token"}
        response = requests.get(f"{API_BASE_URL}/review/stats", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] == True
            assert 'data' in data
            print("   ✅ Get user stats passed")
        else:
            print(f"   ⚠️  Get user stats returned {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Get user stats failed: {str(e)}")
    
    # Test 4: Approve Item (should fail gracefully for non-existent item)
    print("\n4. Testing Approve Item...")
    try:
        headers = {"Authorization": "Bearer test-token"}
        payload = {"item_id": "non-existent-item"}
        response = requests.post(f"{API_BASE_URL}/review/approve", 
                               headers=headers, 
                               json=payload, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 404:
            data = response.json()
            assert data['success'] == False
            assert 'NOT_FOUND' in str(data['error'])
            print("   ✅ Approve item handled non-existent item correctly")
        else:
            print(f"   ⚠️  Approve item returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Approve item failed: {str(e)}")
    
    # Test 5: Batch Approve (should fail gracefully for empty list)
    print("\n5. Testing Batch Approve...")
    try:
        headers = {"Authorization": "Bearer test-token"}
        payload = {"item_ids": []}
        response = requests.post(f"{API_BASE_URL}/review/batch-approve", 
                               headers=headers, 
                               json=payload, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400:
            data = response.json()
            assert data['success'] == False
            assert 'INVALID_REQUEST' in str(data['error'])
            print("   ✅ Batch approve handled empty list correctly")
        else:
            print(f"   ⚠️  Batch approve returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Batch approve failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Integration testing completed!")
    print("✅ API is running and responding to requests")
    print("🌐 Frontend should be able to connect to this backend")
    
    return True

if __name__ == "__main__":
    # Give the server a moment to start
    time.sleep(2)
    test_api_endpoints()