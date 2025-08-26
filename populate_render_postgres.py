#!/usr/bin/env python3
"""
Populate PostgreSQL on Render with Bible verses from SQLite
This script runs locally and populates the remote PostgreSQL database
"""

import sqlite3
import sys
from pathlib import Path

def generate_sql_script():
    """Generate SQL script from SQLite database"""
    
    print("Generating SQL script from SQLite database...")
    
    # Connect to SQLite
    sqlite_db = "bible-outline-enhanced-backend/bible_verses.db"
    if not Path(sqlite_db).exists():
        print(f"ERROR: SQLite database not found at {sqlite_db}")
        sys.exit(1)
    
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Output file
    output_file = "bible_data.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Drop and recreate tables
        f.write("-- Bible Database Migration Script\n")
        f.write("-- Generated from SQLite database\n\n")
        
        f.write("-- Drop existing tables\n")
        f.write("DROP TABLE IF EXISTS book_abbreviations CASCADE;\n")
        f.write("DROP TABLE IF EXISTS verses CASCADE;\n")
        f.write("DROP TABLE IF EXISTS books CASCADE;\n\n")
        
        # Create tables
        f.write("-- Create tables\n")
        f.write("""CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    abbreviation TEXT,
    testament TEXT,
    book_order INTEGER,
    total_chapters INTEGER
);\n\n""")
        
        f.write("""CREATE TABLE verses (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,
    chapter INTEGER,
    verse INTEGER,
    text TEXT,
    FOREIGN KEY (book_id) REFERENCES books (id)
);\n\n""")
        
        f.write("""CREATE TABLE book_abbreviations (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,
    abbreviation TEXT,
    FOREIGN KEY (book_id) REFERENCES books (id)
);\n\n""")
        
        # Create indexes
        f.write("-- Create indexes\n")
        f.write("CREATE INDEX idx_verses_book_chapter_verse ON verses(book_id, chapter, verse);\n")
        f.write("CREATE INDEX idx_books_name ON books(name);\n")
        f.write("CREATE INDEX idx_book_abbreviations_abbr ON book_abbreviations(abbreviation);\n\n")
        
        # Export books
        f.write("-- Insert books\n")
        sqlite_cursor.execute("SELECT id, name, abbreviation, testament, book_order, total_chapters FROM books")
        books = sqlite_cursor.fetchall()
        
        for book in books:
            id, name, abbr, testament, order, chapters = book
            # Escape single quotes
            if name:
                name = name.replace("'", "''")
            if abbr:
                abbr = abbr.replace("'", "''")
            if testament:
                testament = testament.replace("'", "''")
            
            f.write(f"INSERT INTO books (id, name, abbreviation, testament, book_order, total_chapters) VALUES ")
            f.write(f"({id}, '{name}', '{abbr}', '{testament}', {order}, {chapters});\n")
        
        print(f"Exported {len(books)} books")
        
        # Export verses in batches
        f.write("\n-- Insert verses\n")
        sqlite_cursor.execute("SELECT COUNT(*) FROM verses")
        total_verses = sqlite_cursor.fetchone()[0]
        
        batch_size = 100
        offset = 0
        verse_count = 0
        
        while offset < total_verses:
            sqlite_cursor.execute(f"SELECT id, book_id, chapter, verse, text FROM verses LIMIT {batch_size} OFFSET {offset}")
            verses_batch = sqlite_cursor.fetchall()
            
            for verse in verses_batch:
                id, book_id, chapter, verse_num, text = verse
                # Escape single quotes in text
                if text:
                    text = text.replace("'", "''")
                
                f.write(f"INSERT INTO verses (id, book_id, chapter, verse, text) VALUES ")
                f.write(f"({id}, {book_id}, {chapter}, {verse_num}, '{text}');\n")
                verse_count += 1
            
            offset += batch_size
            if offset % 1000 == 0:
                print(f"Exported {min(offset, total_verses)}/{total_verses} verses...")
        
        print(f"Exported {verse_count} verses")
        
        # Export book_abbreviations
        f.write("\n-- Insert book abbreviations\n")
        sqlite_cursor.execute("SELECT id, book_id, abbreviation FROM book_abbreviations")
        abbreviations = sqlite_cursor.fetchall()
        
        for abbr in abbreviations:
            id, book_id, abbreviation = abbr
            # Escape single quotes
            if abbreviation:
                abbreviation = abbreviation.replace("'", "''")
            
            f.write(f"INSERT INTO book_abbreviations (id, book_id, abbreviation) VALUES ")
            f.write(f"({id}, {book_id}, '{abbreviation}');\n")
        
        print(f"Exported {len(abbreviations)} abbreviations")
        
        # Test query
        f.write("\n-- Test query\n")
        f.write("SELECT v.text FROM verses v JOIN books b ON v.book_id = b.id WHERE b.name = 'Ephesians' AND v.chapter = 4 AND v.verse = 7;\n")
    
    sqlite_conn.close()
    
    print(f"\n✅ SQL script generated: {output_file}")
    print(f"   File size: {Path(output_file).stat().st_size / 1024 / 1024:.2f} MB")
    
    return output_file

def create_import_instructions():
    """Create instructions for importing into Render PostgreSQL"""
    
    instructions = """
INSTRUCTIONS TO IMPORT DATA INTO RENDER POSTGRESQL:

1. First, save the DATABASE_URL from Render:
   - Go to https://dashboard.render.com/d/dpg-d2lsvpn5r7bs73e32s40-a
   - Click on "Connect" button
   - Copy the "External Database URL"

2. Install PostgreSQL client tools locally if not already installed:
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Mac: brew install postgresql
   - Linux: sudo apt-get install postgresql-client

3. Import the data using psql:
   psql "YOUR_DATABASE_URL_HERE" < bible_data.sql

   OR if you have connection issues, use individual parameters:
   psql -h HOST -p PORT -U USER -d DATABASE < bible_data.sql

4. Verify the import:
   psql "YOUR_DATABASE_URL_HERE" -c "SELECT COUNT(*) FROM verses;"
   
   Should return: 31103

5. Test a sample verse:
   psql "YOUR_DATABASE_URL_HERE" -c "SELECT text FROM verses v JOIN books b ON v.book_id = b.id WHERE b.name = 'Ephesians' AND v.chapter = 4 AND v.verse = 7;"

ALTERNATIVE: Using Render's Web Shell:

1. Go to https://dashboard.render.com/d/dpg-d2lsvpn5r7bs73e32s40-a
2. Click "Connect" -> "psql Command Line"
3. Copy and paste sections of bible_data.sql into the terminal

Note: The SQL file is large (~17 MB), so the import may take a few minutes.
"""
    
    with open("IMPORT_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    print("\n📋 Import instructions saved to: IMPORT_INSTRUCTIONS.txt")

if __name__ == "__main__":
    print("=" * 60)
    print("Generate PostgreSQL Import Script from SQLite")
    print("=" * 60)
    
    # Generate SQL script
    sql_file = generate_sql_script()
    
    # Create import instructions
    create_import_instructions()
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Read IMPORT_INSTRUCTIONS.txt")
    print("2. Get your DATABASE_URL from Render")
    print("3. Run: psql 'YOUR_DATABASE_URL' < bible_data.sql")
    print("=" * 60)