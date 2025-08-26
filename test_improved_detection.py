#!/usr/bin/env python3
"""
Test improved verse detection with problematic cases
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

def test_verse_lookups():
    """Test problematic verse lookups"""
    
    print("=" * 60)
    print("Testing Improved Verse Detection")
    print("=" * 60)
    
    # Initialize database
    try:
        db = PostgresBibleDatabase()
        print("[OK] Connected to PostgreSQL")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return
    
    # Test problematic verses
    test_cases = [
        # Written out forms
        ("First Corinthians", 1, 2),
        ("First Peter", 1, 7),
        ("Second Timothy", 2, 15),
        
        # Abbreviations
        ("1 Cor", 1, 23),
        ("1 Cor.", 1, 24),
        ("1 Corinthians", 1, 2),
        
        # Standard forms
        ("Ephesians", 4, 7),
        ("Romans", 12, 3),
    ]
    
    print("\nTesting verse lookups with normalization:")
    print("-" * 40)
    
    success_count = 0
    for book, chapter, verse in test_cases:
        text = db.get_verse(book, chapter, verse)
        if text:
            display_text = text[:50] + "..." if len(text) > 50 else text
            print(f"[OK] {book} {chapter}:{verse}")
            print(f"     Normalized to: {db._normalize_book_name(book)}")
            print(f"     Text: {display_text}")
            success_count += 1
        else:
            print(f"[FAIL] {book} {chapter}:{verse} - Not found")
            print(f"       Normalized to: {db._normalize_book_name(book)}")
    
    print("-" * 40)
    print(f"\nResults: {success_count}/{len(test_cases)} verses retrieved")
    
    # Test specific problem from user
    print("\nTesting specific user-reported issues:")
    print("-" * 40)
    
    # First Corinthians 1:2
    text = db.get_verse("First Corinthians", 1, 2)
    if text:
        print(f"[OK] 'First Corinthians 1:2' found:")
        print(f"     {text[:80]}...")
    else:
        print(f"[FAIL] 'First Corinthians 1:2' not found")
    
    # 1 Cor. 1:23-24
    for v in [23, 24]:
        text = db.get_verse("1 Cor", 1, v)
        if text:
            print(f"[OK] '1 Cor. 1:{v}' found:")
            print(f"     {text[:80]}...")
        else:
            print(f"[FAIL] '1 Cor. 1:{v}' not found")
    
    print("-" * 40)
    print("\n[INFO] If verses are not found, check the books table in PostgreSQL")
    print("       to see exact book names stored in the database.")

if __name__ == "__main__":
    test_verse_lookups()