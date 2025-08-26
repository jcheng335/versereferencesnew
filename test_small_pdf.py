#!/usr/bin/env python3
"""
Test with small text content to isolate the issue
"""

import requests
from pathlib import Path
import tempfile
from reportlab.pdfgen import canvas

API_BASE = "http://localhost:5004/api"

def create_small_pdf():
    """Create a small test PDF"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        pdf_path = f.name
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 750, "Scripture Reading: Rom. 5:1-11")
        c.drawString(100, 730, "I. Justification (v. 1)")
        c.save()
        return pdf_path

def test_small_upload():
    """Test with very small PDF"""
    
    print("Creating small test PDF...")
    pdf_path = create_small_pdf()
    
    try:
        print(f"Uploading small test PDF...")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            data = {'use_llm': 'false'}  # Disable LLM for speed
            
            response = requests.post(
                f"{API_BASE}/enhanced/upload",
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("[SUCCESS] Upload completed!")
                print(f"Session ID: {result.get('session_id')}")
                print(f"References found: {result.get('references_found', 0)}")
            else:
                print(f"[ERROR] Status {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        import os
        os.remove(pdf_path)

if __name__ == "__main__":
    print("Testing Small PDF Upload")
    print("="*40)
    test_small_upload()