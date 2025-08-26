#!/usr/bin/env python3
"""
Test W24ECT12 upload with tracing
"""

import requests
from pathlib import Path
import time

API_BASE = "http://localhost:5004/api"

def test_w24ect12():
    """Test W24ECT12 upload with progress tracking"""
    
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: Cannot find {pdf_path}")
        return
    
    print(f"Testing with: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB")
    
    # Test without LLM first (faster)
    print("\n1. Testing WITHOUT LLM (regex only)...")
    with open(pdf_path, 'rb') as f:
        files = {'file': ('W24ECT12en.pdf', f, 'application/pdf')}
        data = {'use_llm': 'false'}
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE}/enhanced/upload",
                files=files,
                data=data,
                timeout=15  # 15 second timeout
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"[SUCCESS] Completed in {elapsed:.1f} seconds")
                print(f"  Session ID: {result.get('session_id')}")
                print(f"  References found: {result.get('references_found', 0)}")
                print(f"  Total verses: {result.get('total_verses', 0)}")
            else:
                print(f"[ERROR] Status {response.status_code} after {elapsed:.1f} seconds")
                print(f"Response: {response.text[:500]}")
                
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] After 15 seconds")
        except Exception as e:
            print(f"[ERROR] {e}")
    
    # Test with LLM
    print("\n2. Testing WITH LLM (GPT-4)...")
    with open(pdf_path, 'rb') as f:
        files = {'file': ('W24ECT12en.pdf', f, 'application/pdf')}
        data = {'use_llm': 'true'}
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE}/enhanced/upload",
                files=files,
                data=data,
                timeout=60  # 60 second timeout for LLM
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"[SUCCESS] Completed in {elapsed:.1f} seconds")
                print(f"  Session ID: {result.get('session_id')}")
                print(f"  References found: {result.get('references_found', 0)}")
                print(f"  Total verses: {result.get('total_verses', 0)}")
            else:
                print(f"[ERROR] Status {response.status_code} after {elapsed:.1f} seconds")
                print(f"Response: {response.text[:500]}")
                
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] After 60 seconds")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    print("Testing W24ECT12 Upload")
    print("="*40)
    test_w24ect12()