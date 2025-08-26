#!/usr/bin/env python3
"""
Final complete test - Process W24ECT12 and compare to Message_12 output
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.llm_first_detector import LLMFirstDetector
import PyPDF2
import json
from pathlib import Path

def load_expected_verses():
    """Load expected verses from Message_12"""
    with open('message_pdf_verses.json', 'r') as f:
        data = json.load(f)
    
    return data.get('W24ECT12', {}).get('verses', [])

def test_complete_detection():
    # Load OpenAI key
    from dotenv import load_dotenv
    load_dotenv('bible-outline-enhanced-backend/.env')
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: No OpenAI API key found")
        return
    
    # Initialize detector
    detector = LLMFirstDetector(api_key)
    print("LLM-first detector initialized")
    
    # Load W24ECT12 PDF
    pdf_path = Path("original outlines/W24ECT12en.pdf")
    
    print(f"\nProcessing: {pdf_path}")
    
    # Extract all text
    full_text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page_num in range(len(reader.pages)):
            full_text += reader.pages[page_num].extract_text() + "\n"
    
    print(f"Extracted {len(full_text)} characters from {len(reader.pages)} pages")
    
    # Detect verses
    print("\nDetecting verses with LLM (this may take a moment)...")
    detected_verses = detector.detect_verses(full_text, use_training=True)
    
    # Load expected verses
    expected_verses = load_expected_verses()
    
    # Analysis
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    
    print(f"Expected verses (from Message_12.pdf): {len(expected_verses)}")
    print(f"Detected verses: {len(detected_verses)}")
    
    accuracy = (len(detected_verses) / len(expected_verses)) * 100 if expected_verses else 0
    print(f"Detection rate: {accuracy:.1f}%")
    
    # Show sample detected verses
    print("\nSample detected verses (first 20):")
    for v in detected_verses[:20]:
        print(f"  - {v.original_text}")
    
    # Find missing verses
    detected_texts = {v.original_text for v in detected_verses}
    missing = [v for v in expected_verses if v not in detected_texts]
    
    if missing:
        print(f"\nMissing {len(missing)} verses. Sample missing:")
        for v in missing[:10]:
            print(f"  - {v}")
    
    # Success check
    if accuracy >= 95:
        print("\n✅ SUCCESS! Achieved excellent detection accuracy!")
    elif accuracy >= 85:
        print("\n✓ Good detection rate, minor improvements needed")
    else:
        print("\n⚠ Need to improve detection accuracy")
    
    # Save results
    results = {
        'expected_count': len(expected_verses),
        'detected_count': len(detected_verses),
        'accuracy': accuracy,
        'detected_verses': [v.original_text for v in detected_verses],
        'missing_verses': missing
    }
    
    with open('final_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to final_test_results.json")

if __name__ == "__main__":
    print("FINAL COMPLETE TEST - W24ECT12 Detection")
    print("="*60)
    test_complete_detection()