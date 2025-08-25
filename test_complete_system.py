"""
Comprehensive test of the verse detection and population system
Tests with W24ECT12en.pdf and compares against MSG12VerseReferences.pdf expectations
"""

import sys
import os
import re
import json
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Add backend to path
sys.path.append('bible-outline-enhanced-backend/src')

# Load environment
load_dotenv()

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text() + "\n"
    doc.close()
    return text

def analyze_original_outline(pdf_path: str) -> Dict:
    """Analyze the original outline structure and identify all verses"""
    
    text = extract_pdf_text(pdf_path)
    
    # Parse outline structure
    lines = text.split('\n')
    outline_points = []
    verse_references = []
    
    current_main = None
    current_sub = None
    current_sub_sub = None
    scripture_reading = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Scripture Reading
        if line.startswith('Scripture Reading:'):
            scripture_reading = line.replace('Scripture Reading:', '').strip()
            verse_references.append({
                'reference': scripture_reading,
                'type': 'scripture_reading',
                'line': i,
                'context': None
            })
        
        # Main point (Roman numerals)
        match = re.match(r'^(I{1,3}|IV|V|VI|VII|VIII|IX|X)\.\s+(.+)', line)
        if match:
            current_main = match.group(1)
            text = match.group(2)
            outline_points.append({
                'level': 'main',
                'number': current_main,
                'text': text,
                'line': i
            })
            
            # Extract verses from the text
            verses = extract_verses_from_text(text, scripture_reading)
            verse_references.extend(verses)
        
        # Sub-point (Letters)
        match = re.match(r'^([A-Z])\.\s+(.+)', line)
        if match and current_main:
            current_sub = match.group(1)
            text = match.group(2)
            outline_points.append({
                'level': 'sub',
                'number': f"{current_main}.{current_sub}",
                'text': text,
                'line': i
            })
            
            verses = extract_verses_from_text(text, scripture_reading)
            verse_references.extend(verses)
        
        # Sub-sub-point (Numbers)
        match = re.match(r'^(\d+)\.\s+(.+)', line)
        if match and current_sub:
            current_sub_sub = match.group(1)
            text = match.group(2)
            outline_points.append({
                'level': 'sub_sub',
                'number': f"{current_main}.{current_sub}.{current_sub_sub}",
                'text': text,
                'line': i
            })
            
            verses = extract_verses_from_text(text, scripture_reading)
            verse_references.extend(verses)
        
        # Extract verses from any line
        if not any([line.startswith('Scripture Reading:'), 
                   re.match(r'^(I{1,3}|IV|V|VI)', line),
                   re.match(r'^[A-Z]\.\s', line),
                   re.match(r'^\d+\.\s', line)]):
            # This is continuation text
            verses = extract_verses_from_text(line, scripture_reading)
            verse_references.extend(verses)
    
    return {
        'outline_points': outline_points,
        'verse_references': verse_references,
        'scripture_reading': scripture_reading,
        'total_points': len(outline_points),
        'total_verses': len(verse_references)
    }

