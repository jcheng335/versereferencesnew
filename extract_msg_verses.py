#!/usr/bin/env python3
"""
Extract all verse references from MSG complete files
Creates training dataset for 100% accurate detection
"""

import re
import json
import pdfplumber
from pathlib import Path
from typing import List, Dict, Set

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
        print(f"Error extracting from {pdf_path}: {e}")
    return text

def extract_verses_from_msg(text: str) -> List[str]:
    """
    Extract verse references from MSG complete files
    These files have verses in blue text in the left margin
    """
    verses = []
    
    # Clean text
    text = text.replace('—', '-').replace('–', '-')
    
    # Comprehensive patterns based on MSG format analysis
    patterns = [
        # Book chapter:verse (with or without period)
        r'\b([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)(?:[a-c])?(?:[-,](\d+)(?:[a-c])?)*',
        # Book chapter:verse-chapter:verse
        r'\b([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)-(\d+):(\d+)',
        # Just chapter:verse (when book is implied)
        r'\b(\d+):(\d+)(?:[a-c])?(?:[-,](\d+)(?:[a-c])?)*',
        # Standalone verses
        r'\bv(?:v)?\.?\s*(\d+)(?:[a-c])?(?:[-,](\d+)(?:[a-c])?)*',
    ]
    
    seen = set()
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            verse_ref = match.group(0).strip()
            # Clean up the reference
            verse_ref = re.sub(r'\s+', ' ', verse_ref)
            if verse_ref and verse_ref not in seen:
                verses.append(verse_ref)
                seen.add(verse_ref)
    
    return verses

def analyze_msg_files():
    """Analyze all MSG complete files to extract verse patterns"""
    
    training_data = {
        'outlines': [],
        'total_verses': 0,
        'unique_patterns': set(),
        'verse_mapping': {}
    }
    
    for i in range(1, 13):
        msg_file = f"output outlines/MSG{i}Complete.pdf"
        original_file = f"original outlines/W24ECT{i:02d}en.pdf"
        
        # Handle special naming
        if i == 9:
            original_file = "original outlines/W24ECT09en (1).pdf"
        elif i == 11:
            original_file = "original outlines/W24ECT11en (1).pdf"
        
        if not Path(msg_file).exists():
            print(f"Warning: {msg_file} not found")
            continue
        
        # Extract text from MSG complete file
        msg_text = extract_text_from_pdf(msg_file)
        
        # Extract verses
        verses = extract_verses_from_msg(msg_text)
        
        # Store outline data
        outline_data = {
            'outline_id': f'MSG{i}',
            'original_file': original_file,
            'msg_file': msg_file,
            'verses_found': verses,
            'verse_count': len(verses)
        }
        
        training_data['outlines'].append(outline_data)
        training_data['total_verses'] += len(verses)
        
        # Track unique patterns
        for verse in verses:
            # Identify pattern type
            if re.match(r'^[1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+', verse):
                training_data['unique_patterns'].add('book_chapter_verse')
            elif re.match(r'^\d+:\d+', verse):
                training_data['unique_patterns'].add('chapter_verse_only')
            elif re.match(r'^v\.?\s*\d+', verse):
                training_data['unique_patterns'].add('standalone_verse')
            elif re.match(r'^vv\.?\s*\d+', verse):
                training_data['unique_patterns'].add('verse_range')
        
        # Map verses to outline
        training_data['verse_mapping'][f'MSG{i}'] = verses
        
        print(f"MSG{i}: {len(verses)} verses extracted")
        if verses:
            print(f"  Samples: {', '.join(verses[:5])}")
    
    # Convert set to list for JSON serialization
    training_data['unique_patterns'] = list(training_data['unique_patterns'])
    
    # Save training data
    with open('msg_verse_training_data.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2)
    
    print("\n" + "="*80)
    print("MSG VERSE EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total outlines processed: {len(training_data['outlines'])}")
    print(f"Total verses extracted: {training_data['total_verses']}")
    print(f"Average verses per outline: {training_data['total_verses'] / len(training_data['outlines']):.1f}")
    print(f"Unique pattern types: {training_data['unique_patterns']}")
    
    return training_data

def create_perfect_patterns(training_data):
    """Create perfect regex patterns based on extracted verses"""
    
    patterns = {}
    
    for outline in training_data['outlines']:
        for verse in outline['verses_found']:
            # Analyze each verse to create pattern
            if re.match(r'^Eph\.?\s+\d+:\d+', verse):
                patterns['ephesians'] = patterns.get('ephesians', 0) + 1
            elif re.match(r'^1\s*Cor\.?\s+\d+:\d+', verse):
                patterns['first_corinthians'] = patterns.get('first_corinthians', 0) + 1
            elif re.match(r'^Rom\.?\s+\d+:\d+', verse):
                patterns['romans'] = patterns.get('romans', 0) + 1
            # Add more book-specific patterns
    
    print("\nMost common book references:")
    for book, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {book}: {count}")
    
    return patterns

if __name__ == "__main__":
    print("Extracting verses from MSG complete files...")
    training_data = analyze_msg_files()
    
    print("\nCreating perfect patterns...")
    patterns = create_perfect_patterns(training_data)
    
    print("\nTraining data saved to msg_verse_training_data.json")