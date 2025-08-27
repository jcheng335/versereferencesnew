#!/usr/bin/env python3
"""
Test the full pipeline locally with W24ECT02en.pdf
"""

import sys
import os
import json
sys.path.append('bible-outline-enhanced-backend/src')

from utils.enhanced_processor import EnhancedProcessor
import uuid

def test_w24ect02():
    """Test with W24ECT02en.pdf - Message Two"""
    
    # Initialize processor
    db_path = "bible-outline-enhanced-backend/src/bible_verses.db"
    processor = EnhancedProcessor(db_path, use_llm_first=True, use_html_processor=True)
    
    # Process document
    pdf_path = "original outlines/W24ECT02en.pdf"
    filename = "W24ECT02en.pdf"
    
    print("=== PROCESSING DOCUMENT ===")
    result = processor.process_document(pdf_path, filename, use_llm=True, force_html=True)
    
    if result['success']:
        session_id = result['session_id']
        print(f"Session ID: {session_id}")
        print(f"References found: {result['references_found']}")
        print(f"Total verses: {result['total_verses']}")
        
        # Populate verses
        print("\n=== POPULATING VERSES ===")
        populate_result = processor.populate_verses(session_id, format_type='margin')
        
        if populate_result['success']:
            print("Success!")
            
            # Save HTML output for inspection
            html_content = populate_result.get('html_content', '')
            if html_content:
                with open('test_output_w24ect02.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("HTML output saved to test_output_w24ect02.html")
                
                # Check for key elements
                print("\n=== CHECKING KEY ELEMENTS ===")
                checks = {
                    'Message Two': 'Message Two' in html_content,
                    'Christ as the Emancipator': 'Christ as the Emancipator' in html_content,
                    'Rom. 8:2': 'Rom. 8:2' in html_content or 'Romans 8:2' in html_content,
                    'Rom. 8:31': 'Rom. 8:31' in html_content or 'Romans 8:31' in html_content,
                    'Rom. 8:39': 'Rom. 8:39' in html_content or 'Romans 8:39' in html_content,
                    'Scripture Reading': 'Scripture Reading' in html_content,
                    'blue color': 'color: blue' in html_content or 'color:blue' in html_content,
                    'Roman numeral I': 'I.' in html_content or '>I<' in html_content
                }
                
                for check, result in checks.items():
                    status = "✓" if result else "✗"
                    print(f"{status} {check}")
            else:
                print("No HTML content returned!")
                
            # Show populated text
            text_content = populate_result.get('populated_content', '')
            if text_content:
                print("\n=== FIRST 1000 CHARS OF OUTPUT ===")
                print(text_content[:1000])
        else:
            print(f"Populate failed: {populate_result.get('error')}")
    else:
        print(f"Processing failed: {result.get('error')}")

if __name__ == "__main__":
    test_w24ect02()