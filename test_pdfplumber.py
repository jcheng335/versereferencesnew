#!/usr/bin/env python3
"""
Test pdfplumber extraction directly
"""

import pdfplumber
from pathlib import Path
import time

def test_pdfplumber():
    """Test extracting text with pdfplumber"""
    
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: Cannot find {pdf_path}")
        return
    
    print(f"Testing pdfplumber extraction: {pdf_path}")
    
    start_time = time.time()
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Number of pages: {len(pdf.pages)}")
            
            total_text = ""
            for i, page in enumerate(pdf.pages):
                print(f"  Extracting page {i+1}...")
                page_text = page.extract_text()
                if page_text:
                    total_text += page_text + "\n"
                    print(f"    Got {len(page_text)} characters")
        
        elapsed = time.time() - start_time
        print(f"\nExtraction completed in {elapsed:.2f} seconds")
        print(f"Total text length: {len(total_text)} characters")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdfplumber()