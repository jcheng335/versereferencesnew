"""
Build Bible database from Jubilee App HTML files
"""

import sqlite3
import os
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple

# Book mappings
BOOK_MAPPINGS = {
    'Gen': 'Gen', 'Exo': 'Exod', 'Lev': 'Lev', 'Num': 'Num', 'Deu': 'Deut',
    'Jos': 'Josh', 'Jdg': 'Judg', 'Rut': 'Ruth',
    '1Sa': '1Sam', '2Sa': '2Sam', '1Ki': '1Kings', '2Ki': '2Kings',
    '1Ch': '1Chr', '2Ch': '2Chr', 'Ezr': 'Ezra', 'Neh': 'Neh', 'Est': 'Esther',
    'Job': 'Job', 'Psa': 'Psa', 'Prv': 'Prov', 'Ecc': 'Eccl', 'SoS': 'Song',
    'Isa': 'Isa', 'Jer': 'Jer', 'Lam': 'Lam', 'Ezk': 'Ezek', 'Dan': 'Dan',
    'Hos': 'Hos', 'Joe': 'Joel', 'Amo': 'Amos', 'Oba': 'Obad', 'Jon': 'Jonah',
    'Mic': 'Mic', 'Nah': 'Nah', 'Hab': 'Hab', 'Zep': 'Zeph', 'Hag': 'Hag',
    'Zec': 'Zech', 'Mal': 'Mal',
    # New Testament
    'Mat': 'Matt', 'Mrk': 'Mark', 'Luk': 'Luke', 'Joh': 'John',
    'Act': 'Acts', 'Rom': 'Rom', '1Co': '1Cor', '2Co': '2Cor',
    'Gal': 'Gal', 'Eph': 'Eph', 'Phi': 'Phil', 'Col': 'Col',
    '1Th': '1Thess', '2Th': '2Thess', '1Ti': '1Tim', '2Ti': '2Tim',
    'Tit': 'Titus', 'Phm': 'Philem', 'Heb': 'Heb',
    'Jam': 'James', '1Pe': '1Pet', '2Pe': '2Pet',
    '1Jo': '1John', '2Jo': '2John', '3Jo': '3John', 'Jud': 'Jude',
    'Rev': 'Rev'
}

def parse_jubilee_html(html_path: str) -> List[Tuple[str, int, int, str]]:
    """Parse a Jubilee HTML file to extract verses"""
    verses = []
    
    # Get book name from filename
    filename = os.path.basename(html_path)
    book_code = filename.replace('.htm', '')
    
    # Skip note files and outline files
    if book_code.endswith('N') or book_code.endswith('O'):
        return []
    
    # Map to standard book name
    book_name = BOOK_MAPPINGS.get(book_code, book_code)
    
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all verse anchors and their text
        # Jubilee format: <a name="v1_1"></a> for chapter 1 verse 1
        current_chapter = 1
        current_verse = 1
        
        # Look for verse markers
        for element in soup.find_all(['a', 'span', 'div']):
            # Check for verse anchor
            if element.name == 'a' and element.get('name'):
                name = element.get('name')
                # Parse verse reference like v1_1 (chapter 1, verse 1)
                match = re.match(r'v(\d+)_(\d+)', name)
                if match:
                    current_chapter = int(match.group(1))
                    current_verse = int(match.group(2))
                    
                    # Get the verse text (usually follows the anchor)
                    verse_text = ""
                    next_sibling = element.next_sibling
                    while next_sibling:
                        if isinstance(next_sibling, str):
                            verse_text += next_sibling
                        elif hasattr(next_sibling, 'get_text'):
                            text = next_sibling.get_text()
                            # Stop at next verse marker
                            if re.match(r'^\d+\.?\s', text):
                                break
                            verse_text += text
                        
                        # Look for next verse or stop after reasonable amount
                        if len(verse_text) > 500:
                            break
                        
                        next_sibling = next_sibling.next_sibling if hasattr(next_sibling, 'next_sibling') else None
                    
                    # Clean up verse text
                    verse_text = verse_text.strip()
                    if verse_text:
                        verses.append((book_name, current_chapter, current_verse, verse_text))
        
        # Alternative parsing method if no anchors found
        if not verses:
            # Look for verse patterns in text
            text = soup.get_text()
            lines = text.split('\n')
            
            for line in lines:
                # Match patterns like "1:1 text" or "1. text"
                match = re.match(r'^(\d+):(\d+)\s+(.+)', line)
                if match:
                    chapter = int(match.group(1))
                    verse = int(match.group(2))
                    text = match.group(3).strip()
                    if text:
                        verses.append((book_name, chapter, verse, text))
    
    except Exception as e:
        print(f"Error parsing {html_path}: {e}")
    
    return verses

def build_database(jubilee_path: str, db_path: str):
    """Build SQLite database from Jubilee HTML files"""
    
    print("Building Bible database from Jubilee App...")
    
    # Create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bible_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse_number INTEGER NOT NULL,
            text TEXT NOT NULL,
            UNIQUE(book, chapter, verse_number)
        )
    ''')
    
    # Process each HTML file
    total_verses = 0
    books_processed = []
    
    for filename in sorted(os.listdir(jubilee_path)):
        if filename.endswith('.htm') and not (filename.endswith('N.htm') or filename.endswith('O.htm')):
            html_path = os.path.join(jubilee_path, filename)
            verses = parse_jubilee_html(html_path)
            
            if verses:
                book_name = verses[0][0]
                books_processed.append(book_name)
                
                for book, chapter, verse_num, text in verses:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO bible_verses (book, chapter, verse_number, text)
                            VALUES (?, ?, ?, ?)
                        ''', (book, chapter, verse_num, text))
                        total_verses += 1
                    except Exception as e:
                        print(f"Error inserting {book} {chapter}:{verse_num}: {e}")
                
                print(f"  Processed {book_name}: {len(verses)} verses")
    
    # Also create a verses table for compatibility
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            verse_text TEXT NOT NULL,
            UNIQUE(book, chapter, verse)
        )
    ''')
    
    # Copy data to verses table
    cursor.execute('''
        INSERT OR REPLACE INTO verses (book, chapter, verse, verse_text)
        SELECT book, chapter, verse_number, text FROM bible_verses
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"\nDatabase created successfully!")
    print(f"Total verses: {total_verses}")
    print(f"Books processed: {len(books_processed)}")
    print(f"Books: {', '.join(books_processed[:10])}...")
    
    return total_verses

def test_database(db_path: str):
    """Test the database with sample queries"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("TESTING DATABASE")
    print("=" * 60)
    
    # Test queries
    test_refs = [
        ('Rom', 5, 1),
        ('Luke', 7, 47),
        ('Eph', 4, 7),
        ('John', 3, 16)
    ]
    
    for book, chapter, verse in test_refs:
        cursor.execute('''
            SELECT text FROM bible_verses 
            WHERE book = ? AND chapter = ? AND verse_number = ?
        ''', (book, chapter, verse))
        result = cursor.fetchone()
        
        if result:
            text = result[0][:100] + "..." if len(result[0]) > 100 else result[0]
            print(f"\n{book} {chapter}:{verse}")
            print(f"  {text}")
        else:
            print(f"\n{book} {chapter}:{verse}: NOT FOUND")
    
    conn.close()

if __name__ == "__main__":
    jubilee_path = "Jubilee App"
    db_path = "bible_verses.db"
    
    if os.path.exists(jubilee_path):
        verses_count = build_database(jubilee_path, db_path)
        if verses_count > 0:
            test_database(db_path)
    else:
        print(f"Jubilee App folder not found at: {jubilee_path}")
        print("Please ensure the Jubilee App folder is in the current directory")