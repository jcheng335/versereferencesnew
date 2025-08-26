#!/usr/bin/env python3
"""
Test PostgreSQL connection and verify full verse text is available
"""

import os
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent / "bible-outline-enhanced-backend" / "src"
sys.path.insert(0, str(backend_src))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / "bible-outline-enhanced-backend" / ".env"
load_dotenv(env_path)

from utils.postgres_bible_database import PostgresBibleDatabase

def test_postgres_connection():
    """Test PostgreSQL database connection and verse retrieval"""
    
    print("=" * 60)
    print("Testing PostgreSQL Connection and Verse Retrieval")
    print("=" * 60)
    
    # Initialize database
    try:
        db = PostgresBibleDatabase()
        print("[OK] Connected to PostgreSQL successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to connect to PostgreSQL: {e}")
        return
    
    # Test verse retrieval
    test_cases = [
        ("Ephesians", 4, 7),
        ("Romans", 12, 3),
        ("John", 3, 16),
        ("Genesis", 1, 1),
        ("Revelation", 22, 21)
    ]
    
    print("\nTesting verse retrieval:")
    print("-" * 40)
    
    success_count = 0
    for book, chapter, verse in test_cases:
        text = db.get_verse(book, chapter, verse)
        if text:
            # Show first 60 chars
            display_text = text[:60] + "..." if len(text) > 60 else text
            print(f"[OK] {book} {chapter}:{verse}")
            print(f"  {display_text}")
            success_count += 1
        else:
            print(f"[FAIL] {book} {chapter}:{verse} - Not found")
    
    print("-" * 40)
    print(f"\nResults: {success_count}/{len(test_cases)} verses retrieved successfully")
    
    # Test abbreviation lookup
    print("\nTesting abbreviation lookup:")
    print("-" * 40)
    
    abbr_tests = [
        ("Eph", 4, 7),
        ("Rom", 12, 3),
        ("1 Cor", 12, 14)
    ]
    
    abbr_success = 0
    for abbr, chapter, verse in abbr_tests:
        text = db.get_verse(abbr, chapter, verse)
        if text:
            display_text = text[:60] + "..." if len(text) > 60 else text
            print(f"[OK] {abbr} {chapter}:{verse}")
            print(f"  {display_text}")
            abbr_success += 1
        else:
            print(f"[FAIL] {abbr} {chapter}:{verse} - Not found")
    
    print("-" * 40)
    print(f"\nResults: {abbr_success}/{len(abbr_tests)} abbreviations resolved successfully")
    
    print("\n" + "=" * 60)
    if success_count == len(test_cases) and abbr_success == len(abbr_tests):
        print("[SUCCESS] ALL TESTS PASSED - PostgreSQL is ready!")
    else:
        print("[WARNING] Some tests failed - check database content")
    print("=" * 60)

if __name__ == "__main__":
    test_postgres_connection()