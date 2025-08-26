#!/usr/bin/env python3
"""
PDF to HTML Converter for Bible Outlines
Converts PDF to structured HTML that's easier for LLM to process
"""

import pdfplumber
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import html

class PDFToHTMLConverter:
    """Convert PDF outlines to structured HTML"""
    
    def __init__(self):
        self.outline_pattern = re.compile(r'^([IVX]+\.|[A-Z]\.|[1-9]\d?\.|[a-z]\.)')
        
    def convert_pdf_to_html(self, pdf_path: str) -> str:
        """
        Convert PDF to structured HTML format
        Returns HTML string with outline structure preserved
        """
        try:
            # Extract text from PDF
            text_lines = self._extract_pdf_lines(pdf_path)
            
            # Build HTML structure
            html_content = self._build_html_structure(text_lines)
            
            return html_content
            
        except Exception as e:
            raise Exception(f"Error converting PDF to HTML: {str(e)}")
    
    def _extract_pdf_lines(self, pdf_path: str) -> List[str]:
        """Extract text lines from PDF"""
        lines = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Split into lines and clean
                    page_lines = text.split('\n')
                    for line in page_lines:
                        line = line.strip()
                        if line:
                            lines.append(line)
        
        return lines
    
    def _build_html_structure(self, lines: List[str]) -> str:
        """Build structured HTML from text lines"""
        
        # Start HTML document
        soup = BeautifulSoup('<!DOCTYPE html><html><head><title>Bible Outline</title></head><body></body></html>', 'html.parser')
        body = soup.body
        
        # Add CSS for styling
        style = soup.new_tag('style')
        style.string = """
        .outline-container { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .title { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
        .scripture-reading { background: #f0f0f0; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }
        .verse-ref { color: #1976D2; font-weight: bold; }
        .outline-level-1 { margin-left: 0px; margin-top: 15px; font-weight: bold; }
        .outline-level-2 { margin-left: 20px; margin-top: 10px; }
        .outline-level-3 { margin-left: 40px; margin-top: 5px; }
        .outline-level-4 { margin-left: 60px; margin-top: 5px; }
        .parenthetical { color: #666; font-style: italic; }
        """
        soup.head.append(style)
        
        # Create container
        container = soup.new_tag('div', attrs={'class': 'outline-container'})
        body.append(container)
        
        # Process lines
        for i, line in enumerate(lines):
            # Title detection
            if i == 0 or 'Message' in line and any(word in line for word in ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve']):
                div = soup.new_tag('div', attrs={'class': 'title'})
                div.string = line
                container.append(div)
            
            # Scripture Reading detection
            elif line.startswith('Scripture Reading:'):
                div = soup.new_tag('div', attrs={'class': 'scripture-reading'})
                # Mark verse references in Scripture Reading
                processed_line = self._mark_verse_references(line)
                div.append(BeautifulSoup(processed_line, 'html.parser'))
                container.append(div)
            
            # Outline points
            elif self._is_outline_point(line):
                level = self._get_outline_level(line)
                div = soup.new_tag('div', attrs={'class': f'outline-level-{level}'})
                
                # Mark verse references in the line
                processed_line = self._mark_verse_references(line)
                div.append(BeautifulSoup(processed_line, 'html.parser'))
                container.append(div)
            
            # Regular text
            else:
                div = soup.new_tag('div')
                # Mark verse references
                processed_line = self._mark_verse_references(line)
                div.append(BeautifulSoup(processed_line, 'html.parser'))
                container.append(div)
        
        return str(soup.prettify())
    
    def _is_outline_point(self, line: str) -> bool:
        """Check if line is an outline point"""
        return bool(self.outline_pattern.match(line))
    
    def _get_outline_level(self, line: str) -> int:
        """Determine outline level (1-4) based on marker"""
        if re.match(r'^[IVX]+\.', line):
            return 1  # Roman numerals
        elif re.match(r'^[A-Z]\.', line):
            return 2  # Capital letters
        elif re.match(r'^[1-9]\d?\.', line):
            return 3  # Numbers
        elif re.match(r'^[a-z]\.', line):
            return 4  # Lowercase letters
        return 1
    
    def _mark_verse_references(self, text: str) -> str:
        """Mark verse references with span tags for easy identification"""
        
        # Pattern for various verse formats
        patterns = [
            # Full references: Rom. 5:1-11, John 14:6a
            r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?[a-z]?)',
            # Parenthetical references: (Acts 10:43)
            r'(\([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?[a-z]?\))',
            # Standalone verses: v. 5, vv. 1-11
            r'(vv?\.\s+\d+(?:-\d+)?)',
            # cf. references
            r'(cf\.\s+[1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?)',
        ]
        
        result = text
        for pattern in patterns:
            result = re.sub(pattern, r'<span class="verse-ref">\1</span>', result)
        
        # Mark parenthetical content
        result = re.sub(r'(\([^)]+\))', r'<span class="parenthetical">\1</span>', result)
        
        return result

    def convert_and_structure(self, pdf_path: str) -> Dict:
        """
        Convert PDF to structured data format for easier processing
        Returns dict with title, scripture_reading, and outline_points
        """
        lines = self._extract_pdf_lines(pdf_path)
        
        result = {
            'title': '',
            'scripture_reading': '',
            'outline_points': []
        }
        
        current_outline = None
        
        for i, line in enumerate(lines):
            # Extract title
            if i == 0 or ('Message' in line and any(word in line for word in ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve'])):
                result['title'] = line
            
            # Extract Scripture Reading
            elif line.startswith('Scripture Reading:'):
                result['scripture_reading'] = line.replace('Scripture Reading:', '').strip()
            
            # Extract outline points
            elif self._is_outline_point(line):
                level = self._get_outline_level(line)
                outline_point = {
                    'level': level,
                    'text': line,
                    'verses': self._extract_verses_from_text(line)
                }
                result['outline_points'].append(outline_point)
        
        return result
    
    def _extract_verses_from_text(self, text: str) -> List[str]:
        """Extract verse references from text"""
        verses = []
        
        # Various verse patterns
        patterns = [
            r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?[a-z]?)',
            r'vv?\.\s+\d+(?:-\d+)?',
            r'cf\.\s+[1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:-\d+)?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            verses.extend(matches)
        
        return verses