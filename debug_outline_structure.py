"""
Debug script to analyze outline structure without tiktoken
"""
import os
import sys
import pdfplumber
from dotenv import load_dotenv
import json
import re

def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def main():
    # Extract text from PDF
    pdf_path = 'W24ECT12en.pdf'
    if not os.path.exists(pdf_path):
        print(f"PDF file {pdf_path} not found")
        return
    
    text = extract_pdf_text(pdf_path)
    
    print(f"Full text length: {len(text)} characters")
    
    # Look for all major outline points
    major_points = re.findall(r'^[IVX]+\.', text, re.MULTILINE)
    print(f"\nMajor outline points found: {major_points}")
    
    # Look for sub-points
    sub_points = re.findall(r'^\s*[A-Z]\.', text, re.MULTILINE)
    print(f"Sub-points found: {sub_points}")
    
    # Check if there's a "II." section
    if "II." in text:
        print("\n'II.' found in text - should be detected!")
        ii_index = text.find("II.")
        print(f"II. appears at character {ii_index}")
        print(f"Context around II.:\n{text[ii_index-100:ii_index+300]}")
    else:
        print("\n'II.' not found in text")
        
    # Show where the text ends around point I
    i_index = text.find("I.")
    if i_index != -1:
        # Find the end of section I by looking for section II or end of text
        ii_index = text.find("II.", i_index)
        if ii_index != -1:
            section_i = text[i_index:ii_index]
            print(f"\nSection I length: {len(section_i)} characters")
            print(f"Section I ends with:\n{section_i[-200:]}")
        else:
            print(f"\nNo Section II found after Section I")
            print(f"Text after Section I (last 500 chars):\n{text[i_index:i_index+2000]}")
    
    # Count all verse references manually
    verse_patterns = [
        r'\b\d?\s?[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*',  # Rom. 5:1-11
        r'\bv\.\s*\d+',  # v. 5
        r'\bvv\.\s*\d+(?:-\d+)?',  # vv. 1-11
        r'\([A-Z][a-z]+\.?\s+\d+:\d+\)',  # (Acts 10:43)
        r'\b[A-Z][a-z]+\.?\s+\d+:\d+[a-z]?',  # John 14:6a
    ]
    
    total_refs = 0
    for pattern in verse_patterns:
        matches = re.findall(pattern, text)
        total_refs += len(matches)
        if matches:
            print(f"\nPattern {pattern} found {len(matches)} matches:")
            print(matches[:10])  # Show first 10
    
    print(f"\nTotal verse references found by regex: {total_refs}")

if __name__ == "__main__":
    main()