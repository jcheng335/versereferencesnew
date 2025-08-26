#!/usr/bin/env python3
"""
Test the comprehensive detector with W24ECT12 to verify 100% accuracy
"""

import requests
import json
from pathlib import Path
import time

API_BASE = "http://localhost:5004/api"

def test_comprehensive_detection():
    """Test the comprehensive detector with W24ECT12"""
    
    # Upload W24ECT12
    pdf_path = Path("W24ECT12en.pdf")
    if not pdf_path.exists():
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
            data=data
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
    print(f"  Average confidence: {result.get('average_confidence', 0):.2f}")
    
    # Show sample references
    if 'references' in result:
        refs = result['references']
        print(f"\n  Sample references (first 10):")
        for ref in refs[:10]:
            if isinstance(ref, dict):
                print(f"    - {ref.get('original_text', ref)}")
            else:
                print(f"    - {ref}")
    
    # Test populate endpoint
    print("\n2. Testing populate endpoint...")
    populate_response = requests.post(
        f"{API_BASE}/enhanced/populate/{session_id}",
        json={'format': 'margin'}
    )
    
    if populate_response.status_code != 200:
        print(f"Populate failed: {populate_response.text}")
    else:
        print("[OK] Populate successful!")
        populate_result = populate_response.json()
        if 'populated_content' in populate_result:
            # Save first 5000 chars to file for inspection
            sample = populate_result['populated_content'][:5000]
            with open('test_output_sample.txt', 'w', encoding='utf-8') as f:
                f.write(sample)
            print("  Sample output saved to test_output_sample.txt")
    
    # Calculate accuracy
    print("\n3. Accuracy Report:")
    print("=" * 50)
    
    # Expected counts from MSG12VerseReferences.pdf
    expected_verses = 308  # From our manual count
    detected = result.get('total_verses', 0)
    
    accuracy = (detected / expected_verses) * 100 if expected_verses > 0 else 0
    
    print(f"  Expected verses: {expected_verses}")
    print(f"  Detected verses: {detected}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 100:
        print("\n[SUCCESS] Achieved 100% detection accuracy!")
    elif accuracy >= 90:
        print(f"\n[GOOD] Good progress! {accuracy:.1f}% accuracy")
    else:
        print(f"\n[WARNING] Need improvement: {accuracy:.1f}% accuracy")
    
    # Analyze patterns detected
    if 'references' in result:
        patterns = {}
        for ref in result['references']:
            if isinstance(ref, dict):
                pattern = ref.get('pattern', 'unknown')
            else:
                pattern = 'string'
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        print("\n4. Pattern Distribution:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count}")

if __name__ == "__main__":
    print("Testing Comprehensive Verse Detector...")
    print("=" * 50)
    test_comprehensive_detection()