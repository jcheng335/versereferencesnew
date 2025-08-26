#!/usr/bin/env python3
"""
Test detection accuracy with W24ECT12
"""

import requests
import json
from pathlib import Path

API_BASE = "http://localhost:5004/api"

def test_detection_accuracy():
    """Test the current detection accuracy"""
    
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print("ERROR: Cannot find W24ECT12en.pdf")
        return
    
    print(f"Testing with: {pdf_path}")
    
    # Upload the file
    with open(pdf_path, 'rb') as f:
        files = {'file': ('W24ECT12en.pdf', f, 'application/pdf')}
        data = {'use_llm': 'true'}
        
        print("\n1. Uploading W24ECT12en.pdf...")
        response = requests.post(
            f"{API_BASE}/enhanced/upload",
            files=files,
            data=data,
            timeout=120  # 2 minute timeout
        )
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return
    
    result = response.json()
    session_id = result.get('session_id')
    
    print(f"[OK] Upload successful!")
    print(f"  Session ID: {session_id}")
    print(f"  References found: {result.get('references_found', 0)}")
    print(f"  Total verses: {result.get('total_verses', 0)}")
    
    # Expected verses from Message_12.pdf
    expected_verses = 234
    detected = result.get('total_verses', 0)
    
    if detected > 0:
        accuracy = (detected / expected_verses) * 100
        print(f"\nAccuracy Report:")
        print(f"  Expected: {expected_verses} verses")
        print(f"  Detected: {detected} verses")
        print(f"  Accuracy: {accuracy:.1f}%")
        
        if accuracy >= 70:
            print("\n[SUCCESS] Good detection accuracy achieved!")
        else:
            print(f"\n[INFO] Detection at {accuracy:.1f}%, needs improvement")
    else:
        print("\n[WARNING] No verses detected")
    
    # Save results
    with open('test_results.txt', 'w') as f:
        f.write(f"Test Results\n")
        f.write(f"Expected: {expected_verses}\n")
        f.write(f"Detected: {detected}\n")
        f.write(f"Session: {session_id}\n")

if __name__ == "__main__":
    print("Testing Detection Accuracy")
    print("="*40)
    test_detection_accuracy()