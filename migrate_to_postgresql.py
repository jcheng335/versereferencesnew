#!/usr/bin/env python3
"""
Migrate SQLite Bible database to PostgreSQL on Render
"""

import sqlite3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pg8000

# Load environment variables
env_path = Path("bible-outline-enhanced-backend/.env")
if env_path.exists():
    load_dotenv(env_path)

def get_postgres_connection():
    """Get PostgreSQL connection using DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        sys.exit(1)
    
    # Parse DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    if database_url.startswith('postgresql://'):
        database_url = database_url[13:]
    elif database_url.startswith('postgres://'):
        database_url = database_url[11:]
    
    auth, host_db = database_url.split('@')
    user, password = auth.split(':')
    host_port, database = host_db.split('/')
    
    if ':' in host_port:
        host, port = host_port.split(':')
        port = int(port)
    else:
        host = host_port
        port = 5432
    
    print(f"Connecting to PostgreSQL at {host}:{port}/{database}")
    
    conn = pg8000.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    
    return conn

def migrate_database():
    """Migrate SQLite to PostgreSQL"""
    
    # Connect to SQLite
    print("Connecting to SQLite database...")
    sqlite_db = "bible-outline-enhanced-backend/bible_verses.db"
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    print("Connecting to PostgreSQL...")
    pg_conn = get_postgres_connection()
    pg_cursor = pg_conn.cursor()
    
    try:
        # Drop existing tables to start fresh
        print("\n1. Dropping existing PostgreSQL tables...")
        pg_cursor.execute("DROP TABLE IF EXISTS book_abbreviations CASCADE")
        pg_cursor.execute("DROP TABLE IF EXISTS verses CASCADE")
        pg_cursor.execute("DROP TABLE IF EXISTS books CASCADE")
        
        # Create new tables in PostgreSQL
        print("\n2. Creating PostgreSQL tables...")
        
        # Create books table
        pg_cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                abbreviation TEXT,
                testament TEXT,
                book_order INTEGER,
                total_chapters INTEGER
            )
        ''')
        
        # Create verses table
        pg_cursor.execute('''
            CREATE TABLE verses (
                id INTEGER PRIMARY KEY,
                book_id INTEGER,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Create book_abbreviations table
        pg_cursor.execute('''
            CREATE TABLE book_abbreviations (
                id INTEGER PRIMARY KEY,
                book_id INTEGER,
                abbreviation TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        # Create indexes for performance
        print("\n3. Creating indexes...")
        pg_cursor.execute("CREATE INDEX idx_verses_book_chapter_verse ON verses(book_id, chapter, verse)")
        pg_cursor.execute("CREATE INDEX idx_books_name ON books(name)")
        pg_cursor.execute("CREATE INDEX idx_book_abbreviations_abbr ON book_abbreviations(abbreviation)")
        
        # Migrate books table
        print("\n4. Migrating books table...")
        sqlite_cursor.execute("SELECT id, name, abbreviation, testament, book_order, total_chapters FROM books")
        books = sqlite_cursor.fetchall()
        
        for book in books:
            pg_cursor.execute(
                "INSERT INTO books (id, name, abbreviation, testament, book_order, total_chapters) VALUES (%s, %s, %s, %s, %s, %s)",
                book
            )
        print(f"   Migrated {len(books)} books")
        
        # Migrate verses table in batches
        print("\n5. Migrating verses table (this may take a moment)...")
        sqlite_cursor.execute("SELECT COUNT(*) FROM verses")
        total_verses = sqlite_cursor.fetchone()[0]
        
        batch_size = 1000
        offset = 0
        
        while offset < total_verses:
            sqlite_cursor.execute(f"SELECT id, book_id, chapter, verse, text FROM verses LIMIT {batch_size} OFFSET {offset}")
            verses_batch = sqlite_cursor.fetchall()
            
            for verse in verses_batch:
                pg_cursor.execute(
                    "INSERT INTO verses (id, book_id, chapter, verse, text) VALUES (%s, %s, %s, %s, %s)",
                    verse
                )
            
            offset += batch_size
            print(f"   Migrated {min(offset, total_verses)}/{total_verses} verses...")
        
        # Migrate book_abbreviations table
        print("\n6. Migrating book_abbreviations table...")
        sqlite_cursor.execute("SELECT id, book_id, abbreviation FROM book_abbreviations")
        abbreviations = sqlite_cursor.fetchall()
        
        for abbr in abbreviations:
            pg_cursor.execute(
                "INSERT INTO book_abbreviations (id, book_id, abbreviation) VALUES (%s, %s, %s)",
                abbr
            )
        print(f"   Migrated {len(abbreviations)} abbreviations")
        
        # Update sequences for auto-increment
        print("\n7. Updating sequences...")
        pg_cursor.execute("SELECT setval('books_id_seq', (SELECT MAX(id) FROM books), true)")
        pg_cursor.execute("SELECT setval('verses_id_seq', (SELECT MAX(id) FROM verses), true)")
        pg_cursor.execute("SELECT setval('book_abbreviations_id_seq', (SELECT MAX(id) FROM book_abbreviations), true)")
        
        # Verify migration
        print("\n8. Verifying migration...")
        pg_cursor.execute("SELECT COUNT(*) FROM books")
        pg_books_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM verses")
        pg_verses_count = pg_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM book_abbreviations")
        pg_abbr_count = pg_cursor.fetchone()[0]
        
        print(f"   Books: {pg_books_count} (expected: 66)")
        print(f"   Verses: {pg_verses_count} (expected: 31103)")
        print(f"   Abbreviations: {pg_abbr_count} (expected: 270)")
        
        # Test a sample verse
        print("\n9. Testing sample verse retrieval...")
        pg_cursor.execute("""
            SELECT v.text 
            FROM verses v 
            JOIN books b ON v.book_id = b.id 
            WHERE b.name = 'Ephesians' AND v.chapter = 4 AND v.verse = 7
        """)
        sample_verse = pg_cursor.fetchone()
        if sample_verse:
            print(f"   Ephesians 4:7: {sample_verse[0][:80]}...")
        
        # Commit changes
        pg_conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show connection info for app
        print("\n10. Database ready for use:")
        print(f"   DATABASE_URL is configured in Render")
        print(f"   Total verses available: {pg_verses_count}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        pg_conn.rollback()
        raise
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("SQLite to PostgreSQL Migration")
    print("=" * 60)
    migrate_database()