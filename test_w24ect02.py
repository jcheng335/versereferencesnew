#!/usr/bin/env python3
"""
Comprehensive test of W24ECT02en.pdf against Message_2 ground truth
"""

import os
import sys
import json
import re
from pathlib import Path
import pdfplumber
from typing import List, Set, Dict

# Add backend src to path
backend_src = Path(__file__).parent / "bible-outline-enhanced-backend" / "src"
sys.path.insert(0, str(backend_src))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / "bible-outline-enhanced-backend" / ".env"
load_dotenv(env_path)

from utils.llm_first_detector import LLMFirstDetector
from utils.postgres_bible_database import PostgresBibleDatabase

def extract_verses_from_ground_truth(pdf_path: str) -> Set[str]:
    """Extract all verse references from Message_2 PDF ground truth"""
    verses = set()
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                # Look for verse patterns in the margin/left side
                lines = text.split('\n')
                for line in lines:
                    # Common patterns in Message output
                    patterns = [
                        r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?)',  # Book chapter:verse
                        r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:,\s*\d+(?:-\d+)?)*)',  # With lists
                        r'(vv?\.\s*\d+(?:-\d+)?)',  # v. or vv.
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, line)
                        for match in matches:
                            # Clean up the match
                            verse = match.strip()
                            if verse and len(verse) > 2:  # Filter out noise
                                verses.add(verse)
    
    return verses

def extract_verses_from_html(html_path: str) -> List[Dict]:
    """Extract verse references and their text from Message_2 HTML"""
    verses = []
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Extract verse references with their text
        # Look for patterns like: <span class="verse-ref">Rom. 5:18:</span>
        pattern = r'<span class="verse-ref">([^<]+)</span>\s*<span class="verse-text">([^<]+)</span>'
        matches = re.findall(pattern, content)
        
        for ref, text in matches:
            ref = ref.strip().rstrip(':')
            verses.append({
                'reference': ref,
                'text': text.strip()
            })
    
    return verses

def test_verse_detection(input_pdf: str):
    """Test our verse detection against ground truth"""
    
    print("=" * 70)
    print("COMPREHENSIVE TEST: W24ECT02en.pdf vs Message_2 Ground Truth")
    print("=" * 70)
    
    # 1. Extract ground truth verses from HTML (more reliable)
    html_path = "html_outlines/Message_2.html"
    if Path(html_path).exists():
        print("\n1. Extracting verses from Message_2.html ground truth...")
        expected_verses = extract_verses_from_html(html_path)
        print(f"   Found {len(expected_verses)} verses in ground truth")
        
        # Show sample
        if expected_verses:
            print("\n   Sample verses from ground truth:")
            for v in expected_verses[:5]:
                ref = v['reference']
                text_preview = v['text'][:50] + "..." if len(v['text']) > 50 else v['text']
                print(f"   - {ref}: {text_preview}")
    else:
        print(f"[WARNING] Ground truth HTML not found at {html_path}")
        expected_verses = []
    
    # 2. Extract ground truth from PDF as backup
    pdf_ground_truth = "output outlines/Message_2.pdf"
    if Path(pdf_ground_truth).exists():
        print("\n2. Extracting verses from Message_2.pdf for verification...")
        pdf_verses = extract_verses_from_ground_truth(pdf_ground_truth)
        print(f"   Found {len(pdf_verses)} verse references in PDF")
    else:
        pdf_verses = set()
    
    # 3. Test our detection
    print("\n3. Testing our verse detection on W24ECT02en.pdf...")
    
    # Read the input PDF
    with pdfplumber.open(input_pdf) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    # Detect verses using our LLM detector
    try:
        detector = LLMFirstDetector()
        detected_refs = detector.detect_verses(full_text)
        print(f"   LLM detected {len(detected_refs)} verse references")
        
        # Show sample detections
        if detected_refs:
            print("\n   Sample detections:")
            for ref in detected_refs[:5]:
                print(f"   - {ref.original_text} -> {ref.book} {ref.chapter}:{ref.start_verse}")
    except Exception as e:
        print(f"   [ERROR] LLM detection failed: {e}")
        detected_refs = []
    
    # 4. Compare detection with ground truth
    print("\n4. Comparison Analysis:")
    print("-" * 50)
    
    accuracy = 0  # Initialize accuracy
    
    # Use PDF verses if HTML is empty
    if not expected_verses and pdf_verses:
        print("   Using PDF verse references for comparison...")
        expected_set = {v.lower().replace(' ', '') for v in pdf_verses}
    elif expected_verses:
        expected_set = {v['reference'].lower().replace(' ', '') for v in expected_verses}
    else:
        expected_set = set()
    
    if expected_set and detected_refs:
        detected_set = {ref.original_text.lower().replace(' ', '') for ref in detected_refs}
        
        # Find matches and misses
        matched = expected_set & detected_set
        missed = expected_set - detected_set
        extra = detected_set - expected_set
        
        accuracy = len(matched) / len(expected_set) * 100 if expected_set else 0
        
        print(f"   Expected verses: {len(expected_set)}")
        print(f"   Detected verses: {len(detected_set)}")
        print(f"   Matched: {len(matched)}")
        print(f"   Missed: {len(missed)}")
        print(f"   Extra detections: {len(extra)}")
        print(f"   ACCURACY: {accuracy:.1f}%")
        
        if missed and len(missed) <= 20:
            print(f"\n   Missed verses (showing up to 20):")
            for m in list(missed)[:20]:
                # Find original reference
                for v in expected_verses:
                    if v['reference'].lower().replace(' ', '') == m:
                        print(f"   - {v['reference']}")
                        break
        elif missed:
            print(f"\n   Too many missed verses ({len(missed)}), showing first 10:")
            for m in list(missed)[:10]:
                for v in expected_verses:
                    if v['reference'].lower().replace(' ', '') == m:
                        print(f"   - {v['reference']}")
                        break
    else:
        print("   No comparison possible - no detected verses or ground truth")
    
    # 5. Test verse text population
    print("\n5. Testing Verse Text Population:")
    print("-" * 50)
    
    try:
        db = PostgresBibleDatabase()
        populated_count = 0
        sample_verses = []
        
        for ref in detected_refs[:10]:  # Test first 10
            verse_text = db.get_verse(ref.book, ref.chapter, ref.start_verse)
            if verse_text:
                populated_count += 1
                sample_verses.append({
                    'ref': f"{ref.book} {ref.chapter}:{ref.start_verse}",
                    'text': verse_text[:60] + "..." if len(verse_text) > 60 else verse_text
                })
        
        print(f"   Populated {populated_count}/10 sample verses with full text")
        
        if sample_verses:
            print("\n   Sample populated verses:")
            for sv in sample_verses[:3]:
                print(f"   - {sv['ref']}: {sv['text']}")
    except Exception as e:
        print(f"   [ERROR] Database test failed: {e}")
    
    # 6. Summary
    print("\n" + "=" * 70)
    if accuracy >= 95:
        print("[SUCCESS] Excellent detection accuracy!")
    elif accuracy >= 80:
        print("[GOOD] Good detection, but room for improvement")
    else:
        print("[NEEDS WORK] Detection needs significant improvement")
    
    print(f"Final Score: {accuracy:.1f}% verse detection accuracy")
    print("=" * 70)

if __name__ == "__main__":
    input_file = "original outlines/W24ECT02en.pdf"
    
    if not Path(input_file).exists():
        print(f"[ERROR] Input file not found: {input_file}")
        sys.exit(1)
    
    test_verse_detection(input_file)