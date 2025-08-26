#!/usr/bin/env python3
"""
Simple test to verify parameter mismatch error is fixed
"""

import requests
from pathlib import Path

API_BASE = "http://localhost:5004/api"

def test_upload():
    """Test simple upload"""
    
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print("ERROR: Cannot find W24ECT12en.pdf")
        return
    
    print(f"Testing upload with: {pdf_path}")
    
    # Upload the file
    with open(pdf_path, 'rb') as f:
        files = {'file': ('W24ECT12en.pdf', f, 'application/pdf')}
        data = {'use_llm': 'true'}
        
        print("\nUploading W24ECT12en.pdf...")
        try:
            response = requests.post(
                f"{API_BASE}/enhanced/upload",
                files=files,
                data=data,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print("[SUCCESS] Upload completed without errors!")
                print(f"Session ID: {result.get('session_id')}")
                print(f"References found: {result.get('references_found', 0)}")
                print(f"Total verses: {result.get('total_verses', 0)}")
            else:
                print(f"[ERROR] Upload failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("[ERROR] Request timed out after 30 seconds")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    print("Testing Parameter Fix")
    print("="*40)
    test_upload()