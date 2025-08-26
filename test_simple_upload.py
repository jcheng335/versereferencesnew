#!/usr/bin/env python3
"""
Simple test for W24ECT12 upload
"""

import requests
from pathlib import Path

API_BASE = "http://localhost:5004/api"

def test_upload():
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: Cannot find {pdf_path}")
        return False
    
    print(f"Uploading {pdf_path.name}...")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path.name, f, 'application/pdf')}
        data = {'use_llm': 'true'}
        
        try:
            response = requests.post(
                f"{API_BASE}/enhanced/upload",
                files=files,
                data=data,
                timeout=45
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS!")
                print(f"  Session ID: {result.get('session_id')}")
                print(f"  References found: {result.get('references_found', 0)}")
                print(f"  Total verses: {result.get('total_verses', 0)}")
                
                if result.get('error'):
                    print(f"  Error: {result.get('error')}")
                    return False
                    
                return True
            else:
                print(f"FAILED: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"ERROR: {e}")
            return False

if __name__ == "__main__":
    success = test_upload()
    exit(0 if success else 1)