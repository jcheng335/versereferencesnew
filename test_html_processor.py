#!/usr/bin/env python3
"""Test the HTML structured processor for 100% verse population"""

import sys
import os
sys.path.insert(0, 'bible-outline-enhanced-backend/src')

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path("bible-outline-enhanced-backend/.env")
if env_path.exists():
    load_dotenv(env_path)

# Import the processors
from utils.sqlite_bible_database import SQLiteBibleDatabase
from utils.html_structured_processor import HtmlStructuredProcessor

# Initialize database
db_path = "bible-outline-enhanced-backend/bible_verses.db"
bible_db = SQLiteBibleDatabase(db_path)

# Initialize HTML processor
processor = HtmlStructuredProcessor(bible_db)

# Test with sample PDF
test_file = "original outlines/W24ECT12en.pdf"
if not Path(test_file).exists():
    print(f"Test file not found: {test_file}")
    exit(1)

print("=" * 80)
print("Testing HTML Structured Processor for 100% Verse Population")
print("=" * 80)

# Process the document
result = processor.process_document(test_file, "W24ECT12en.pdf")

if result['success']:
    stats = result['stats']
    print("\n== Processing Statistics:")
    print(f"  Total outline points: {stats['total_outline_points']}")
    print(f"  Total verses detected: {stats['total_verses_detected']}")
    print(f"  Total verses populated: {stats['total_verses_populated']}")
    print(f"  Population rate: {stats['population_rate']:.1f}%")
    
    print("\n== Verses by outline level:")
    for level, count in stats['verses_by_level'].items():
        print(f"  {level}: {count} verses")
    
    # Save output
    output_file = "W24ECT12en_populated.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result['text_output'])
    print(f"\n[OK] Populated text saved to: {output_file}")
    
    # Save HTML output
    html_file = "W24ECT12en_populated.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(result['html_output'])
    print(f"[OK] HTML output saved to: {html_file}")
    
    # Show sample of populated text
    print("\n== Sample of populated output:")
    print("-" * 80)
    lines = result['text_output'].split('\n')
    for line in lines[:50]:  # Show first 50 lines
        if line.strip():
            print(line)
    
else:
    print("\n[ERROR] Processing failed!")
    print(result)

print("\n" + "=" * 80)
print("Test complete!")