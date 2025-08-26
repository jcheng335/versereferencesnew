#!/usr/bin/env python3
"""
Create comprehensive training data from 12 outline PDFs
Builds ML training dataset with all verse patterns
"""

import re
import json
import PyPDF2
import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using multiple methods"""
    text = ""
    
    # Try pdfplumber first (better for complex layouts)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        pass
    
    # Fallback to PyPDF2 if needed
    if not text:
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            pass
    
    return text

def extract_verses_comprehensive(text):
    """Extract all verse references using comprehensive patterns"""
    
    # Clean text
    text = text.replace('—', '-').replace('–', '-')
    
    # Comprehensive patterns based on MSG12VerseReferences analysis
    patterns = {
        'scripture_reading': r'Scripture Reading[:\s]+([^\n]+)',
        'parenthetical': r'\(([1-3]?\s*[A-Z][a-z]+\.?\s+\d+[:\d\-,;\s]*(?:[a-z])?)\)',
        'full_reference': r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+[a-z]?(?:[\-,]\d+[a-z]?)*)',
        'verse_list': r'([A-Z][a-z]+\.?\s+\d+:\d+(?:,\s*\d+[\-]\d+)?(?:,\s*\d+)*)',
        'standalone_single': r'\b(v\.\s*\d+[a-z]?)\b',
        'standalone_range': r'\b(vv\.\s*\d+[\-]\d+[a-z]?)\b',
        'chapter_only': r'(?:according to|in|from)\s+([A-Z][a-z]+\s+\d+)',
        'cf_reference': r'cf\.\s+([A-Z][a-z]+\.?\s+\d+[:\d\-,]*)',
        'see_reference': r'see\s+([A-Z][a-z]+\.?\s+\d+[:\d\-,]*)',
        'semicolon_list': r'([A-Z][a-z]+\.?\s+\d+:\d+[a-z]?(?:[;\s]+[A-Z][a-z]+\.?\s+\d+:\d+[a-z]?)+)',
        'verse_with_letter': r'([A-Z][a-z]+\.?\s+\d+:\d+[a-c])',
        'numbered_book': r'([1-3]\s+[A-Z][a-z]+\.?\s+\d+[:\d\-,]*)',
        'complex_range': r'([A-Z][a-z]+\.?\s+\d+:\d+\-\d+:\d+)',
        'dash_context': r'([A-Z][a-z]+)\s+(\d+)\s*[-—]\s*(?:vv?\.\s*)?(\d+(?:[-,]\d+)*)'
    }
    
    all_verses = []
    seen = set()
    
    # Extract verses with each pattern
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                verse = ' '.join(str(m) for m in match if m).strip()
            else:
                verse = str(match).strip()
            
            # Clean and normalize
            verse = re.sub(r'\s+', ' ', verse)
            verse = verse.strip()
            
            if verse and verse not in seen and len(verse) > 2:
                seen.add(verse)
                all_verses.append({
                    'reference': verse,
                    'pattern': pattern_name
                })
    
    return all_verses

def create_training_data():
    """Create comprehensive training dataset from all PDFs"""
    
    training_data = {
        'outlines': [],
        'verse_patterns': {},
        'statistics': {}
    }
    
    total_verses = 0
    pattern_counts = {}
    
    # Process each outline
    for i in range(1, 13):
        original_path = f"original outlines/W24ECT{i:02d}en.pdf"
        complete_path = f"output outlines/MSG{i}Complete.pdf"
        
        # Handle special cases
        if i == 9:
            original_path = "original outlines/W24ECT09en (1).pdf"
        elif i == 11:
            original_path = "original outlines/W24ECT11en (1).pdf"
        
        if not Path(original_path).exists():
            print(f"Warning: {original_path} not found")
            continue
        
        # Extract text from original
        original_text = extract_text_from_pdf(original_path)
        
        # Extract verses
        verses = extract_verses_comprehensive(original_text)
        
        # Create training sample
        sample = {
            'outline_id': f'W24ECT{i:02d}',
            'original_file': original_path,
            'complete_file': complete_path,
            'text_length': len(original_text),
            'verses': verses,
            'verse_count': len(verses),
            'unique_patterns': list(set(v['pattern'] for v in verses))
        }
        
        training_data['outlines'].append(sample)
        
        # Update statistics
        total_verses += len(verses)
        for verse in verses:
            pattern = verse['pattern']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        print(f"Outline {i}: {len(verses)} verses extracted")
        if verses:
            print(f"  Sample verses: {', '.join(v['reference'] for v in verses[:3])}")
    
    # Add statistics
    training_data['statistics'] = {
        'total_outlines': len(training_data['outlines']),
        'total_verses': total_verses,
        'average_verses_per_outline': total_verses / len(training_data['outlines']) if training_data['outlines'] else 0,
        'pattern_distribution': pattern_counts,
        'most_common_patterns': sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    }
    
    # Save training data
    with open('comprehensive_training_data.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2)
    
    print("\n" + "="*80)
    print("TRAINING DATA SUMMARY")
    print("="*80)
    print(f"Total outlines processed: {training_data['statistics']['total_outlines']}")
    print(f"Total verses extracted: {training_data['statistics']['total_verses']}")
    print(f"Average verses per outline: {training_data['statistics']['average_verses_per_outline']:.1f}")
    print(f"\nTop 5 pattern types:")
    for pattern, count in training_data['statistics']['most_common_patterns']:
        print(f"  {pattern}: {count} occurrences")
    
    return training_data

if __name__ == "__main__":
    training_data = create_training_data()