#!/usr/bin/env python3
"""
Test the LLM-first detector directly
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.llm_first_detector import LLMFirstDetector
import PyPDF2
from pathlib import Path

def test_llm_detector():
    # Load OpenAI key
    from dotenv import load_dotenv
    load_dotenv('bible-outline-enhanced-backend/.env')
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: No OpenAI API key found")
        return
    
    print(f"OpenAI key loaded (length: {len(api_key)})")
    
    # Initialize detector
    try:
        detector = LLMFirstDetector(api_key)
        print("LLM-first detector initialized successfully")
    except Exception as e:
        print(f"Failed to initialize detector: {e}")
        return
    
    # Load W24ECT12 PDF
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    print(f"\nTesting with: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Extract text from first page for testing
            text = reader.pages[0].extract_text()
            
            print(f"Extracted {len(text)} characters from first page")
            print("\nSample text (first 300 chars):")
            print(text[:300])
            
            # Detect verses
            print("\nDetecting verses with LLM...")
            verses = detector.detect_verses(text[:2000], use_training=True)  # Use first 2000 chars
            
            print(f"\nFound {len(verses)} verses:")
            for v in verses:
                print(f"  - {v.original_text} ({v.book} {v.chapter}:{v.start_verse})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_detector()