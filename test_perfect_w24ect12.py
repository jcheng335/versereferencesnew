#!/usr/bin/env python3
"""
Test perfect detector on W24ECT12 
Compare to MSG12VerseReferences expected output
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.perfect_verse_detector import PerfectVerseDetector
import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

def extract_msg12_verses():
    """Extract all verses from MSG12VerseReferences to get expected count"""
    # Based on visual inspection of MSG12VerseReferences.pdf
    # Page 1 alone has these verses:
    expected_verses = [
        "Eph 4:7-16", "Eph 6:10-20",  # Scripture Reading
        "Eph 4:7", "Eph 4:8", "Eph 4:9", "Eph 4:10", "Eph 4:11", 
        "Eph 4:12", "Eph 4:13", "Eph 4:14", "Eph 4:15", "Eph 4:16",
        "Eph 6:10", "Eph 6:11", "Eph 6:12", "Eph 6:13", "Eph 6:14",
        "Eph 6:15", "Eph 6:16", "Eph 6:17", "Eph 6:18", "Eph 6:19", "Eph 6:20",
        "1 Cor 12:14-22", "Rom 12:4-5", "1 Cor 12:14", "1 Cor 12:15",
        "1 Cor 12:16", "1 Cor 12:17", "1 Cor 12:18", "1 Cor 12:19",
        "1 Cor 12:20", "1 Cor 12:21", "1 Cor 12:22", 
        "Rom 12:4", "Rom 12:5", "2 Cor 1:15"
    ]
    # This is just page 1 - MSG12 has 10 pages with 200+ total verses
    return expected_verses

def test_w24ect12():
    """Test perfect detector on W24ECT12"""
    
    detector = PerfectVerseDetector()
    
    # Extract text from W24ECT12
    text = extract_text_from_pdf("W24ECT12en.pdf")
    
    # Detect verses
    result = detector.extract_all_verses(text)
    
    print("="*80)
    print("PERFECT VERSE DETECTOR TEST - W24ECT12")
    print("="*80)
    
    print(f"\nTotal verses detected: {result['unique_count']}")
    print(f"Expected from MSG12: 200+ verses")
    
    print(f"\nConfidence: {result['average_confidence']:.2f}")
    print(f"High confidence verses: {result['high_confidence_count']}")
    
    print("\nType distribution:")
    for verse_type, count in sorted(result['type_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {verse_type}: {count}")
    
    print("\nFirst 20 detected verses:")
    for i, verse in enumerate(result['verses'][:20], 1):
        print(f"  {i:2d}. {verse['reference']} ({verse['type']})")
    
    # Check specific verses that should be found
    expected_samples = [
        "Eph 4:7-16", "Eph 6:10-20",  # Scripture Reading
        "Eph 4:7", "1 Cor 12:14", "Rom 12:4",  # Main references
    ]
    
    detected_refs = [v['reference'] for v in result['verses']]
    
    print("\nChecking key verses:")
    for exp in expected_samples:
        # Check if verse is found (with flexible matching)
        found = any(exp in ref or ref in exp for ref in detected_refs)
        status = "✓" if found else "✗"
        print(f"  {status} {exp}")
    
    # Overall assessment
    if result['unique_count'] >= 150:
        print("\n✅ EXCELLENT: Detected 150+ verses (75%+ of expected)")
    elif result['unique_count'] >= 100:
        print("\n⚠️ GOOD: Detected 100+ verses (50%+ of expected)")
    else:
        print("\n❌ NEEDS IMPROVEMENT: Detected < 100 verses")
    
    return result

if __name__ == "__main__":
    result = test_w24ect12()