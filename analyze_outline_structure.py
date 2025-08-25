"""
Comprehensive analysis of outline structure and verse detection
Compares original W24ECT12en.pdf with MSG12VerseReferences.pdf
"""

import pdfplumber
import re
from typing import List, Dict, Tuple
import json

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def analyze_outline_structure(text: str) -> List[Dict]:
    """Analyze the outline structure - main points, sub-points, etc"""
    lines = text.split('\n')
    outline_points = []
    
    # Patterns for different outline levels
    patterns = {
        'scripture_reading': r'^Scripture Reading:\s*(.*)',
        'main_point': r'^([I]{1,3}|IV|V|VI|VII|VIII|IX|X)\.\s+(.*)',
        'sub_point': r'^\s*([A-Z])\.\s+(.*)',
        'sub_sub_point': r'^\s*(\d+)\.\s+(.*)',
        'sub_sub_sub_point': r'^\s*([a-z])\.\s+(.*)',
    }
    
    current_main = None
    current_sub = None
    current_sub_sub = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Check for Scripture Reading
        match = re.match(patterns['scripture_reading'], line_stripped)
        if match:
            outline_points.append({
                'level': 'scripture_reading',
                'number': 'SR',
                'text': match.group(1),
                'line_num': i
            })
            continue
        
        # Check for main point (I., II., etc.)
        match = re.match(patterns['main_point'], line_stripped)
        if match:
            current_main = match.group(1)
            current_sub = None
            current_sub_sub = None
            outline_points.append({
                'level': 'main',
                'number': current_main,
                'text': match.group(2),
                'line_num': i
            })
            continue
        
        # Check for sub-point (A., B., etc.)
        match = re.match(patterns['sub_point'], line_stripped)
        if match and current_main:
            current_sub = match.group(1)
            current_sub_sub = None
            outline_points.append({
                'level': 'sub',
                'number': f"{current_main}.{current_sub}",
                'text': match.group(2),
                'line_num': i
            })
            continue
        
        # Check for sub-sub-point (1., 2., etc.)
        match = re.match(patterns['sub_sub_point'], line_stripped)
        if match and current_sub:
            current_sub_sub = match.group(1)
            outline_points.append({
                'level': 'sub_sub',
                'number': f"{current_main}.{current_sub}.{current_sub_sub}",
                'text': match.group(2),
                'line_num': i
            })
            continue
        
        # Check for sub-sub-sub-point (a., b., etc.)
        match = re.match(patterns['sub_sub_sub_point'], line_stripped)
        if match and current_sub_sub:
            outline_points.append({
                'level': 'sub_sub_sub',
                'number': f"{current_main}.{current_sub}.{current_sub_sub}.{match.group(1)}",
                'text': match.group(2),
                'line_num': i
            })
    
    return outline_points

def extract_all_verse_references(text: str) -> List[str]:
    """Extract ALL verse references from text using comprehensive patterns"""
    
    verses = []
    seen = set()
    
    # Comprehensive patterns (order matters!)
    patterns = [
        # Scripture Reading pattern
        (r'Scripture Reading:\s*([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?(?:\s*;\s*[123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?)*)', 'scripture_reading'),
        
        # Multiple verses with semicolon
        (r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?(?:\s*;\s*[123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?)+)', 'multi_semicolon'),
        
        # Complex lists like Rom. 16:1, 4-5, 16, 20
        (r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:,\s*\d+(?:-\d+)?)*)', 'complex_list'),
        
        # Standard references
        (r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?[a-z]?)', 'standard'),
        
        # Chapter only references
        (r'according to ([123]?\s*[A-Za-z]+\.?\s+\d+)', 'chapter_only'),
        (r'in ([123]?\s*[A-Za-z]+\.?\s+\d+)(?=[,\s])', 'chapter_only'),
        
        # Standalone verse/verses with context
        (r'\b(vv?\.\s*\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)', 'standalone'),
    ]
    
    for pattern, pattern_type in patterns:
        for match in re.finditer(pattern, text):
            ref = match.group(1).strip()
            
            # Normalize the reference
            ref = re.sub(r'\s+', ' ', ref)
            
            # Check if we've seen this reference at this position
            position = match.start()
            ref_key = f"{ref}@{position}"
            
            if ref_key not in seen:
                seen.add(ref_key)
                verses.append(ref)
    
    return verses

