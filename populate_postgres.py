"""
Populate PostgreSQL database on Render with Bible verses
Migrates verses from SQLite to PostgreSQL for production use
"""

import sqlite3
import psycopg2
import os
from psycopg2.extras import execute_batch

def migrate_to_postgres():
    """Migrate Bible verses from SQLite to PostgreSQL"""
    
    # PostgreSQL connection (Render)
    postgres_url = "postgresql://bible_outline_user:kCMrTRNk1fwFltvgejVyT08aoINDLOCb@dpg-d2lsvpn5r7bs73e32s40-a.oregon-postgres.render.com/bible_outline_db"
    
    # SQLite connection (local)
    sqlite_db = "bible_verses.db"
    
    if not os.path.exists(sqlite_db):
        print(f"SQLite database {sqlite_db} not found!")
        return
    
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()
    
    print("Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(postgres_url)
    pg_cursor = pg_conn.cursor()
    
    try:
        # Create bible_verses table in PostgreSQL
        print("Creating bible_verses table in PostgreSQL...")
        pg_cursor.execute("""
            CREATE TABLE IF NOT EXISTS bible_verses (
                id SERIAL PRIMARY KEY,
                book VARCHAR(50) NOT NULL,
                chapter INTEGER NOT NULL,
                verse_number INTEGER NOT NULL,
                text TEXT NOT NULL,
                UNIQUE(book, chapter, verse_number)
            )
        """)
        
        # Create indexes for faster queries
        pg_cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bible_verses_book 
            ON bible_verses(book)
        """)
        
        pg_cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bible_verses_chapter 
            ON bible_verses(book, chapter)
        """)
        
        pg_conn.commit()
        
        # Get all verses from SQLite
        print("Reading verses from SQLite...")
        sqlite_cursor.execute("""
            SELECT book, chapter, verse_number, text 
            FROM bible_verses
            ORDER BY id
        """)
        
        verses = sqlite_cursor.fetchall()
        print(f"Found {len(verses)} verses to migrate")
        
        # Clear existing data in PostgreSQL (if any)
        print("Clearing existing data in PostgreSQL...")
        pg_cursor.execute("TRUNCATE TABLE bible_verses RESTART IDENTITY")
        pg_conn.commit()
        
        # Insert verses into PostgreSQL in batches
        print("Inserting verses into PostgreSQL...")
        batch_size = 1000
        
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i+batch_size]
            
            execute_batch(
                pg_cursor,
                """
                INSERT INTO bible_verses (book, chapter, verse_number, text)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (book, chapter, verse_number) DO NOTHING
                """,
                batch,
                page_size=100
            )
            
            pg_conn.commit()
            print(f"Inserted batch {i//batch_size + 1}/{(len(verses) + batch_size - 1)//batch_size}")
        
        # Verify the migration
        pg_cursor.execute("SELECT COUNT(*) FROM bible_verses")
        count = pg_cursor.fetchone()[0]
        print(f"\nMigration complete! {count} verses now in PostgreSQL")
        
        # Show some sample verses
        pg_cursor.execute("""
            SELECT book, chapter, verse_number, LEFT(text, 50) as text_preview
            FROM bible_verses
            LIMIT 5
        """)
        
        print("\nSample verses:")
        for row in pg_cursor.fetchall():
            print(f"  {row[0]} {row[1]}:{row[2]} - {row[3]}...")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_to_postgres()