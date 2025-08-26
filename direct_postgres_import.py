#!/usr/bin/env python3
"""
Direct import to Render PostgreSQL using psycopg2
This requires the DATABASE_URL from Render
"""

import sqlite3
import os
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import execute_batch

def get_connection_params(database_url):
    """Parse DATABASE_URL into connection parameters"""
    result = urlparse(database_url)
    return {
        'database': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }

def import_data_to_postgres():
    """Import SQLite data to PostgreSQL"""
    
    # Get DATABASE_URL from environment or prompt
    database_url = input("Please enter your Render PostgreSQL DATABASE_URL: ").strip()
    
    if not database_url:
        print("ERROR: DATABASE_URL is required")
        print("\nTo get your DATABASE_URL:")
        print("1. Go to https://dashboard.render.com/d/dpg-d2lsvpn5r7bs73e32s40-a")
        print("2. Click 'Connect' button")
        print("3. Copy the 'External Database URL'")
        sys.exit(1)
    
    print("\nConnecting to PostgreSQL...")
    
    try:
        # Connect to PostgreSQL
        conn_params = get_connection_params(database_url)
        pg_conn = psycopg2.connect(**conn_params)
        pg_cursor = pg_conn.cursor()
        
        # Connect to SQLite
        sqlite_conn = sqlite3.connect("bible-outline-enhanced-backend/bible_verses.db")
        sqlite_cursor = sqlite_conn.cursor()
        
        print("Connected successfully!")
        
        # Drop existing tables
        print("\n1. Dropping existing tables...")
        pg_cursor.execute("DROP TABLE IF EXISTS book_abbreviations CASCADE")
        pg_cursor.execute("DROP TABLE IF EXISTS verses CASCADE")
        pg_cursor.execute("DROP TABLE IF EXISTS books CASCADE")
        
        # Create new tables
        print("2. Creating new tables...")
        
        pg_cursor.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                abbreviation TEXT,
                testament TEXT,
                book_order INTEGER,
                total_chapters INTEGER
            )
        """)
        
        pg_cursor.execute("""
            CREATE TABLE verses (
                id INTEGER PRIMARY KEY,
                book_id INTEGER,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        """)
        
        pg_cursor.execute("""
            CREATE TABLE book_abbreviations (
                id INTEGER PRIMARY KEY,
                book_id INTEGER,
                abbreviation TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        """)
        
        # Create indexes
        print("3. Creating indexes...")
        pg_cursor.execute("CREATE INDEX idx_verses_book_chapter_verse ON verses(book_id, chapter, verse)")
        pg_cursor.execute("CREATE INDEX idx_books_name ON books(name)")
        pg_cursor.execute("CREATE INDEX idx_book_abbreviations_abbr ON book_abbreviations(abbreviation)")
        
        # Import books
        print("4. Importing books...")
        sqlite_cursor.execute("SELECT id, name, abbreviation, testament, book_order, total_chapters FROM books")
        books = sqlite_cursor.fetchall()
        
        insert_query = "INSERT INTO books (id, name, abbreviation, testament, book_order, total_chapters) VALUES (%s, %s, %s, %s, %s, %s)"
        execute_batch(pg_cursor, insert_query, books)
        print(f"   Imported {len(books)} books")
        
        # Import verses in batches
        print("5. Importing verses (this will take a few minutes)...")
        
        # Get all verses
        sqlite_cursor.execute("SELECT id, book_id, chapter, verse, text FROM verses")
        
        batch_size = 500
        total_imported = 0
        
        while True:
            verses_batch = sqlite_cursor.fetchmany(batch_size)
            if not verses_batch:
                break
            
            insert_query = "INSERT INTO verses (id, book_id, chapter, verse, text) VALUES (%s, %s, %s, %s, %s)"
            execute_batch(pg_cursor, insert_query, verses_batch)
            
            total_imported += len(verses_batch)
            print(f"   Imported {total_imported} verses...")
        
        print(f"   Total verses imported: {total_imported}")
        
        # Import book_abbreviations
        print("6. Importing abbreviations...")
        sqlite_cursor.execute("SELECT id, book_id, abbreviation FROM book_abbreviations")
        abbreviations = sqlite_cursor.fetchall()
        
        insert_query = "INSERT INTO book_abbreviations (id, book_id, abbreviation) VALUES (%s, %s, %s)"
        execute_batch(pg_cursor, insert_query, abbreviations)
        print(f"   Imported {len(abbreviations)} abbreviations")
        
        # Commit changes
        pg_conn.commit()
        
        # Verify import
        print("\n7. Verifying import...")
        pg_cursor.execute("SELECT COUNT(*) FROM books")
        books_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM verses")
        verses_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM book_abbreviations")
        abbr_count = pg_cursor.fetchone()[0]
        
        print(f"   Books: {books_count} (expected: 66)")
        print(f"   Verses: {verses_count} (expected: 31103)")
        print(f"   Abbreviations: {abbr_count} (expected: 270)")
        
        # Test a sample verse
        print("\n8. Testing sample verse...")
        pg_cursor.execute("""
            SELECT v.text 
            FROM verses v 
            JOIN books b ON v.book_id = b.id 
            WHERE b.name = 'Ephesians' AND v.chapter = 4 AND v.verse = 7
        """)
        sample = pg_cursor.fetchone()
        if sample:
            print(f"   Ephesians 4:7: {sample[0][:80]}...")
        
        print("\n✅ Import completed successfully!")
        
        # Close connections
        pg_cursor.close()
        pg_conn.close()
        sqlite_cursor.close()
        sqlite_conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Bible Database Import")
    print("=" * 60)
    
    # Check for psycopg2
    try:
        import psycopg2
    except ImportError:
        print("\n❌ psycopg2 is not installed!")
        print("Please install it first:")
        print("   pip install psycopg2-binary")
        sys.exit(1)
    
    import_data_to_postgres()