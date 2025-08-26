#!/usr/bin/env python3
"""
Extract all verse references from the new Message PDFs to create perfect training data
"""

import PyPDF2
import re
import json
from pathlib import Path
from typing import List, Set

def extract_all_verses_from_pdf(pdf_path) -> List[str]:
    """Extract all verse references from a PDF"""
    verses = []
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            for page_num in range(len(reader.pages)):
                text = reader.pages[page_num].extract_text()
                
                # Multiple patterns to catch all verse formats
                patterns = [
                    # Standard format: Rom. 5:18 or Rom 5:18
                    r'\b([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)(?:-(\d+))?\b',
                    # Verse lists: Rom. 16:1, 4-5, 16, 20
                    r'\b([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+(?:,\s*\d+(?:-\d+)?)*)\b',
                    # Chapter only: Luke 7
                    r'\b([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+)(?=\s|$|[,;.])',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        verse_ref = match.group(0).strip()
                        if verse_ref not in verses:
                            verses.append(verse_ref)
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    return verses

def process_all_message_pdfs():
    """Process all Message PDFs and extract verses"""
    output_dir = Path("output outlines")
    results = {}
    
    # Map Message files to original outlines
    mappings = {
        "Message_1.pdf": "W24ECT01",
        "Message_2.pdf": "W24ECT02",
        "Message_3.pdf": "W24ECT03",
        "Message_4.pdf": "W24ECT04",
        "Message_5.pdf": "W24ECT05",
        "Message_6.pdf": "W24ECT06",
        "Message_7.pdf": "W24ECT07",
        "Message_8.pdf": "W24ECT08",
        "Message_9.pdf": "W24ECT09",
        "Message_10.pdf": "W24ECT10",
        "Message_11.pdf": "W24ECT11",
        "Message_12.pdf": "W24ECT12",
    }
    
    total_verses = 0
    
    for message_file, outline_id in mappings.items():
        pdf_path = output_dir / message_file
        if pdf_path.exists():
            print(f"\nProcessing {message_file}...")
            verses = extract_all_verses_from_pdf(pdf_path)
            
            # Remove duplicates while preserving order
            unique_verses = []
            seen = set()
            for v in verses:
                if v not in seen:
                    unique_verses.append(v)
                    seen.add(v)
            
            results[outline_id] = {
                "source_file": message_file,
                "verses": unique_verses,
                "count": len(unique_verses)
            }
            
            total_verses += len(unique_verses)
            print(f"  Found {len(unique_verses)} unique verses")
            
            # Show sample
            if unique_verses:
                print("  Sample verses:")
                for v in unique_verses[:5]:
                    print(f"    - {v}")
    
    # Save results
    output_file = "message_pdf_verses.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Total verses extracted: {total_verses}")
    print(f"Results saved to: {output_file}")
    
    # Show statistics
    print(f"\nStatistics by outline:")
    for outline_id, data in results.items():
        print(f"  {outline_id}: {data['count']} verses")
    
    return results

def create_perfect_training_data():
    """Create training data file for perfect detection"""
    results = process_all_message_pdfs()
    
    # Convert to training format
    training_data = {
        "outlines": []
    }
    
    for outline_id, data in results.items():
        outline_data = {
            "outline_id": outline_id,
            "verses": [
                {
                    "reference": verse,
                    "pattern": "extracted",
                    "confidence": 1.0
                }
                for verse in data["verses"]
            ]
        }
        training_data["outlines"].append(outline_data)
    
    # Save training data
    with open("perfect_training_data.json", 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"\nPerfect training data saved to: perfect_training_data.json")
    
    return training_data

if __name__ == "__main__":
    print("Extracting verses from Message PDFs...")
    create_perfect_training_data()