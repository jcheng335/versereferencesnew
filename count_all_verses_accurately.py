"""
Accurately count ALL Bible verses in MSG12VerseReferences.pdf
Each individual verse reference counts as one (e.g., Eph. 4:7 is one, Eph. 4:8 is another)
"""

import pdfplumber
import re
from collections import OrderedDict

def extract_all_verses_from_pdf(pdf_path: str):
    """Extract all verse references from PDF"""
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    # All comprehensive patterns for Bible verse references
    verse_patterns = [
        # Book Chapter:Verse-Verse (range)
        r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:-\d+)?)',
        # Book Chapter:Verse, Verse (list)
        r'([123]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:,\s*\d+)*)',
        # Standalone verses (v. or vv.)
        r'\b(vv?\.\s*\d+(?:-\d+)?(?:,\s*\d+)*)',
    ]
    
    all_verses = []
    seen_positions = set()
    
    # First, find all book-based references
    book_pattern = re.compile(r'([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)')
    
    for match in book_pattern.finditer(text):
        book = match.group(1).strip()
        chapter = match.group(2)
        verse_part = match.group(3)
        
        # Normalize book name
        book = book.replace('.', '').strip()
        
        # Parse verse part
        if '-' in verse_part and ',' not in verse_part:
            # Simple range like 7-16
            parts = verse_part.split('-')
            start = int(parts[0])
            end = int(parts[1])
            for v in range(start, end + 1):
                ref = f"{book} {chapter}:{v}"
                all_verses.append(ref)
        elif ',' in verse_part:
            # List like 1,4-5,16,20
            parts = verse_part.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Sub-range
                    subparts = part.split('-')
                    start = int(subparts[0])
                    end = int(subparts[1])
                    for v in range(start, end + 1):
                        ref = f"{book} {chapter}:{v}"
                        all_verses.append(ref)
                else:
                    # Single verse
                    ref = f"{book} {chapter}:{part}"
                    all_verses.append(ref)
        else:
            # Single verse
            ref = f"{book} {chapter}:{verse_part}"
            all_verses.append(ref)
    
    # Find standalone v./vv. references and try to resolve them
    standalone_pattern = re.compile(r'\b(vv?\.\s*\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)')
    lines = text.split('\n')
    
    current_context = None
    for line in lines:
        # Check for Scripture Reading to set context
        sr_match = re.search(r'Scripture Reading:\s*([123]?\s*[A-Za-z]+\.?\s+\d+)', line)
        if sr_match:
            current_context = sr_match.group(1).replace('.', '').strip()
        
        # Check for "according to" pattern
        according_match = re.search(r'according to ([123]?\s*[A-Za-z]+\.?\s+\d+)', line)
        if according_match:
            current_context = according_match.group(1).replace('.', '').strip()
        
        # Find standalone verses
        for match in standalone_pattern.finditer(line):
            verse_text = match.group(1)
            # Clean up the verse text
            verse_text = verse_text.replace('vv.', '').replace('v.', '').strip()
            
            if current_context:
                # Parse the verse numbers
                if '-' in verse_text and ',' not in verse_text:
                    # Range
                    parts = verse_text.split('-')
                    start = int(parts[0])
                    end = int(parts[1])
                    for v in range(start, end + 1):
                        ref = f"{current_context}:{v}"
                        all_verses.append(ref)
                elif ',' in verse_text:
                    # List
                    parts = verse_text.split(',')
                    for part in parts:
                        part = part.strip()
                        if '-' in part:
                            subparts = part.split('-')
                            start = int(subparts[0])
                            end = int(subparts[1])
                            for v in range(start, end + 1):
                                ref = f"{current_context}:{v}"
                                all_verses.append(ref)
                        else:
                            ref = f"{current_context}:{part}"
                            all_verses.append(ref)
                else:
                    # Single verse
                    ref = f"{current_context}:{verse_text}"
                    all_verses.append(ref)
    
    return all_verses

def count_unique_verses(verses):
    """Count unique verse references"""
    unique = OrderedDict()
    for verse in verses:
        # Normalize the verse reference
        verse = re.sub(r'\s+', ' ', verse.strip())
        if verse not in unique:
            unique[verse] = 0
        unique[verse] += 1
    return unique

if __name__ == "__main__":
    import sys
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "MSG12VerseReferences.pdf"
    
    print(f"Analyzing: {pdf_path}")
    print("=" * 80)
    
    all_verses = extract_all_verses_from_pdf(pdf_path)
    
    print(f"Total individual verse references: {len(all_verses)}")
    print("\nSample of verses found:")
    for i, verse in enumerate(all_verses[:30], 1):
        print(f"  {i:3}. {verse}")
    
    if len(all_verses) > 30:
        print(f"  ... and {len(all_verses) - 30} more verses")
    
    # Count unique references
    unique_verses = count_unique_verses(all_verses)
    print(f"\nTotal unique verse references: {len(unique_verses)}")
    
    # Show verse frequency
    print("\nVerse frequency (showing verses that appear more than once):")
    for verse, count in unique_verses.items():
        if count > 1:
            print(f"  {verse}: appears {count} times")
    
    # Group by book
    books = {}
    for verse in unique_verses.keys():
        book_match = re.match(r'([123]?\s*[A-Za-z]+)', verse)
        if book_match:
            book = book_match.group(1)
            if book not in books:
                books[book] = 0
            books[book] += 1
    
    print("\nVerses by book:")
    for book, count in sorted(books.items()):
        print(f"  {book}: {count} verses")