def extract_verses_from_text(text: str, context: str = None) -> List[Dict]:
    """Extract all verse references from a text line"""
    verses = []
    
    # Comprehensive patterns
    patterns = [
        # Book Chapter:Verse-Verse
        (r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)', 'full'),
        # Book Chapter:Verse; Book Chapter:Verse
        (r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?(?:\s*;\s*[123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?)+)', 'multi'),
        # Standalone verses
        (r'\b(vv?\.\s*\d+(?:-\d+)?(?:,\s*\d+)*)', 'standalone'),
    ]
    
    for pattern, pattern_type in patterns:
        for match in re.finditer(pattern, text):
            ref = match.group(1).strip()
            
            # If standalone and we have context, resolve it
            if pattern_type == 'standalone' and context:
                # Extract book and chapter from context
                context_match = re.match(r'([123]?\s*[A-Za-z]+\.?\s+\d+)', context)
                if context_match:
                    book_chapter = context_match.group(1)
                    verse_nums = ref.replace('vv.', '').replace('v.', '').strip()
                    ref = f"{book_chapter}:{verse_nums}"
            
            verses.append({
                'reference': ref,
                'type': pattern_type,
                'line': 0,  # Will be set by caller
                'context': context
            })
    
    return verses

def test_with_llm():
    """Test the LLM-based detection system"""
    from utils.llm_verse_detector import LLMVerseDetector
    
    print("=" * 80)
    print("TESTING LLM-BASED VERSE DETECTION")
    print("=" * 80)
    
    # Read W24ECT12en.pdf
    text = extract_pdf_text("W24ECT12en.pdf")
    
    # Initialize detector
    detector = LLMVerseDetector()
    
    # Process document
    result = detector.process_document(text)
    
    if result['success']:
        print(f"\n[SUCCESS] LLM Detection Results:")
        print(f"  Total verses found: {result['total_verses']}")
        print(f"  Verses with text: {result['verses_found']}")
        print(f"  Success rate: {result['success_rate']:.1f}%")
        
        # Show sample results
        print("\nSample outline points with verses:")
        for point in result['outline_points'][:5]:
            if point['verses']:
                print(f"\n{point['outline_number']}. {point['outline_text'][:60]}...")
                print(f"  Verses: {', '.join([v['reference'] for v in point['verses']])}")
    else:
        print(f"\n[FAILED] {result.get('error', 'Unknown error')}")
    
    return result

def test_hybrid_system():
    """Test the complete hybrid detection system"""
    from utils.enhanced_processor import EnhancedProcessor
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE HYBRID SYSTEM")
    print("=" * 80)
    
    processor = EnhancedProcessor()
    
    # Read PDF
    with open("W24ECT12en.pdf", 'rb') as f:
        pdf_content = f.read()
    
    # Process document
    result = processor.process_document(pdf_content, use_llm=True)
    
    print(f"\nHybrid System Results:")
    print(f"  References found: {result.get('references_found', 0)}")
    print(f"  Total verses: {result.get('total_verses', 0)}")
    print(f"  Average confidence: {result.get('average_confidence', 0):.2f}")
    
    # Check detected verses
    if 'all_references' in result:
        print(f"\nFirst 20 detected references:")
        for i, ref in enumerate(result['all_references'][:20], 1):
            print(f"  {i:2}. {ref['reference']} (confidence: {ref.get('confidence', 0):.2f})")
    
    return result

def compare_with_expected():
    """Compare detection results with expected verses from MSG12VerseReferences.pdf"""
    
    print("\n" + "=" * 80)
    print("COMPARISON WITH EXPECTED OUTPUT")
    print("=" * 80)
    
    # Expected verses based on manual count from MSG12VerseReferences.pdf
    expected_verses = [
        "Rom. 5:1-11", "Acts 10:43", "Rom. 3:24", "Rom. 3:26",
        "Isa. 61:10", "Luke 15:22", "Jer. 23:6", "Zech. 3:4",
        "Rom. 5:18", "Rom. 5:1-11", "Rom. 5:5", "Rom. 5:2",
        "Rom. 5:1", "Rom. 5:10", "Rom. 5:11", "John 14:6a",
        "Jude 20-21", "1 John 4:8", "1 John 4:16", "2 Tim. 1:6-7",
        "2 Tim. 4:22", "Luke 7:47-48", "Luke 7:50", "Rom. 3:17",
        "Rom. 8:6", "Rom. 5:3-4", "Rom. 5:11", "2 Cor. 12:7-9",
        "Rom. 8:28-29", "Phil. 2:19-22", "1 Thess. 2:4", "1 Pet. 1:7",
        "Mal. 3:3", "Rev. 3:18", "Rev. 1:20", "Rev. 21:18",
        "Rev. 21:23", "2 Pet. 1:4", "Matt. 24:45-51", "Rom. 5:4",
        "2 Cor. 4:17", "1 Pet. 5:10", "1 Thess. 2:12", "Col. 1:27",
        "Phil. 3:21", "Heb. 2:10-11", "2 Cor. 3:16-18", "2 Cor. 4:6b",
        "Rom. 5:10", "Rom. 12:5", "Rom. 16:1", "Rom. 16:4-5",
        "Rom. 16:16", "Rom. 16:20"
    ]
    
    # Analyze original outline
    original_analysis = analyze_original_outline("W24ECT12en.pdf")
    
    # Get detected verses
    detected_refs = [v['reference'] for v in original_analysis['verse_references']]
    
    # Compare
    found = []
    missing = []
    
    for expected in expected_verses:
        # Normalize reference
        normalized = expected.replace('.', '').strip()
        
        # Check if found
        found_match = False
        for detected in detected_refs:
            detected_norm = detected.replace('.', '').strip()
            if normalized in detected_norm or detected_norm in normalized:
                found_match = True
                break
        
        if found_match:
            found.append(expected)
        else:
            missing.append(expected)
    
    print(f"\nExpected verses: {len(expected_verses)}")
    print(f"Detected verses: {len(detected_refs)}")
    print(f"Found: {len(found)}/{len(expected_verses)} ({len(found)/len(expected_verses)*100:.1f}%)")
    
    if missing:
        print(f"\nMissing verses ({len(missing)}):")
        for verse in missing[:10]:
            print(f"  - {verse}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    
    return {
        'expected': expected_verses,
        'detected': detected_refs,
        'found': found,
        'missing': missing,
        'detection_rate': len(found) / len(expected_verses) * 100
    }

def main():
    """Run all tests"""
    
    print("COMPREHENSIVE VERSE DETECTION TEST")
    print("=" * 80)
    print("Testing with W24ECT12en.pdf")
    print("Expected output: MSG12VerseReferences.pdf format")
    print()
    
    # Test 1: Analyze original outline
    print("1. Analyzing original outline structure...")
    original = analyze_original_outline("W24ECT12en.pdf")
    print(f"   Found {original['total_points']} outline points")
    print(f"   Found {original['total_verses']} verse references")
    
    # Test 2: LLM detection
    print("\n2. Testing LLM detection...")
    try:
        llm_result = test_with_llm()
    except Exception as e:
        print(f"   LLM test failed: {e}")
        llm_result = None
    
    # Test 3: Hybrid system
    print("\n3. Testing hybrid system...")
    try:
        hybrid_result = test_hybrid_system()
    except Exception as e:
        print(f"   Hybrid test failed: {e}")
        hybrid_result = None
    
    # Test 4: Compare with expected
    print("\n4. Comparing with expected output...")
    comparison = compare_with_expected()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Original outline points: {original['total_points']}")
    print(f"Original verse references: {original['total_verses']}")
    if llm_result:
        print(f"LLM detection rate: {llm_result.get('success_rate', 0):.1f}%")
    if hybrid_result:
        print(f"Hybrid detection: {hybrid_result.get('references_found', 0)} references")
    print(f"Expected match rate: {comparison['detection_rate']:.1f}%")
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump({
            'original_analysis': {
                'points': original['total_points'],
                'verses': original['total_verses']
            },
            'llm_result': llm_result if llm_result else None,
            'hybrid_result': {
                'references': hybrid_result.get('references_found', 0),
                'confidence': hybrid_result.get('average_confidence', 0)
            } if hybrid_result else None,
            'comparison': {
                'expected': len(comparison['expected']),
                'found': len(comparison['found']),
                'missing': len(comparison['missing']),
                'rate': comparison['detection_rate']
            }
        }, f, indent=2)
    
    print("\n[Results saved to test_results.json]")

if __name__ == "__main__":
    main()