#!/usr/bin/env python3
"""
Test HTML conversion directly
"""

from pathlib import Path
import sys
sys.path.insert(0, 'bible-outline-enhanced-backend/src')

from utils.pdf_to_html_converter import PDFToHTMLConverter

def test_conversion():
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: Cannot find {pdf_path}")
        return
    
    converter = PDFToHTMLConverter()
    
    # Test structured conversion
    print("Testing structured conversion...")
    structured = converter.convert_and_structure(str(pdf_path))
    
    print(f"Title: {structured['title']}")
    print(f"Scripture Reading: {structured['scripture_reading']}")
    print(f"Number of outline points: {len(structured['outline_points'])}")
    
    # Show first few points
    print("\nFirst 10 outline points:")
    for i, point in enumerate(structured['outline_points'][:10]):
        print(f"  {i+1}. Level {point['level']}: {point['text'][:80]}...")
        if point['verses']:
            print(f"     Verses detected in converter: {point['verses']}")
    
    # Count total text
    all_text = structured['title'] + "\n" + structured['scripture_reading'] + "\n"
    for point in structured['outline_points']:
        all_text += point['text'] + "\n"
    
    print(f"\nTotal text length: {len(all_text)} chars")
    
    # Check for specific verses we know should be there
    known_verses = ["Eph. 4:7-16", "6:10-20", "Psalm 68:18", "Num. 10:35", "Acts 2:33"]
    print(f"\nChecking for known verses in text:")
    for verse in known_verses:
        if verse in all_text:
            print(f"  ✓ Found: {verse}")
        else:
            print(f"  ✗ Missing: {verse}")

if __name__ == "__main__":
    test_conversion()