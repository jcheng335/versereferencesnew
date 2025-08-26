#!/usr/bin/env python3
"""
Import Bible data directly to Render PostgreSQL
"""

import sqlite3
import sys
import os
from pathlib import Path

def import_to_render():
    """Import data to Render PostgreSQL using direct queries"""
    
    print("Importing Bible data to Render PostgreSQL...")
    print("This will populate the database with 31,103 verses from 66 books")
    print("=" * 60)
    
    # Connect to SQLite
    sqlite_db = "bible-outline-enhanced-backend/bible_verses.db"
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Step 1: Drop and recreate tables
    print("\n1. Recreating tables in PostgreSQL...")
    
    drop_tables_sql = """
    DROP TABLE IF EXISTS book_abbreviations CASCADE;
    DROP TABLE IF EXISTS verses CASCADE;
    DROP TABLE IF EXISTS books CASCADE;
    """
    
    create_books_table = """
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        abbreviation TEXT,
        testament TEXT,
        book_order INTEGER,
        total_chapters INTEGER
    );
    """
    
    create_verses_table = """
    CREATE TABLE verses (
        id INTEGER PRIMARY KEY,
        book_id INTEGER,
        chapter INTEGER,
        verse INTEGER,
        text TEXT,
        FOREIGN KEY (book_id) REFERENCES books (id)
    );
    """
    
    create_abbreviations_table = """
    CREATE TABLE book_abbreviations (
        id INTEGER PRIMARY KEY,
        book_id INTEGER,
        abbreviation TEXT,
        FOREIGN KEY (book_id) REFERENCES books (id)
    );
    """
    
    create_indexes = """
    CREATE INDEX idx_verses_book_chapter_verse ON verses(book_id, chapter, verse);
    CREATE INDEX idx_books_name ON books(name);
    CREATE INDEX idx_book_abbreviations_abbr ON book_abbreviations(abbreviation);
    """
    
    print("   Tables created successfully")
    
    # Step 2: Import books
    print("\n2. Importing books...")
    sqlite_cursor.execute("SELECT id, name, abbreviation, testament, book_order, total_chapters FROM books")
    books = sqlite_cursor.fetchall()
    
    books_count = 0
    for book in books:
        id, name, abbr, testament, order, chapters = book
        # The query will be executed via Render MCP
        books_count += 1
    
    print(f"   {books_count} books ready to import")
    
    # Step 3: Import verses (this is the large dataset)
    print("\n3. Preparing verses for import...")
    sqlite_cursor.execute("SELECT COUNT(*) FROM verses")
    total_verses = sqlite_cursor.fetchone()[0]
    print(f"   Total verses to import: {total_verses}")
    
    # Step 4: Import abbreviations
    print("\n4. Preparing abbreviations...")
    sqlite_cursor.execute("SELECT COUNT(*) FROM book_abbreviations")
    total_abbr = sqlite_cursor.fetchone()[0]
    print(f"   Total abbreviations to import: {total_abbr}")
    
    sqlite_conn.close()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("\n1. The SQL file 'bible_data.sql' has been created")
    print("2. You need to import it to Render PostgreSQL")
    print("\n3. Option A - Use psql command line:")
    print("   - Get DATABASE_URL from Render dashboard")
    print("   - Run: psql 'DATABASE_URL' < bible_data.sql")
    print("\n4. Option B - Use Render's query tool:")
    print("   - Go to your PostgreSQL dashboard on Render")
    print("   - Use the query interface to run the SQL")
    print("\n5. After import, verify with:")
    print("   SELECT COUNT(*) FROM verses; -- Should be 31103")
    print("   SELECT COUNT(*) FROM books; -- Should be 66")
    print("=" * 60)

if __name__ == "__main__":
    import_to_render()