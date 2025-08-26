#!/usr/bin/env python3
"""
Test PDF text extraction directly
"""

import PyPDF2
from pathlib import Path

def test_pdf_extraction():
    """Test extracting text from W24ECT12"""
    
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: Cannot find {pdf_path}")
        return
    
    print(f"Testing PDF extraction: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB")
    
    # Extract text
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        print(f"Number of pages: {len(reader.pages)}")
        
        total_text_length = 0
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            total_text_length += len(text)
            print(f"  Page {i+1}: {len(text)} characters")
            if i == 0:
                print(f"  First 200 chars: {text[:200]}")
        
        print(f"\nTotal text length: {total_text_length} characters")
        
        if total_text_length > 3000:
            chunks_needed = (total_text_length // 2500) + 1
            print(f"Will need {chunks_needed} chunks for LLM processing")

if __name__ == "__main__":
    test_pdf_extraction()