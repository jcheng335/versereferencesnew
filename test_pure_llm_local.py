#!/usr/bin/env python3
"""
Test the Pure LLM detector locally with W24ECT02en.pdf
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.pure_llm_detector import PureLLMDetector
import pdfplumber

def test_w24ect02():
    """Test with W24ECT02en.pdf - Message Two"""
    
    # Load PDF
    pdf_path = "original outlines/W24ECT02en.pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    print(f"Extracted {len(text)} characters from PDF")
    print("\n=== FIRST 500 CHARS ===")
    print(text[:500])
    print("\n=== DETECTING VERSES ===")
    
    # Initialize detector
    detector = PureLLMDetector()
    
    # Detect verses
    verses = detector.detect_verses(text)
    
    print(f"\n=== RESULTS ===")
    print(f"Total verses detected: {len(verses)}")
    
    # Expected verses from Message_2
    expected = [
        "Rom. 8:2",
        "Rom. 8:31", "Rom. 8:32", "Rom. 8:33", "Rom. 8:34", "Rom. 8:35", 
        "Rom. 8:36", "Rom. 8:37", "Rom. 8:38", "Rom. 8:39"
    ]
    
    # Check detection
    detected_refs = [f"{v.book} {v.chapter}:{v.start_verse}" for v in verses]
    
    print("\n=== FIRST 20 DETECTED VERSES ===")
    for i, v in enumerate(verses[:20]):
        print(f"{i+1}. {v.book} {v.chapter}:{v.start_verse}{f'-{v.end_verse}' if v.end_verse else ''} ({v.original_text})")
    
    print("\n=== CHECKING EXPECTED VERSES ===")
    for exp in expected:
        # Normalize format
        exp_norm = exp.replace(".", "")
        found = any(exp_norm in f"{v.book} {v.chapter}:{v.start_verse}" for v in verses)
        status = "✓" if found else "✗"
        print(f"{status} {exp}")
    
    # Check for title
    print("\n=== CHECKING FOR TITLE ===")
    title_found = "Message Two" in text[:200]
    print(f"Title 'Message Two': {'✓' if title_found else '✗'}")
    
    # Check for Scripture Reading expansion
    scripture_reading_verses = [v for v in verses if v.book == "Romans" and v.chapter == 8 and 31 <= v.start_verse <= 39]
    print(f"\n=== SCRIPTURE READING EXPANSION ===")
    print(f"Found {len(scripture_reading_verses)} verses from Rom. 8:31-39")
    print("Expected: 9 verses (31, 32, 33, 34, 35, 36, 37, 38, 39)")

if __name__ == "__main__":
    test_w24ect02()