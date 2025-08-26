#!/usr/bin/env python3
"""
Convert Message PDFs to HTML format for easier processing and training
"""

import PyPDF2
import re
from pathlib import Path
from typing import List, Dict, Tuple

def pdf_to_html(pdf_path: Path) -> str:
    """Convert PDF to HTML with proper formatting"""
    html_lines = []
    html_lines.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bible Outline with Verses</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .verse-ref { color: blue; float: left; width: 150px; margin-right: 20px; font-size: 12px; }
        .outline-text { margin-left: 170px; }
        .scripture-reading { font-weight: bold; margin-bottom: 10px; }
        .outline-point { margin: 10px 0; clear: both; }
        .sub-point { margin-left: 20px; }
        h1 { text-align: center; }
        .clear { clear: both; }
    </style>
</head>
<body>
""")
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            for page_num in range(len(reader.pages)):
                text = reader.pages[page_num].extract_text()
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if line starts with verse reference (blue text in margin)
                    verse_pattern = r'^([1-3]?\s*[A-Z][a-z]+\.?\s+\d+[:\d\-,]*)'
                    verse_match = re.match(verse_pattern, line)
                    
                    if verse_match:
                        # This is a verse reference in the margin
                        verse_ref = verse_match.group(1)
                        rest_of_line = line[len(verse_ref):].strip()
                        
                        html_lines.append(f'<div class="outline-point">')
                        html_lines.append(f'  <span class="verse-ref">{verse_ref}</span>')
                        html_lines.append(f'  <span class="outline-text">{rest_of_line}</span>')
                        html_lines.append(f'</div>')
                        html_lines.append('<div class="clear"></div>')
                    
                    elif 'Scripture Reading' in line:
                        html_lines.append(f'<div class="scripture-reading">{line}</div>')
                    
                    elif 'Message' in line and 'Hymns' not in line:
                        html_lines.append(f'<h1>{line}</h1>')
                    
                    elif re.match(r'^[IVX]+\.', line) or re.match(r'^[A-Z]\.', line) or re.match(r'^\d+\.', line):
                        # Outline points
                        html_lines.append(f'<div class="outline-point">')
                        html_lines.append(f'  <span class="outline-text">{line}</span>')
                        html_lines.append(f'</div>')
                    
                    else:
                        # Regular text
                        html_lines.append(f'<p>{line}</p>')
        
        html_lines.append("""
</body>
</html>
""")
        
        return '\n'.join(html_lines)
    
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return ""

def process_all_message_pdfs():
    """Convert all Message PDFs to HTML"""
    output_dir = Path("output outlines")
    html_dir = Path("html_outlines")
    html_dir.mkdir(exist_ok=True)
    
    for pdf_file in output_dir.glob("Message_*.pdf"):
        print(f"Converting {pdf_file.name} to HTML...")
        html_content = pdf_to_html(pdf_file)
        
        if html_content:
            html_file = html_dir / pdf_file.name.replace('.pdf', '.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  Saved to {html_file}")
    
    print("\nAll PDFs converted to HTML!")

if __name__ == "__main__":
    process_all_message_pdfs()