#!/usr/bin/env python3
"""
Test ultimate verse detector on all 12 outlines
Compares detection to expected counts from training data
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.ultimate_verse_detector import UltimateVerseDetector
import pdfplumber
import json

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
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def test_all_outlines():
    """Test detection on all 12 outlines"""
    
    detector = UltimateVerseDetector()
    
    # Expected counts from training data
    expected = {
        1: 59,
        2: 170,
        3: 30,
        4: 164,
        5: 53,
        6: 158,
        7: 74,
        8: 96,
        9: 59,
        10: 73,
        11: 47,
        12: 138
    }
    
    results = []
    total_detected = 0
    total_expected = 0
    
    print("="*80)
    print("TESTING ULTIMATE VERSE DETECTOR ON ALL 12 OUTLINES")
    print("="*80)
    
    for i in range(1, 13):
        # Get file path
        if i == 9:
            pdf_path = f"original outlines/W24ECT09en (1).pdf"
        elif i == 11:
            pdf_path = f"original outlines/W24ECT11en (1).pdf"
        else:
            pdf_path = f"original outlines/W24ECT{i:02d}en.pdf"
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        # Detect verses
        result = detector.extract_all_verses(text)
        
        detected_count = result['unique_count']
        expected_count = expected[i]
        accuracy = (detected_count / expected_count * 100) if expected_count > 0 else 0
        
        total_detected += detected_count
        total_expected += expected_count
        
        print(f"\nOutline {i:2d}: {detected_count:3d}/{expected_count:3d} verses ({accuracy:.1f}% accuracy)")
        
        # Show type distribution
        if result['type_distribution']:
            print(f"  Types: {', '.join(f'{k}:{v}' for k,v in result['type_distribution'].items())}")
        
        # Show confidence
        print(f"  Confidence: {result['average_confidence']:.2f} avg, {result['high_confidence_count']} high")
        
        # Sample verses
        if result['verses']:
            samples = result['verses'][:3]
            print(f"  Samples: {', '.join(v['reference'] for v in samples)}")
        
        results.append({
            'outline': i,
            'detected': detected_count,
            'expected': expected_count,
            'accuracy': accuracy,
            'details': result
        })
    
    # Overall summary
    overall_accuracy = (total_detected / total_expected * 100) if total_expected > 0 else 0
    
    print("\n" + "="*80)
    print("OVERALL RESULTS")
    print("="*80)
    print(f"Total Detected: {total_detected}/{total_expected} verses")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    # Find weak areas
    weak_outlines = [r for r in results if r['accuracy'] < 90]
    if weak_outlines:
        print(f"\nOutlines needing improvement (< 90% accuracy):")
        for r in weak_outlines:
            print(f"  Outline {r['outline']}: {r['accuracy']:.1f}%")
    else:
        print("\n✅ All outlines detected with 90%+ accuracy!")
    
    # Save results
    with open('ultimate_detection_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to ultimate_detection_results.json")
    
    return overall_accuracy >= 90

if __name__ == "__main__":
    success = test_all_outlines()
    sys.exit(0 if success else 1)