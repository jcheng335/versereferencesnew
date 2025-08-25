"""
Advanced PDF extraction using multiple methods
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict

def extract_text_pymupdf(pdf_path: str) -> str:
    """Extract text using PyMuPDF (more robust)"""
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text() + "\n"
    
    doc.close()
    return text

def extract_verses_from_text(text: str) -> List[str]:
    """Extract all Bible verse references from text"""
    
    verses = []
    
    # Comprehensive Bible book names
    books = [
        # Old Testament
        'Gen', 'Genesis', 'Exod', 'Exodus', 'Lev', 'Leviticus', 'Num', 'Numbers',
        'Deut', 'Deuteronomy', 'Josh', 'Joshua', 'Judg', 'Judges', 'Ruth',
        '1Sam', '1 Sam', '2Sam', '2 Sam', '1Kings', '1 Kings', '2Kings', '2 Kings',
        '1Chr', '1 Chr', '2Chr', '2 Chr', 'Ezra', 'Neh', 'Nehemiah', 'Esth', 'Esther',
        'Job', 'Psa', 'Psalm', 'Psalms', 'Prov', 'Proverbs', 'Eccl', 'Ecclesiastes',
        'Song', 'Isa', 'Isaiah', 'Jer', 'Jeremiah', 'Lam', 'Lamentations',
        'Ezek', 'Ezekiel', 'Dan', 'Daniel', 'Hos', 'Hosea', 'Joel', 'Amos', 'Obad', 'Obadiah',
        'Jonah', 'Mic', 'Micah', 'Nah', 'Nahum', 'Hab', 'Habakkuk', 'Zeph', 'Zephaniah',
        'Hag', 'Haggai', 'Zech', 'Zechariah', 'Mal', 'Malachi',
        # New Testament
        'Matt', 'Matthew', 'Mark', 'Luke', 'John',
        'Acts', 'Rom', 'Romans', '1Cor', '1 Cor', '2Cor', '2 Cor',
        'Gal', 'Galatians', 'Eph', 'Ephesians', 'Phil', 'Philippians',
        'Col', 'Colossians', '1Thes', '1 Thes', '1Thess', '1 Thess', 
        '2Thes', '2 Thes', '2Thess', '2 Thess',
        '1Tim', '1 Tim', '2Tim', '2 Tim', 'Titus', 'Philem', 'Philemon',
        'Heb', 'Hebrews', 'James', '1Pet', '1 Pet', '2Pet', '2 Pet',
        '1John', '1 John', '2John', '2 John', '3John', '3 John', 'Jude',
        'Rev', 'Revelation'
    ]
    
    # Create pattern for book names
    books_pattern = '|'.join(re.escape(book) for book in books)
    
    # Main pattern for Bible references
    verse_pattern = rf'({books_pattern})\.?\s+(\d+):(\d+(?:[-,]\d+)*[a-z]?)'
    
    for match in re.finditer(verse_pattern, text, re.IGNORECASE):
        book = match.group(1)
        chapter = match.group(2)
        verse_part = match.group(3)
        
        # Expand ranges and lists
        if '-' in verse_part:
            # Handle range
            parts = re.split(r'[-,]', verse_part)
            if len(parts) == 2 and parts[0].isdigit() and parts[1].rstrip('abcd').isdigit():
                start = int(parts[0])
                end = int(parts[1].rstrip('abcd'))
                for v in range(start, end + 1):
                    verses.append(f"{book} {chapter}:{v}")
            else:
                verses.append(f"{book} {chapter}:{verse_part}")
        elif ',' in verse_part:
            # Handle list
            parts = verse_part.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Sub-range in list
                    subparts = part.split('-')
                    if len(subparts) == 2 and subparts[0].isdigit() and subparts[1].rstrip('abcd').isdigit():
                        start = int(subparts[0])
                        end = int(subparts[1].rstrip('abcd'))
                        for v in range(start, end + 1):
                            verses.append(f"{book} {chapter}:{v}")
                    else:
                        verses.append(f"{book} {chapter}:{part}")
                else:
                    verses.append(f"{book} {chapter}:{part}")
        else:
            verses.append(f"{book} {chapter}:{verse_part}")
    
    # Also find standalone verse references (v. and vv.)
    standalone_pattern = r'\b(vv?\.\s*\d+(?:[-,]\d+)*)'
    
    # Find context from Scripture Reading
    scripture_reading_match = re.search(r'Scripture Reading:\s*([A-Za-z]+\.?\s+\d+)', text)
    if scripture_reading_match:
        context = scripture_reading_match.group(1).strip()
        book_chapter = context.replace('.', '')
        
        for match in re.finditer(standalone_pattern, text):
            verse_text = match.group(1)
            verse_nums = verse_text.replace('vv.', '').replace('v.', '').strip()
            
            if '-' in verse_nums:
                parts = verse_nums.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start = int(parts[0])
                    end = int(parts[1])
                    for v in range(start, end + 1):
                        verses.append(f"{book_chapter}:{v}")
            elif ',' in verse_nums:
                parts = verse_nums.split(',')
                for part in parts:
                    part = part.strip()
                    if part.isdigit():
                        verses.append(f"{book_chapter}:{part}")
            elif verse_nums.isdigit():
                verses.append(f"{book_chapter}:{verse_nums}")
    
    return verses

def analyze_pdf(pdf_path: str):
    """Analyze PDF and extract all verses"""
    
    print(f"Extracting text from: {pdf_path}")
    text = extract_text_pymupdf(pdf_path)
    
    # Show first 500 characters to verify extraction
    print("\nFirst 500 characters of extracted text:")
    print("-" * 40)
    print(text[:500])
    print("-" * 40)
    
    # Extract verses
    verses = extract_verses_from_text(text)
    
    print(f"\nTotal verse references found: {len(verses)}")
    
    # Show first 50 verses
    print("\nFirst 50 verses:")
    for i, verse in enumerate(verses[:50], 1):
        print(f"  {i:3}. {verse}")
    
    if len(verses) > 50:
        print(f"\n  ... and {len(verses) - 50} more verses")
    
    # Count unique verses
    unique_verses = list(dict.fromkeys(verses))
    print(f"\nTotal unique verses: {len(unique_verses)}")
    
    # Group by book
    books = {}
    for verse in unique_verses:
        book_match = re.match(r'([123]?\s*[A-Za-z]+)', verse)
        if book_match:
            book = book_match.group(1)
            if book not in books:
                books[book] = []
            books[book].append(verse)
    
    print("\nVerses by book:")
    for book in sorted(books.keys()):
        print(f"  {book}: {len(books[book])} verses")
    
    return verses

if __name__ == "__main__":
    import sys
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "MSG12VerseReferences.pdf"
    verses = analyze_pdf(pdf_path)