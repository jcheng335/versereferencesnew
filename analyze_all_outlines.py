"""
Analyze all 12 original outlines and compare with the expected output
Extract patterns of verses that need to be detected and populated
"""

import fitz  # PyMuPDF
import re
import json
import os
from typing import List, Dict, Tuple, Set
from collections import defaultdict

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text() + "\n"
    doc.close()
    return text

def extract_all_verse_patterns(text: str) -> Dict[str, List[str]]:
    """Extract all verse references and categorize by pattern type"""
    
    patterns = defaultdict(list)
    
    # Track what we've already found to avoid duplicates
    found_positions = set()
    
    # Pattern categories with their regex
    pattern_types = [
        # Scripture Reading
        ('scripture_reading', r'Scripture Reading:\s*([^}\n]+)'),
        
        # Full book references with ranges/lists
        ('full_complex', r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\d+)+(?:[a-z])?)', 'e.g., Rom. 5:1-11, Rom. 16:1,4-5'),
        
        # Simple full references
        ('full_simple', r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+[a-z]?)', 'e.g., John 3:16, Rom. 5:1'),
        
        # Multiple references with semicolon
        ('multi_semicolon', r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\d+)?(?:\s*;\s*[123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\d+)?)+)', 'e.g., Isa. 61:10; Luke 15:22'),
        
        # Standalone verses with context
        ('standalone_range', r'\b(vv\.\s*\d+-\d+)', 'e.g., vv. 47-48'),
        ('standalone_single', r'\b(v\.\s*\d+[a-z]?)', 'e.g., v. 5, v. 10a'),
        ('standalone_list', r'\b(vv?\.\s*\d+(?:,\s*\d+)+)', 'e.g., vv. 1, 10-11'),
        
        # Chapter only references
        ('chapter_only', r'according to ([123]?\s*[A-Za-z]+\.?\s+\d+)(?![:])', 'e.g., according to Luke 7'),
        
        # Parenthetical references
        ('parenthetical', r'\(([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\d+)?)\)', 'e.g., (Acts 10:43)'),
        
        # Dash-separated references
        ('dash_separated', r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+)—([123]?\s*[A-Za-z]+\.?\s+\d+:\d+)', 'e.g., Matt. 24:45—51'),
        
        # Cross-references with cf.
        ('cross_reference', r'cf\.\s*([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\d+)?)', 'e.g., cf. Rom. 8:28'),
        
        # See also references
        ('see_also', r'see\s+also\s+([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\d+)?)', 'e.g., see also Eph. 4:16'),
    ]
    
    # Process each pattern type
    for pattern_name, pattern_regex, *description in pattern_types:
        for match in re.finditer(pattern_regex, text, re.IGNORECASE):
            # Check if we've already captured this text at this position
            pos_key = (match.start(), match.end())
            if pos_key not in found_positions:
                found_positions.add(pos_key)
                ref = match.group(1).strip()
                patterns[pattern_name].append(ref)
    
    return dict(patterns)

def analyze_outline_structure(text: str) -> List[Dict]:
    """Analyze the hierarchical structure of the outline"""
    
    lines = text.split('\n')
    structure = []
    
    current_main = None
    current_sub = None
    current_sub_sub = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Main points (Roman numerals)
        main_match = re.match(r'^(I{1,3}|IV|V|VI|VII|VIII|IX|X)\.\s+(.+)', line)
        if main_match:
            current_main = main_match.group(1)
            current_sub = None
            current_sub_sub = None
            
            structure.append({
                'type': 'main',
                'number': current_main,
                'text': main_match.group(2),
                'line': i + 1,
                'verses': extract_all_verse_patterns(main_match.group(2))
            })
            continue
        
        # Sub-points (Capital letters)
        sub_match = re.match(r'^([A-Z])\.\s+(.+)', line)
        if sub_match and current_main:
            current_sub = sub_match.group(1)
            current_sub_sub = None
            
            structure.append({
                'type': 'sub',
                'number': f"{current_main}.{current_sub}",
                'text': sub_match.group(2),
                'line': i + 1,
                'verses': extract_all_verse_patterns(sub_match.group(2))
            })
            continue
        
        # Sub-sub-points (Numbers)
        sub_sub_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if sub_sub_match and current_sub:
            current_sub_sub = sub_sub_match.group(1)
            
            structure.append({
                'type': 'sub_sub',
                'number': f"{current_main}.{current_sub}.{current_sub_sub}",
                'text': sub_sub_match.group(2),
                'line': i + 1,
                'verses': extract_all_verse_patterns(sub_sub_match.group(2))
            })
            continue
        
        # Sub-sub-sub-points (Lowercase letters)
        sub_sub_sub_match = re.match(r'^([a-z])\.\s+(.+)', line)
        if sub_sub_sub_match and current_sub_sub:
            structure.append({
                'type': 'sub_sub_sub',
                'number': f"{current_main}.{current_sub}.{current_sub_sub}.{sub_sub_sub_match.group(1)}",
                'text': sub_sub_sub_match.group(2),
                'line': i + 1,
                'verses': extract_all_verse_patterns(sub_sub_sub_match.group(2))
            })
    
    return structure

