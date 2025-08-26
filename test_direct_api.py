#!/usr/bin/env python3
"""
Test the API directly with a small sample
"""

import requests
import json

API_BASE = "http://localhost:5004/api"

def test_api():
    """Test with simple text"""
    
    test_text = """
    Scripture Reading: Eph. 4:7-16; 6:10-20
    
    I. Christ ascended to the heavens (Psalm 68:18) to give gifts—Num. 10:35; Acts 2:33; 
       Eph. 4:8; Psalm 68:11-12, 19
       
    A. According to Eph. 4:11, He gave the apostles, prophets, evangelists, and 
       shepherds and teachers
       
    B. These are persons with the spiritual gifts (Rom. 12:6-8; 1 Cor. 12:28; Eph. 4:7)
    
    II. The function of the gifted persons is for the perfecting of the saints (v. 12)
    
    A. Unto the work of ministry (v. 12)
    B. Unto the building up of the Body of Christ (vv. 12, 16)
    """
    
    print("Testing enhanced upload endpoint...")
    
    # Create a temporary text file to upload
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_text)
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_outline.txt', f, 'text/plain')}
            data = {'use_llm': 'true'}
            
            response = requests.post(
                f"{API_BASE}/enhanced/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"[SUCCESS] Upload completed!")
                print(f"  Session ID: {result.get('session_id')}")
                print(f"  References found: {result.get('references_found', 0)}")
                print(f"  Total verses: {result.get('total_verses', 0)}")
                
                if result.get('detected_references'):
                    print("\nFirst 5 detected references:")
                    for ref in result['detected_references'][:5]:
                        print(f"  - {ref.get('book')} {ref.get('chapter')}:{ref.get('start_verse')}")
            else:
                print(f"[ERROR] Status {response.status_code}")
                print(f"Response: {response.text}")
    
    finally:
        import os
        os.remove(temp_file)

if __name__ == "__main__":
    print("Testing Direct API")
    print("="*40)
    test_api()