#!/usr/bin/env python3
"""
Direct import to Render PostgreSQL
"""

import sqlite3
import os
import sys
import psycopg2
from psycopg2.extras import execute_batch

DATABASE_URL = "postgresql://bible_outline_user:kCMrTRNk1fwFltvgejVyT08aoINDLOCb@dpg-d2lsvpn5r7bs73e32s40-a.oregon-postgres.render.com/bible_outline_db"

def import_data():
    print("=" * 60)
    print("Importing Bible Database to Render PostgreSQL")
    print("=" * 60)
    
    # Connect to PostgreSQL
    print("\nConnecting to PostgreSQL on Render...")
    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cursor = pg_conn.cursor()
    print("[OK] Connected successfully!")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect("bible-outline-enhanced-backend/bible_verses.db")
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Drop existing tables
        print("\n1. Dropping existing tables...")
        pg_cursor.execute("DROP TABLE IF EXISTS book_abbreviations CASCADE")
        pg_cursor.execute("DROP TABLE IF EXISTS verses CASCADE")
        pg_cursor.execute("DROP TABLE IF EXISTS books CASCADE")
        print("   [OK] Tables dropped")
        
        # Create new tables
        print("\n2. Creating new tables...")
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
        print("   [OK] Tables created")
        
        # Create indexes
        print("\n3. Creating indexes...")
        pg_cursor.execute("CREATE INDEX idx_verses_book_chapter_verse ON verses(book_id, chapter, verse)")
        pg_cursor.execute("CREATE INDEX idx_books_name ON books(name)")
        pg_cursor.execute("CREATE INDEX idx_book_abbreviations_abbr ON book_abbreviations(abbreviation)")
        print("   [OK] Indexes created")
        
        # Import books
        print("\n4. Importing books...")
        sqlite_cursor.execute("SELECT id, name, abbreviation, testament, book_order, total_chapters FROM books")
        books = sqlite_cursor.fetchall()
        
        insert_query = "INSERT INTO books (id, name, abbreviation, testament, book_order, total_chapters) VALUES (%s, %s, %s, %s, %s, %s)"
        execute_batch(pg_cursor, insert_query, books, page_size=100)
        print(f"   [OK] Imported {len(books)} books")
        
        # Import verses in batches
        print("\n5. Importing verses (this will take a moment)...")
        sqlite_cursor.execute("SELECT id, book_id, chapter, verse, text FROM verses")
        
        batch_size = 500
        total_imported = 0
        
        while True:
            verses_batch = sqlite_cursor.fetchmany(batch_size)
            if not verses_batch:
                break
            
            insert_query = "INSERT INTO verses (id, book_id, chapter, verse, text) VALUES (%s, %s, %s, %s, %s)"
            execute_batch(pg_cursor, insert_query, verses_batch, page_size=100)
            
            total_imported += len(verses_batch)
            if total_imported % 5000 == 0:
                print(f"   ... {total_imported} verses imported")
        
        print(f"   [OK] Total verses imported: {total_imported}")
        
        # Import book_abbreviations
        print("\n6. Importing abbreviations...")
        sqlite_cursor.execute("SELECT id, book_id, abbreviation FROM book_abbreviations")
        abbreviations = sqlite_cursor.fetchall()
        
        insert_query = "INSERT INTO book_abbreviations (id, book_id, abbreviation) VALUES (%s, %s, %s)"
        execute_batch(pg_cursor, insert_query, abbreviations, page_size=100)
        print(f"   [OK] Imported {len(abbreviations)} abbreviations")
        
        # Commit changes
        pg_conn.commit()
        print("\n7. Committing changes...")
        print("   [OK] Changes committed")
        
        # Verify import
        print("\n8. Verifying import...")
        pg_cursor.execute("SELECT COUNT(*) FROM books")
        books_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM verses")
        verses_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM book_abbreviations")
        abbr_count = pg_cursor.fetchone()[0]
        
        print(f"   Books: {books_count} (expected: 66)")
        print(f"   Verses: {verses_count} (expected: 31103)")
        print(f"   Abbreviations: {abbr_count} (expected: 270)")
        
        # Test sample verses
        print("\n9. Testing sample verses...")
        test_verses = [
            ("Ephesians", 4, 7),
            ("Romans", 12, 3),
            ("John", 3, 16),
            ("Genesis", 1, 1),
            ("Revelation", 22, 21)
        ]
        
        for book, chapter, verse in test_verses:
            pg_cursor.execute("""
                SELECT v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE b.name = %s AND v.chapter = %s AND v.verse = %s
            """, (book, chapter, verse))
            result = pg_cursor.fetchone()
            if result:
                text = result[0][:60] + "..." if len(result[0]) > 60 else result[0]
                print(f"   {book} {chapter}:{verse} - {text}")
        
        print("\n" + "=" * 60)
        print("SUCCESS! PostgreSQL database fully populated!")
        print("=" * 60)
        print("\nYour PostgreSQL database now contains:")
        print(f"  • {books_count} books")
        print(f"  • {verses_count} verses with full Bible text")
        print(f"  • {abbr_count} book abbreviations")
        print("\nThe application will now use PostgreSQL for all verse lookups.")
        print("Make sure DATABASE_URL is set in your Render environment variables.")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        pg_conn.rollback()
        raise
    
    finally:
        pg_cursor.close()
        pg_conn.close()
        sqlite_cursor.close()
        sqlite_conn.close()

if __name__ == "__main__":
    import_data()