def compare_outlines(original_path: str, complete_path: str, outline_num: int) -> Dict:
    """Compare an original outline with its corresponding complete version"""
    
    # Extract text from both files
    original_text = extract_pdf_text(original_path)
    complete_text = extract_pdf_text(complete_path)
    
    # Split complete text by message (assuming each starts with "Message")
    messages = re.split(r'Message\s+(?:One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve)', complete_text)
    
    if outline_num <= len(messages):
        complete_message = messages[outline_num] if outline_num > 0 else complete_text
    else:
        complete_message = complete_text
    
    # Extract patterns from both
    original_patterns = extract_all_verse_patterns(original_text)
    complete_patterns = extract_all_verse_patterns(complete_message)
    
    # Analyze structure
    original_structure = analyze_outline_structure(original_text)
    
    # Count verses
    original_count = sum(len(verses) for verses in original_patterns.values())
    complete_count = sum(len(verses) for verses in complete_patterns.values())
    
    # Find missing patterns
    missing_verses = []
    for pattern_type, verses in complete_patterns.items():
        original_verses = set(original_patterns.get(pattern_type, []))
        for verse in verses:
            if verse not in original_verses:
                # Check if it's in any other pattern type in original
                found = False
                for other_type, other_verses in original_patterns.items():
                    if verse in other_verses:
                        found = True
                        break
                if not found:
                    missing_verses.append({'verse': verse, 'type': pattern_type})
    
    return {
        'original_path': original_path,
        'outline_number': outline_num,
        'original_patterns': original_patterns,
        'complete_patterns': complete_patterns,
        'original_structure': original_structure,
        'original_verse_count': original_count,
        'complete_verse_count': complete_count,
        'missing_verses': missing_verses,
        'detection_rate': (original_count / complete_count * 100) if complete_count > 0 else 0
    }

def analyze_all_outlines():
    """Analyze all 12 original outlines"""
    
    results = []
    pattern_statistics = defaultdict(int)
    all_missing_verses = []
    
    # Process each outline
    for i in range(1, 13):
        outline_num = str(i).zfill(2)
        original_path = f"original outlines/W24ECT{outline_num}en.pdf"
        
        # Handle naming variations
        if not os.path.exists(original_path):
            # Try with parentheses
            original_path = f"original outlines/W24ECT{outline_num}en (1).pdf"
        
        if os.path.exists(original_path):
            print(f"Analyzing outline {i}: {original_path}")
            result = compare_outlines(original_path, "2024-12-WT-Outlines-with-Verses-E.pdf", i)
            results.append(result)
            
            # Collect statistics
            for pattern_type, verses in result['original_patterns'].items():
                pattern_statistics[pattern_type] += len(verses)
            
            all_missing_verses.extend(result['missing_verses'])
            
            print(f"  Original verses: {result['original_verse_count']}")
            print(f"  Complete verses: {result['complete_verse_count']}")
            print(f"  Detection rate: {result['detection_rate']:.1f}%")
            print(f"  Missing verses: {len(result['missing_verses'])}")
        else:
            print(f"Warning: Could not find {original_path}")
    
    # Analyze missing verse patterns
    missing_patterns = defaultdict(list)
    for missing in all_missing_verses:
        missing_patterns[missing['type']].append(missing['verse'])
    
    # Summary
    total_original = sum(r['original_verse_count'] for r in results)
    total_complete = sum(r['complete_verse_count'] for r in results)
    avg_detection = sum(r['detection_rate'] for r in results) / len(results) if results else 0
    
    print("\n" + "=" * 80)
    print("OVERALL ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Outlines analyzed: {len(results)}")
    print(f"Total original verses detected: {total_original}")
    print(f"Total complete verses expected: {total_complete}")
    print(f"Overall detection rate: {(total_original/total_complete*100) if total_complete > 0 else 0:.1f}%")
    print(f"Average detection rate: {avg_detection:.1f}%")
    
    print("\nVerse Pattern Statistics:")
    for pattern_type, count in sorted(pattern_statistics.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern_type}: {count} verses")
    
    print("\nMost Common Missing Pattern Types:")
    for pattern_type, verses in sorted(missing_patterns.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"  {pattern_type}: {len(verses)} missing verses")
        print(f"    Examples: {', '.join(verses[:3])}")
    
    # Save detailed results
    save_results = {
        'summary': {
            'outlines_analyzed': len(results),
            'total_original_verses': total_original,
            'total_complete_verses': total_complete,
            'overall_detection_rate': (total_original/total_complete*100) if total_complete > 0 else 0,
            'average_detection_rate': avg_detection
        },
        'pattern_statistics': dict(pattern_statistics),
        'missing_patterns': {k: v[:10] for k, v in missing_patterns.items()},  # Save first 10 examples
        'detailed_results': [
            {
                'outline': r['outline_number'],
                'original_verses': r['original_verse_count'],
                'complete_verses': r['complete_verse_count'],
                'detection_rate': r['detection_rate'],
                'missing_count': len(r['missing_verses'])
            }
            for r in results
        ]
    }
    
    with open('outline_analysis_results.json', 'w') as f:
        json.dump(save_results, f, indent=2)
    
    print("\n[Detailed results saved to outline_analysis_results.json]")
    
    return results

if __name__ == "__main__":
    print("COMPREHENSIVE OUTLINE ANALYSIS")
    print("Analyzing all 12 original outlines against complete versions")
    print("=" * 80)
    
    results = analyze_all_outlines()