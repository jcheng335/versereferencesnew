#!/usr/bin/env python3
"""
Comprehensive Bible Verse Format Extractor
Analyzes all 12 PDF files in original outlines directory to extract every possible verse reference format
"""

import pdfplumber
import re
import os
import json
from collections import defaultdict, Counter

class VerseFormatExtractor:
    def __init__(self):
        # Comprehensive Bible book patterns
        self.books_pattern = r'''(?:
            # Full book names
            Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|
            Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|
            Ecclesiastes|Song of Songs|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|
            Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|
            Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|
            Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|
            Philemon|Hebrews|James|Peter|Jude|Revelation|
            
            # Common abbreviations
            Gen|Exod?|Lev|Num|Deut?|Josh|Judg|Ruth|Sam|Kgs?|Chr|Ezra|Neh|Esth?|
            Job|Psa?|Prov|Eccl?|Song|Isa|Jer|Lam|Ezek?|Dan|Hos|Joel|Amos|Obad?|
            Jon|Mic|Nah|Hab|Zeph?|Hag|Zech?|Mal|Matt?|Mk|Mark|Luke?|Jn|John|
            Acts?|Rom|Cor|Gal|Eph|Phil|Col|Thess?|Tim|Tit|Phlm|Heb|Jas|Pet|Jude|Rev|
            
            # Numbered books
            [123]\s*(?:Samuel|Sam|Kings?|Kgs?|Chronicles|Chr|Corinthians|Cor|
            Thessalonians|Thess?|Timothy|Tim|Peter|Pet|John|Jn)|
            
            # Additional common forms
            First|Second|Third|1st|2nd|3rd
        )'''
        
        # Comprehensive verse patterns - extract ANY text that could be a verse reference
        self.verse_patterns = [
            # Pattern 1: Full references with book names
            r'(?:' + self.books_pattern + r')\.?\s+\d+(?::\d+(?:[abc])?(?:-\d+[abc]?)?(?:,\s*\d+(?::\d+)?(?:[abc])?(?:-\d+[abc]?)?)*)?(?:;\s*(?:' + self.books_pattern + r')\.?\s+\d+(?::\d+(?:[abc])?(?:-\d+[abc]?)?(?:,\s*\d+(?::\d+)?(?:[abc])?(?:-\d+[abc]?)?)*)?)*',
            
            # Pattern 2: Scripture Reading format
            r'Scripture\s+Reading:?\s*[^\n]+',
            
            # Pattern 3: Parenthetical references
            r'\([^)]*(?:' + self.books_pattern + r')[^)]*\d+[^)]*\)',
            
            # Pattern 4: Standalone verse references  
            r'(?:vv?\.|verses?|vs\.)\s*\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*',
            
            # Pattern 5: Chapter only
            r'(?:' + self.books_pattern + r')\.?\s+\d+(?:\s*$|\s*[^\d:])',
            
            # Pattern 6: Simple format like "5:1-11"
            r'\d+:\d+(?:[abc])?(?:-\d+[abc]?)?(?:,\s*\d+(?::\d+[abc]?)?(?:-\d+[abc]?)?)*',
            
            # Pattern 7: cf. references
            r'cf\.\s*[^\n]+?(?:\d+:\d+|\d+\s*$)',
            
            # Pattern 8: Written out numbers
            r'(?:First|Second|Third|1st|2nd|3rd)\s+(?:' + self.books_pattern + r')[^\n]*',
            
            # Pattern 9: Complex lists with semicolons
            r'(?:' + self.books_pattern + r')\.?\s+\d+:\d+[^;]*(?:;\s*(?:' + self.books_pattern + r')\.?\s+\d+:\d+[^;]*)*',
            
            # Pattern 10: Catch remaining numeric references
            r'\b\d{1,3}:\d{1,3}(?:[abc])?(?:-\d{1,3}[abc]?)?(?:,\s*\d{1,3}(?::\d{1,3}[abc]?)?(?:-\d{1,3}[abc]?)?)*\b',
        ]
        
    def extract_from_pdf(self, pdf_path):
        """Extract text from PDF and find all potential verse references"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                return self.find_all_verse_formats(full_text)
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return []
    
    def find_all_verse_formats(self, text):
        """Find all potential verse reference formats in text"""
        found_formats = []
        
        # Clean text first
        text = text.replace('—', '-').replace("'", "'").replace('"', '"').replace('"', '"')
        
        # Apply each pattern
        for i, pattern in enumerate(self.verse_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE | re.VERBOSE | re.MULTILINE)
            for match in matches:
                found_text = match.group().strip()
                if found_text and len(found_text) > 1:  # Filter out very short matches
                    found_formats.append({
                        'pattern_id': i + 1,
                        'text': found_text,
                        'context': self.get_context(text, match.start(), match.end())
                    })
        
        # Also look for any text that contains numbers and common verse indicators
        additional_patterns = [
            r'[^\n]*\b(?:v\.|vs\.|verse|chapter|chap\.)[^\n]*\d+[^\n]*',
            r'[^\n]*\d+:\d+[^\n]*',
            r'[^\n]*(?:according to|as in|see)[^\n]*[A-Z][a-z]+\s+\d+[^\n]*'
        ]
        
        for pattern in additional_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                found_text = match.group().strip()
                if found_text and len(found_text) > 5:
                    found_formats.append({
                        'pattern_id': 'additional',
                        'text': found_text,
                        'context': self.get_context(text, match.start(), match.end())
                    })
        
        return found_formats
    
    def get_context(self, text, start, end, context_len=50):
        """Get surrounding context for a match"""
        context_start = max(0, start - context_len)
        context_end = min(len(text), end + context_len)
        before = text[context_start:start]
        after = text[end:context_end]
        return {
            'before': before.replace('\n', ' ').strip(),
            'after': after.replace('\n', ' ').strip()
        }

def main():
    """Main function to analyze all PDFs"""
    extractor = VerseFormatExtractor()
    
    # Directory containing the PDFs
    pdf_dir = r"C:\Users\jchen\versereferencesnew\original outlines"
    
    if not os.path.exists(pdf_dir):
        print(f"Directory not found: {pdf_dir}")
        return
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    pdf_files.sort()
    
    print(f"Found {len(pdf_files)} PDF files to analyze")
    print("=" * 60)
    
    all_formats = []
    format_counter = Counter()
    pdf_results = {}
    
    # Process each PDF
    for pdf_file in pdf_files:
        print(f"\nAnalyzing: {pdf_file}")
        pdf_path = os.path.join(pdf_dir, pdf_file)
        
        formats_found = extractor.extract_from_pdf(pdf_path)
        pdf_results[pdf_file] = formats_found
        
        print(f"  Found {len(formats_found)} potential verse references")
        
        # Count unique format types
        unique_texts = set()
        for fmt in formats_found:
            normalized_text = fmt['text'].lower().strip()
            unique_texts.add(normalized_text)
            format_counter[normalized_text] += 1
        
        print(f"  Unique formats: {len(unique_texts)}")
        
        # Show first few examples
        if formats_found:
            print("  Examples:")
            for fmt in formats_found[:5]:
                print(f"    [{fmt['pattern_id']}] {fmt['text']}")
        
        all_formats.extend(formats_found)
    
    print("\n" + "=" * 60)
    print(f"TOTAL ANALYSIS COMPLETE")
    print(f"Total potential verse references found: {len(all_formats)}")
    print(f"Unique format variations: {len(format_counter)}")
    
    # Get most common formats
    print(f"\nMOST COMMON FORMATS:")
    for text, count in format_counter.most_common(30):
        print(f"  [{count:2d}x] {text}")
    
    # Group by pattern type
    print(f"\nFORMATS BY PATTERN TYPE:")
    pattern_groups = defaultdict(list)
    for fmt in all_formats:
        pattern_groups[fmt['pattern_id']].append(fmt['text'])
    
    for pattern_id, texts in pattern_groups.items():
        unique_texts = list(set(texts))
        print(f"  Pattern {pattern_id}: {len(unique_texts)} unique formats")
        for text in unique_texts[:10]:  # Show first 10
            print(f"    - {text}")
        if len(unique_texts) > 10:
            print(f"    ... and {len(unique_texts) - 10} more")
    
    # Save detailed results
    output_file = "comprehensive_verse_formats.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_references': len(all_formats),
                'unique_formats': len(format_counter),
                'pdfs_analyzed': len(pdf_files),
                'most_common': dict(format_counter.most_common(50))
            },
            'by_pdf': pdf_results,
            'all_formats': all_formats,
            'pattern_analysis': dict(pattern_groups)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Extract unique format examples for manual review
    unique_examples = []
    seen_normalized = set()
    
    for fmt in all_formats:
        normalized = re.sub(r'\s+', ' ', fmt['text'].lower().strip())
        if normalized not in seen_normalized and len(normalized) > 2:
            seen_normalized.add(normalized)
            unique_examples.append(fmt['text'])
    
    print(f"\nUNIQUE FORMAT EXAMPLES ({len(unique_examples)} total):")
    for i, example in enumerate(sorted(unique_examples)[:100], 1):  # Show first 100
        print(f"{i:3d}. {example}")
    
    if len(unique_examples) > 100:
        print(f"... and {len(unique_examples) - 100} more unique formats")
    
    # Save just the unique examples for easy reference
    with open("unique_verse_formats.txt", 'w', encoding='utf-8') as f:
        f.write("UNIQUE BIBLE VERSE REFERENCE FORMATS\n")
        f.write("=" * 50 + "\n\n")
        for i, example in enumerate(sorted(unique_examples), 1):
            f.write(f"{i:3d}. {example}\n")
    
    print(f"\nUnique formats list saved to: unique_verse_formats.txt")

if __name__ == "__main__":
    main()