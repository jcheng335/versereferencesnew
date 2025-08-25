#!/usr/bin/env python3
"""
Test script for document upload functionality
"""

import requests
import json

def test_document_upload():
    """Test document upload API"""
    url = "http://localhost:5001/api/document/upload"
    
    # Test file upload
    with open("/home/ubuntu/upload/W24ECT11en_unlocked.pdf", "rb") as f:
        files = {"file": ("W24ECT11en_unlocked.pdf", f, "application/pdf")}
        
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Upload successful!")
                    print(f"Session ID: {data.get('session_id')}")
                    print(f"References found: {data.get('reference_count')}")
                    print(f"Detected references: {data.get('detected_references')}")
                    return data.get('session_id')
                else:
                    print(f"❌ Upload failed: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

def test_populate_verses(session_id):
    """Test verse population"""
    if not session_id:
        print("❌ No session ID to test with")
        return
    
    url = "http://localhost:5001/api/document/process-document"
    data = {
        "session_id": session_id,
        "format": "inline"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\n--- Populate Verses Test ---")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Verse population successful!")
                print(f"References processed: {len(result.get('references', []))}")
                print(f"Verses found: {len(result.get('verses', []))}")
                
                # Show first few verses
                verses = result.get('verses', [])[:3]
                for verse in verses:
                    print(f"  - {verse.get('reference')}: {verse.get('text')[:100]}...")
            else:
                print(f"❌ Population failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Bible Outline Document Upload...")
    
    # Test upload
    session_id = test_document_upload()
    
    # Test verse population
    if session_id:
        test_populate_verses(session_id)
    
    print("\n✅ Test completed!")

