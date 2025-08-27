#!/usr/bin/env python3
"""
Test W24ECT02en.pdf with deployed Bible outline backend
Tests all required elements as specified
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BACKEND_URL = "https://bible-outline-backend.onrender.com"
PDF_PATH = Path("./original outlines/W24ECT02en.pdf")

def test_deployment():
    """Test the deployed backend with W24ECT02en.pdf"""
    
    print("=== Testing W24ECT02en.pdf with Deployed Backend ===")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"PDF Path: {PDF_PATH}")
    
    # Check if PDF file exists
    if not PDF_PATH.exists():
        print(f"[FAIL] PDF file not found at {PDF_PATH}")
        return False
    
    print(f"[OK] PDF file found: {PDF_PATH}")
    
    # Step 1: Upload the file to /api/enhanced/upload
    print("\n=== Step 1: Upload PDF ===")
    
    try:
        with open(PDF_PATH, 'rb') as pdf_file:
            files = {'file': ('W24ECT02en.pdf', pdf_file, 'application/pdf')}
            data = {'use_llm': 'true'}
            
            response = requests.post(
                f"{BACKEND_URL}/api/enhanced/upload",
                files=files,
                data=data,
                timeout=60
            )
            
            print(f"Upload status code: {response.status_code}")
            print(f"Upload response: {response.text[:500]}...")
            
            if response.status_code != 200:
                print(f"[FAIL] Upload failed with status {response.status_code}")
                return False
                
            upload_result = response.json()
            session_id = upload_result.get('session_id')
            
            if not session_id:
                print("[FAIL] No session_id in upload response")
                return False
                
            print(f"[OK] Upload successful, session_id: {session_id}")
            print(f"References found: {upload_result.get('references_found', 'N/A')}")
            print(f"Total verses: {upload_result.get('total_verses', 'N/A')}")
            
    except Exception as e:
        print(f"[FAIL] Upload error: {str(e)}")
        return False
    
    # Step 2: Populate with margin format
    print(f"\n=== Step 2: Populate with session_id {session_id} ===")
    
    try:
        populate_data = {"format": "margin"}
        response = requests.post(
            f"{BACKEND_URL}/api/enhanced/populate/{session_id}",
            json=populate_data,
            timeout=60
        )
        
        print(f"Populate status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[FAIL] Populate failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        html_content = response.text
        print(f"[OK] Populate successful, HTML length: {len(html_content)}")
        
    except Exception as e:
        print(f"[FAIL] Populate error: {str(e)}")
        return False
    
    # Step 3: Save HTML response
    print(f"\n=== Step 3: Save HTML Response ===")
    
    try:
        output_file = "W24ECT02en_test_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[OK] HTML saved to: {output_file}")
        
    except Exception as e:
        print(f"[FAIL] Save HTML error: {str(e)}")
        return False
    
    # Step 4: Verify key elements
    print(f"\n=== Step 4: Verify Key Elements ===")
    
    results = {}
    
    # Check for "Message Two" title
    if "Message Two" in html_content:
        print("[OK] Found 'Message Two' title")
        results['message_two_title'] = True
    else:
        print("[FAIL] Missing 'Message Two' title")
        results['message_two_title'] = False
    
    # Check for "Christ as the Emancipator" subtitle
    if "Christ as the Emancipator" in html_content:
        print("[OK] Found 'Christ as the Emancipator' subtitle")
        results['christ_emancipator_subtitle'] = True
    else:
        print("[FAIL] Missing 'Christ as the Emancipator' subtitle")
        results['christ_emancipator_subtitle'] = False
    
    # Check for Scripture Reading section
    if "Scripture Reading" in html_content:
        print("[OK] Found 'Scripture Reading' section")
        results['scripture_reading_section'] = True
    else:
        print("[FAIL] Missing 'Scripture Reading' section")
        results['scripture_reading_section'] = False
    
    # Check for Rom. 8:2 verse
    if "Rom. 8:2" in html_content or "Romans 8:2" in html_content:
        print("[OK] Found Romans 8:2 reference")
        results['rom_8_2'] = True
    else:
        print("[FAIL] Missing Romans 8:2 reference")
        results['rom_8_2'] = False
    
    # Check for Rom. 8:31-39 verses
    if "Rom. 8:31-39" in html_content or "Romans 8:31-39" in html_content:
        print("[OK] Found Romans 8:31-39 reference")
        results['rom_8_31_39'] = True
    else:
        print("[FAIL] Missing Romans 8:31-39 reference")
        results['rom_8_31_39'] = False
    
    # Check for blue color styling
    if "blue" in html_content or "#0000FF" in html_content or "color: #" in html_content:
        print("[OK] Found blue color styling")
        results['blue_color'] = True
    else:
        print("[FAIL] Missing blue color styling")
        results['blue_color'] = False
    
    # Check for Roman numeral I
    if ">I.<" in html_content or "I. " in html_content:
        print("[OK] Found Roman numeral I")
        results['roman_numeral_i'] = True
    else:
        print("[FAIL] Missing Roman numeral I")
        results['roman_numeral_i'] = False
    
    # Summary
    print(f"\n=== Final Results ===")
    passed = sum(results.values())
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return True
    else:
        print(f"\n[WARNING] {total - passed} TESTS FAILED")
        return False

if __name__ == "__main__":
    success = test_deployment()
    exit(0 if success else 1)