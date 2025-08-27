#!/usr/bin/env python3
"""
Test script to check the status of Bible outline backend service
"""
import requests
import json
import time

def test_backend_service():
    """Test the backend service endpoints and functionality"""
    base_url = "https://bible-outline-backend.onrender.com"
    
    print("=== Testing Bible Outline Backend Service ===\n")
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        if response.status_code == 200:
            if 'text/html' in response.headers.get('Content-Type', ''):
                print("   ⚠️  WARNING: Backend is serving HTML instead of API")
            else:
                print("   ✅ Backend responding correctly")
        else:
            print(f"   ❌ Backend returned error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    # Test 2: Health endpoint
    print("\n2. Testing health endpoint...")
    for endpoint in ["/health", "/api/health", "/api/enhanced/health"]:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Health check passed: {data}")
                except:
                    print(f"   ⚠️  Non-JSON response (likely HTML)")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
    
    # Test 3: API availability 
    print("\n3. Testing API endpoints...")
    try:
        response = requests.post(f"{base_url}/api/enhanced/upload", 
                               json={}, timeout=15)
        print(f"   Upload endpoint status: {response.status_code}")
        if response.status_code in [400, 422]:  # Expected error for missing file
            print("   ✅ API is working (expected error for missing file)")
        elif 'text/html' in response.headers.get('Content-Type', ''):
            print("   ❌ API returning HTML instead of JSON")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    # Test 4: Frontend service (for comparison)
    print("\n4. Testing frontend service...")
    try:
        response = requests.get("https://bible-outline-frontend.onrender.com", timeout=10)
        print(f"   Frontend status: {response.status_code}")
        print(f"   Frontend content-type: {response.headers.get('Content-Type', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
    
    return None

def main():
    """Main test function"""
    print("Starting backend service tests...\n")
    test_backend_service()
    
    print("\n=== Test Summary ===")
    print("The backend service appears to have deployment issues.")
    print("It's serving HTML content instead of the expected Flask API.")
    print("\nRecommendations:")
    print("1. Check Render service logs for deployment errors")
    print("2. Verify the service is using the correct start command")
    print("3. Ensure environment variables are properly set")
    print("4. Consider redeploying the backend service")

if __name__ == "__main__":
    main()