def compare_outlines(original_path: str, expected_path: str):
    """Compare original outline with expected output"""
    
    print("=" * 80)
    print("COMPREHENSIVE OUTLINE ANALYSIS")
    print("=" * 80)
    
    # Extract text from both PDFs
    original_text = extract_pdf_text(original_path)
    expected_text = extract_pdf_text(expected_path)
    
    # Analyze outline structure
    print("\n1. ORIGINAL OUTLINE STRUCTURE (W24ECT12en.pdf):")
    print("-" * 40)
    original_points = analyze_outline_structure(original_text)
    for point in original_points[:10]:  # Show first 10 points
        indent = "  " * (0 if point['level'] == 'main' else 1 if point['level'] == 'sub' else 2)
        print(f"{indent}{point['number']}. {point['text'][:60]}...")
    print(f"... Total outline points: {len(original_points)}")
    
    # Extract verses from original
    print("\n2. VERSE REFERENCES IN ORIGINAL:")
    print("-" * 40)
    original_verses = extract_all_verse_references(original_text)
    print(f"Total references found: {len(original_verses)}")
    for i, verse in enumerate(original_verses[:20], 1):
        print(f"  {i:2}. {verse}")
    if len(original_verses) > 20:
        print(f"  ... and {len(original_verses) - 20} more")
    
    # Extract verses from expected output
    print("\n3. VERSE REFERENCES IN EXPECTED OUTPUT (MSG12VerseReferences.pdf):")
    print("-" * 40)
    expected_verses = extract_all_verse_references(expected_text)
    print(f"Total references found: {len(expected_verses)}")
    for i, verse in enumerate(expected_verses[:20], 1):
        print(f"  {i:2}. {verse}")
    if len(expected_verses) > 20:
        print(f"  ... and {len(expected_verses) - 20} more")
    
    # Find missing verses
    print("\n4. MISSING VERSES (in expected but not in original detection):")
    print("-" * 40)
    original_set = set(original_verses)
    expected_set = set(expected_verses)
    missing = expected_set - original_set
    
    if missing:
        for verse in sorted(missing):
            print(f"  - {verse}")
    else:
        print("  None - all verses detected!")
    
    # Analyze context-dependent verses
    print("\n5. CONTEXT-DEPENDENT VERSES:")
    print("-" * 40)
    
    # Find lines with standalone v./vv. references
    lines = original_text.split('\n')
    context_verses = []
    current_book_chapter = None
    
    for i, line in enumerate(lines):
        # Check for Scripture Reading or chapter references
        sr_match = re.search(r'Scripture Reading:\s*([123]?\s*[A-Za-z]+\.?\s+\d+)', line)
        if sr_match:
            current_book_chapter = sr_match.group(1)
        
        chapter_match = re.search(r'according to ([123]?\s*[A-Za-z]+\.?\s+\d+)', line)
        if chapter_match:
            current_book_chapter = chapter_match.group(1)
        
        # Find standalone verses
        standalone_matches = re.findall(r'\b(vv?\.\s*\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)', line)
        if standalone_matches and current_book_chapter:
            for match in standalone_matches:
                resolved = f"{current_book_chapter}:{match.replace('vv.', '').replace('v.', '').strip()}"
                context_verses.append({
                    'original': match,
                    'resolved': resolved,
                    'context': current_book_chapter,
                    'line': i + 1
                })
    
    for cv in context_verses[:10]:
        print(f"  Line {cv['line']}: '{cv['original']}' -> {cv['resolved']} (context: {cv['context']})")
    
    if len(context_verses) > 10:
        print(f"  ... and {len(context_verses) - 10} more")
    
    # Summary
    print("\n6. SUMMARY:")
    print("-" * 40)
    print(f"  Original outline points: {len(original_points)}")
    print(f"  Verses in original: {len(original_verses)}")
    print(f"  Verses in expected: {len(expected_verses)}")
    print(f"  Detection rate: {len(original_verses)}/{len(expected_verses)} = {len(original_verses)/len(expected_verses)*100:.1f}%")
    print(f"  Missing verses: {len(missing)}")
    print(f"  Context-dependent verses: {len(context_verses)}")
    
    return {
        'outline_points': original_points,
        'original_verses': original_verses,
        'expected_verses': expected_verses,
        'missing': list(missing),
        'context_verses': context_verses
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        original = sys.argv[1]
        expected = sys.argv[2] if len(sys.argv) > 2 else "MSG12VerseReferences.pdf"
    else:
        original = "W24ECT12en.pdf"
        expected = "MSG12VerseReferences.pdf"
    
    result = compare_outlines(original, expected)
    
    # Save analysis to JSON for further processing
    with open('outline_analysis.json', 'w') as f:
        json.dump({
            'outline_points': result['outline_points'],
            'missing': result['missing'],
            'context_verses': result['context_verses'],
            'stats': {
                'total_points': len(result['outline_points']),
                'total_original_verses': len(result['original_verses']),
                'total_expected_verses': len(result['expected_verses']),
                'detection_rate': len(result['original_verses'])/len(result['expected_verses'])*100
            }
        }, f, indent=2)
    
    print("\n[Analysis saved to outline_analysis.json]")