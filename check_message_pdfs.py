#!/usr/bin/env python3
"""
Check if the new Message PDFs have extractable text with verse references
"""

import PyPDF2
from pathlib import Path

def check_pdf(pdf_path):
    """Extract and check text from PDF"""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"\nChecking: {pdf_path.name}")
            print(f"Pages: {len(reader.pages)}")
            
            # Extract text from first page
            text = reader.pages[0].extract_text()
            
            # Check if text exists
            if text and len(text.strip()) > 100:
                print("Status: TEXT-BASED PDF")
                
                # Look for verse references
                import re
                verse_pattern = r'[A-Z][a-z]+\.?\s+\d+:\d+'
                verses = re.findall(verse_pattern, text)
                
                if verses:
                    print(f"Found {len(verses)} verse references on first page")
                    print("Sample verses:")
                    for v in verses[:5]:
                        print(f"  - {v}")
                else:
                    print("No verse references found on first page")
                    
                # Show sample text
                print("\nSample text (first 300 chars):")
                sample = text[:300].replace('\n', ' ')
                print(sample)
            else:
                print("Status: IMAGE-BASED PDF or NO TEXT")
                
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

def main():
    output_dir = Path("output outlines")
    
    # Check all Message PDFs
    message_files = sorted(output_dir.glob("Message_*.pdf"))
    
    print(f"Found {len(message_files)} Message PDF files")
    
    for pdf_path in message_files:
        check_pdf(pdf_path)
    
    # Also check MSG12VerseReferences.pdf for comparison
    msg12_path = Path("MSG12VerseReferences.pdf")
    if msg12_path.exists():
        print("\n" + "="*50)
        print("For comparison - original MSG12VerseReferences:")
        check_pdf(msg12_path)

if __name__ == "__main__":
    main()