#!/usr/bin/env python3
"""
Test the Bible outline backend upload functionality with the actual PDF
"""
import requests
import json
import time
import os

def test_upload():
    base_url = "https://bible-outline-backend.onrender.com"
    pdf_path = "./original outlines/W24ECT02en.pdf"
    
    print("=== Testing PDF Upload ===\n")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print("ERROR: PDF file not found!")
        return None
    
    file_size = os.path.getsize(pdf_path)
    print(f"File: {pdf_path}")
    print(f"Size: {file_size} bytes ({file_size/1024:.1f} KB)")
    
    # Test upload with timeout
    print("\nAttempting upload...")
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('W24ECT02en.pdf', f, 'application/pdf')}
            data = {'use_llm': 'true'}
            
            response = requests.post(
                f"{base_url}/api/enhanced/upload",
                files=files,
                data=data,
                timeout=120  # 2 minute timeout
            )
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("SUCCESS! Upload completed.")
                print(f"Session ID: {result.get('session_id', 'N/A')}")
                print(f"References Found: {result.get('references_found', 'N/A')}")
                print(f"Total Verses: {result.get('total_verses', 'N/A')}")
                return result.get('session_id')
            except json.JSONDecodeError:
                print("ERROR: Invalid JSON response")
                print(f"Response: {response.text[:500]}...")
        else:
            print(f"ERROR: Upload failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except requests.Timeout:
        print("ERROR: Upload timed out after 2 minutes")
    except Exception as e:
        print(f"ERROR: Upload failed - {e}")
    
    return None

def test_populate(session_id):
    """Test the populate endpoint with the session ID"""
    if not session_id:
        print("No session ID to test populate")
        return
        
    base_url = "https://bible-outline-backend.onrender.com"
    print(f"\n=== Testing Populate with Session {session_id} ===")
    
    try:
        response = requests.post(
            f"{base_url}/api/enhanced/populate/{session_id}",
            json={"format": "margin"},
            timeout=60
        )
        
        print(f"Populate Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Populate completed")
            print(f"Response length: {len(response.text)} characters")
            # Show first few lines
            lines = response.text.split('\n')[:10]
            print("\nFirst 10 lines of output:")
            for i, line in enumerate(lines, 1):
                print(f"{i:2d}: {line[:80]}...")
        else:
            print(f"ERROR: {response.text[:200]}...")
            
    except Exception as e:
        print(f"ERROR: Populate failed - {e}")

def main():
    session_id = test_upload()
    if session_id:
        test_populate(session_id)
    else:
        print("\nUpload failed, cannot test populate endpoint")

if __name__ == "__main__":
    main()