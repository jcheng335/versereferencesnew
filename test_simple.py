#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "https://bible-outline-backend.onrender.com"
    
    print("=== Bible Outline Backend Test ===\n")
    
    # Test basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        if 'text/html' in str(response.headers.get('Content-Type', '')):
            print("   WARNING: Backend serving HTML instead of API")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test API upload endpoint
    print("\n2. Testing upload endpoint...")
    try:
        response = requests.post(f"{base_url}/api/enhanced/upload", json={}, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
        if response.status_code == 400 and "No file provided" in response.text:
            print("   SUCCESS: API is working (expected error)")
            return True
        else:
            print("   ERROR: Unexpected response")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    print(f"\nResult: {'PASS' if success else 'FAIL'}")