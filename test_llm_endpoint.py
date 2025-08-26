#!/usr/bin/env python3
"""
Test the test-llm endpoint directly
"""

import requests
import json

API_BASE = "http://localhost:5004/api"

def test_llm():
    """Test LLM detection with simple text"""
    
    test_text = """
    Scripture Reading: Eph. 4:7-16; 6:10-20
    
    I. Christ ascended to the heavens (Psalm 68:18)
    
    A. According to v. 11, He gave gifts
    B. See also Rom. 12:3
    """
    
    print("Testing LLM detection with sample text...")
    
    try:
        response = requests.post(
            f"{API_BASE}/enhanced/test-llm",
            json={"text": test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] LLM test completed!")
            print(f"References found: {result.get('references_found', 0)}")
            print(f"LLM available: {result.get('llm_available')}")
            
            if result.get('references'):
                print("\nDetected verses:")
                for ref in result['references']:
                    print(f"  - {ref['book']} {ref['chapter']}:{ref['start_verse']}" +
                          (f"-{ref['end_verse']}" if ref.get('end_verse') else ""))
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    print("Testing LLM Endpoint")
    print("="*40)
    test_llm()