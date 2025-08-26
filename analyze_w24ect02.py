#!/usr/bin/env python3
"""
Analyze W24ECT02en.pdf to understand what verses need detection
"""

import pdfplumber
from pathlib import Path
import re

def analyze_pdf(pdf_path: str):
    """Extract and analyze content from W24ECT02en.pdf"""
    
    print("=" * 70)
    print(f"Analyzing: {pdf_path}")
    print("=" * 70)
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page_num, page in enumerate(pdf.pages[:2], 1):  # First 2 pages
            text = page.extract_text()
            if text:
                print(f"\n--- Page {page_num} Content (first 2000 chars) ---")
                print(text[:2000])
                full_text += text + "\n"
        
        # Look for verse patterns
        print("\n" + "=" * 70)
        print("Detected Verse Patterns in First 2 Pages:")
        print("-" * 70)
        
        # Multiple patterns to catch various formats
        patterns = [
            r'Scripture Reading:\s*([^\n]+)',  # Scripture Reading line
            r'\(([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?(?:;\s*\d+:\d+(?:-\d+)?)*)\)',  # Parenthetical
            r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?)',  # Standard references
            r'(vv?\.\s*\d+(?:-\d+)?)',  # v. or vv. references
            r'cf\.\s*([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+)',  # cf. references
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, full_text[:3000])
            if matches:
                print(f"\nPattern: {pattern[:50]}...")
                for match in matches[:10]:  # Show first 10
                    print(f"  - {match}")
                    all_matches.append(match)
        
        print(f"\nTotal verse-like patterns found in first 2 pages: {len(all_matches)}")

def analyze_ground_truth(pdf_path: str):
    """Extract verses from Message_2.pdf to see what we should find"""
    
    print("\n" + "=" * 70)
    print(f"Analyzing Ground Truth: {pdf_path}")
    print("=" * 70)
    
    with pdfplumber.open(pdf_path) as pdf:
        verses = []
        for page_num, page in enumerate(pdf.pages[:2], 1):
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    # Look for verse references (usually in specific format in output)
                    # Common patterns in Message output files
                    patterns = [
                        r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?)',
                        r'(vv?\.\s*\d+(?:-\d+)?)',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, line)
                        verses.extend(matches)
        
        # Deduplicate and show
        unique_verses = list(set(verses))
        print(f"\nUnique verses in first 2 pages of ground truth: {len(unique_verses)}")
        print("\nSample verses (first 20):")
        for v in unique_verses[:20]:
            print(f"  - {v}")

if __name__ == "__main__":
    input_file = "original outlines/W24ECT02en.pdf"
    ground_truth = "output outlines/Message_2.pdf"
    
    if Path(input_file).exists():
        analyze_pdf(input_file)
    else:
        print(f"Input file not found: {input_file}")
    
    if Path(ground_truth).exists():
        analyze_ground_truth(ground_truth)
    else:
        print(f"Ground truth not found: {ground_truth}")