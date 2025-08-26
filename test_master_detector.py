#!/usr/bin/env python3
"""
Test master detector on W24ECT12 
Goal: Achieve 100% accuracy (308 verses)
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.master_verse_detector import MasterVerseDetector
import pdfplumber

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

def test_master_detector():
    """Test master detector on W24ECT12"""
    
    # Initialize detector (no OpenAI key for now)
    detector = MasterVerseDetector()
    
    # Extract text from W24ECT12
    text = extract_text_from_pdf("original outlines/W24ECT12en.pdf")
    
    if not text:
        print("Error: Could not extract text from PDF")
        return
    
    # Detect verses
    result = detector.extract_all_verses(text)
    
    print("="*80)
    print("MASTER VERSE DETECTOR TEST - W24ECT12")
    print("="*80)
    
    print(f"\nTotal verses detected: {result['unique_count']}")
    print(f"Target from MSG12: 308 verses")
    print(f"Detection rate: {(result['unique_count']/308)*100:.1f}%")
    
    print(f"\nAverage confidence: {result['average_confidence']:.2f}")
    
    print("\nConfidence levels:")
    for level, count in result['confidence_levels'].items():
        print(f"  {level}: {count}")
    
    print("\nSource distribution:")
    for source, count in sorted(result['source_distribution'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {source}: {count}")
    
    print("\nFirst 20 detected verses:")
    for i, verse in enumerate(result['verses'][:20], 1):
        ref = f"{verse['book']} {verse['chapter']}"
        if verse.get('start_verse'):
            ref += f":{verse['start_verse']}"
            if verse.get('end_verse') and verse['end_verse'] != verse['start_verse']:
                ref += f"-{verse['end_verse']}"
        print(f"  {i:2d}. {ref} (conf: {verse['confidence']:.2f}, src: {verse['source']})")
    
    # Check specific verses that should be found
    expected_samples = [
        "Eph 4:7-16", "Eph 6:10-20",  # Scripture Reading
        "Eph 4:7", "1Cor 12:14", "Rom 12:4",  # Main references
    ]
    
    detected_refs = []
    for v in result['verses']:
        ref = f"{v['book']} {v['chapter']}"
        if v.get('start_verse'):
            ref += f":{v['start_verse']}"
            if v.get('end_verse') and v['end_verse'] != v['start_verse']:
                ref += f"-{v['end_verse']}"
        detected_refs.append(ref)
    
    print("\nChecking key verses:")
    for exp in expected_samples:
        # Normalize for comparison
        exp_norm = exp.replace(' ', '').lower()
        found = any(ref.replace(' ', '').lower() == exp_norm for ref in detected_refs)
        status = "FOUND" if found else "MISSING"
        print(f"  [{status}] {exp}")
    
    # Overall assessment
    detection_rate = result['unique_count'] / 308 * 100
    if detection_rate >= 90:
        print(f"\n✅ EXCELLENT: {detection_rate:.1f}% detection rate!")
    elif detection_rate >= 70:
        print(f"\n⚠️ GOOD: {detection_rate:.1f}% detection rate")
    else:
        print(f"\n❌ NEEDS IMPROVEMENT: {detection_rate:.1f}% detection rate")
    
    # Suggest improvements if needed
    if detection_rate < 90:
        print("\nSuggestions for improvement:")
        print("1. Add OpenAI API key for LLM detection")
        print("2. Fine-tune patterns based on MSG12VerseReferences")
        print("3. Extract training data from all 12 MSG complete files")
    
    return result

if __name__ == "__main__":
    result = test_master_detector()