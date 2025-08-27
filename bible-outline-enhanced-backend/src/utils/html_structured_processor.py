#!/usr/bin/env python3
"""
HTML-based Structured Document Processor
Converts PDF to HTML, extracts structure, detects verses, populates, and converts back
"""

import re
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pdfplumber
from bs4 import BeautifulSoup
from openai import OpenAI

@dataclass
class OutlineNode:
    """Represents a node in the outline structure"""
    level: str  # 'scripture_reading', 'I', 'A', '1', 'a', 'text'
    number: str  # The outline number/letter
    text: str  # The outline text
    verses: List[Dict[str, Any]]  # Associated verses
    children: List['OutlineNode']  # Child nodes
    line_number: int  # Original line number in document
    
    def to_dict(self):
        return {
            'level': self.level,
            'number': self.number,
            'text': self.text,
            'verses': self.verses,
            'children': [child.to_dict() for child in self.children],
            'line_number': self.line_number
        }

class HtmlStructuredProcessor:
    def __init__(self, bible_db, openai_key: str = None):
        """Initialize the HTML-based processor"""
        self.bible_db = bible_db
        self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        if self.openai_key:
            self.client = OpenAI(api_key=self.openai_key)
    
    def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Main processing pipeline:
        1. PDF -> HTML
        2. HTML -> Structured Data
        3. Detect verses in structure
        4. Populate verses
        5. Return structured result
        """
        print("Step 1: Converting PDF to HTML...")
        html_content = self._pdf_to_html(file_path)
        
        print("Step 2: Extracting structured data from HTML...")
        structured_data = self._html_to_structured_data(html_content)
        
        print("Step 3: Detecting verses in structured data...")
        structured_with_verses = self._detect_verses_in_structure(structured_data)
        
        print("Step 4: Populating verse texts...")
        populated_structure = self._populate_verse_texts(structured_with_verses)
        
        print("Step 5: Generating final output...")
        return {
            'success': True,
            'structured_data': populated_structure,
            'html_output': self._structure_to_html(populated_structure),
            'text_output': self._structure_to_text(populated_structure),
            'stats': self._calculate_stats(populated_structure)
        }
    
    def _pdf_to_html(self, file_path: str) -> str:
        """Convert PDF to structured HTML preserving formatting"""
        html_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text with positioning info
                text = page.extract_text()
                if not text:
                    continue
                
                # Convert to HTML with structure preservation
                lines = text.split('\n')
                html_parts.append(f'<div class="page" data-page="{page_num + 1}">')
                
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        html_parts.append('<br/>')
                        continue
                    
                    # Detect document metadata (title, message number, hymns)
                    if page_num == 0 and line_num < 10:
                        # Check for Message Number
                        if re.match(r'^(Message|MESSAGE)\s+(\w+)', line, re.IGNORECASE):
                            html_parts.append(f'<div class="message-number" data-line="{line_num}">{line}</div>')
                        # Check for hymn references
                        elif re.match(r'.*(Hymn|hymn)s?\s*[:.]?\s*\d+', line, re.IGNORECASE):
                            html_parts.append(f'<div class="hymn-reference" data-line="{line_num}">{line}</div>')
                        # Check for Scripture Reading
                        elif line.startswith('Scripture Reading:'):
                            html_parts.append(f'<div class="scripture-reading" data-line="{line_num}">{line}</div>')
                        # Otherwise treat as potential title/subtitle
                        elif line and not re.match(r'^[IVX]+\.', line):
                            html_parts.append(f'<div class="title-text" data-line="{line_num}">{line}</div>')
                        else:
                            html_parts.append(f'<div class="text" data-line="{line_num}">{line}</div>')
                    # Regular content detection
                    elif line.startswith('Scripture Reading:'):
                        html_parts.append(f'<div class="scripture-reading" data-line="{line_num}">{line}</div>')
                    elif re.match(r'^[IVX]+\.', line):
                        html_parts.append(f'<div class="outline-roman" data-line="{line_num}">{line}</div>')
                    elif re.match(r'^[A-Z]\.', line):
                        html_parts.append(f'<div class="outline-letter" data-line="{line_num}">{line}</div>')
                    elif re.match(r'^\d+\.', line):
                        html_parts.append(f'<div class="outline-number" data-line="{line_num}">{line}</div>')
                    elif re.match(r'^[a-z]\.', line):
                        html_parts.append(f'<div class="outline-subletter" data-line="{line_num}">{line}</div>')
                    else:
                        html_parts.append(f'<div class="text" data-line="{line_num}">{line}</div>')
                
                html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _html_to_structured_data(self, html_content: str) -> OutlineNode:
        """Parse HTML into hierarchical structured data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Create root node
        root = OutlineNode(
            level='root',
            number='',
            text='Document Root',
            verses=[],
            children=[],
            line_number=0
        )
        
        # Stack for maintaining hierarchy
        current_parent = {
            'root': root,
            'roman': None,
            'letter': None,
            'number': None,
            'subletter': None
        }
        
        # Process each element
        for element in soup.find_all(['div']):
            line_num = int(element.get('data-line', 0))
            text = element.text.strip()
            
            if 'scripture-reading' in element.get('class', []):
                node = OutlineNode(
                    level='scripture_reading',
                    number='',
                    text=text,
                    verses=[],
                    children=[],
                    line_number=line_num
                )
                root.children.append(node)
                
            elif 'outline-roman' in element.get('class', []):
                match = re.match(r'^([IVX]+)\.(.+)', text)
                if match:
                    node = OutlineNode(
                        level='I',
                        number=match.group(1),
                        text=match.group(2).strip(),
                        verses=[],
                        children=[],
                        line_number=line_num
                    )
                    root.children.append(node)
                    current_parent['roman'] = node
                    current_parent['letter'] = None
                    current_parent['number'] = None
                    
            elif 'outline-letter' in element.get('class', []):
                match = re.match(r'^([A-Z])\.(.+)', text)
                if match and current_parent['roman']:
                    node = OutlineNode(
                        level='A',
                        number=match.group(1),
                        text=match.group(2).strip(),
                        verses=[],
                        children=[],
                        line_number=line_num
                    )
                    current_parent['roman'].children.append(node)
                    current_parent['letter'] = node
                    current_parent['number'] = None
                    
            elif 'outline-number' in element.get('class', []):
                match = re.match(r'^(\d+)\.(.+)', text)
                if match:
                    node = OutlineNode(
                        level='1',
                        number=match.group(1),
                        text=match.group(2).strip(),
                        verses=[],
                        children=[],
                        line_number=line_num
                    )
                    parent = current_parent['letter'] or current_parent['roman'] or root
                    parent.children.append(node)
                    current_parent['number'] = node
                    
            elif 'outline-subletter' in element.get('class', []):
                match = re.match(r'^([a-z])\.(.+)', text)
                if match and current_parent['number']:
                    node = OutlineNode(
                        level='a',
                        number=match.group(1),
                        text=match.group(2).strip(),
                        verses=[],
                        children=[],
                        line_number=line_num
                    )
                    current_parent['number'].children.append(node)
                    
            else:
                # Regular text - append to most recent outline point
                if current_parent['number']:
                    current_parent['number'].text += ' ' + text
                elif current_parent['letter']:
                    current_parent['letter'].text += ' ' + text
                elif current_parent['roman']:
                    current_parent['roman'].text += ' ' + text
        
        return root
    
    def _detect_verses_in_structure(self, root: OutlineNode) -> OutlineNode:
        """Detect all verse references in the structured data"""
        
        # Get Scripture Reading reference for context
        scripture_context = self._extract_scripture_context(root)
        
        def process_node(node: OutlineNode, context_book: str = None, context_chapter: int = None):
            """Recursively process each node to find verses"""
            
            # Detect verses in this node's text
            verses = self._extract_verses_from_text(node.text, context_book, context_chapter)
            node.verses = verses
            
            # Update context if we found a Scripture Reading
            if node.level == 'scripture_reading':
                # Extract book and chapter from first reference
                first_ref = verses[0] if verses else None
                if first_ref:
                    context_book = first_ref['book']
                    context_chapter = first_ref['chapter']
            
            # Process children with updated context
            for child in node.children:
                process_node(child, context_book, context_chapter)
        
        # Start processing from root
        process_node(root)
        return root
    
    def _extract_scripture_context(self, root: OutlineNode) -> Optional[Dict]:
        """Extract Scripture Reading reference for context"""
        for child in root.children:
            if child.level == 'scripture_reading':
                # Parse the Scripture Reading
                match = re.search(r'Scripture Reading:\s*(.+)', child.text)
                if match:
                    ref_text = match.group(1)
                    # Parse first reference for context
                    first_ref = re.match(r'([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+)', ref_text)
                    if first_ref:
                        return {
                            'book': first_ref.group(1).strip(),
                            'chapter': int(first_ref.group(2))
                        }
        return None
    
    def _extract_verses_from_text(self, text: str, context_book: str = None, context_chapter: int = None) -> List[Dict]:
        """Extract all verse references from text using multiple methods"""
        verses = []
        
        # Use GPT-5 if available
        if self.client and context_book:
            verses.extend(self._extract_with_llm(text, context_book, context_chapter))
        
        # Also use regex patterns
        verses.extend(self._extract_with_regex(text, context_book, context_chapter))
        
        # Deduplicate
        seen = set()
        unique_verses = []
        for v in verses:
            key = f"{v['book']}_{v['chapter']}_{v['start_verse']}_{v.get('end_verse', '')}"
            if key not in seen:
                seen.add(key)
                unique_verses.append(v)
        
        return unique_verses
    
    def _extract_with_llm(self, text: str, context_book: str, context_chapter: int) -> List[Dict]:
        """Use LLM to extract verses"""
        if not text or len(text) < 5:
            return []
        
        prompt = f"""Extract Bible verse references from this text.
Context: We are in {context_book} chapter {context_chapter}.
For standalone verses (v., vv.), use this context.

Text: {text}

Return JSON array of verses found:
[{{"reference": "original", "book": "Book", "chapter": N, "start_verse": N, "end_verse": N}}]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "Extract Bible verses. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1000,
                timeout=30
            )
            
            content = response.choices[0].message.content
            # Parse JSON response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            verses = json.loads(content)
            return verses if isinstance(verses, list) else []
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return []
    
    def _extract_with_regex(self, text: str, context_book: str = None, context_chapter: int = None) -> List[Dict]:
        """Extract verses using comprehensive regex patterns"""
        verses = []
        
        # Pattern 1: Full references (Book Chapter:Verse-EndVerse)
        pattern1 = r'([1-3]?\s*[A-Z][a-z]+(?:\s+[A-Z]?[a-z]*)?)\s*\.?\s*(\d+):(\d+)(?:-(\d+))?'
        for match in re.finditer(pattern1, text):
            verses.append({
                'reference': match.group(0),
                'book': match.group(1).strip().replace('.', ''),
                'chapter': int(match.group(2)),
                'start_verse': int(match.group(3)),
                'end_verse': int(match.group(4)) if match.group(4) else None
            })
        
        # Pattern 2: Standalone verses (v. N, vv. N-M)
        if context_book and context_chapter:
            pattern2 = r'v(?:v)?\.?\s+(\d+)(?:-(\d+))?'
            for match in re.finditer(pattern2, text):
                verses.append({
                    'reference': match.group(0),
                    'book': context_book,
                    'chapter': context_chapter,
                    'start_verse': int(match.group(1)),
                    'end_verse': int(match.group(2)) if match.group(2) else None
                })
        
        # Pattern 3: Verse lists (N, M, P-Q)
        if context_book and context_chapter and 'Scripture Reading' not in text:
            pattern3 = r'(?:^|[^\d])(\d+)(?:-(\d+))?(?:,\s*\d+(?:-\d+)?)*'
            for match in re.finditer(pattern3, text):
                # Check if this looks like a verse reference
                num = int(match.group(1))
                if 1 <= num <= 200:  # Reasonable verse range
                    verses.append({
                        'reference': match.group(0).strip(),
                        'book': context_book,
                        'chapter': context_chapter,
                        'start_verse': num,
                        'end_verse': int(match.group(2)) if match.group(2) else None
                    })
        
        return verses
    
    def _populate_verse_texts(self, root: OutlineNode) -> OutlineNode:
        """Populate actual verse texts from the Bible database"""
        
        def populate_node(node: OutlineNode):
            """Recursively populate verse texts"""
            
            # Populate verses for this node
            for verse in node.verses:
                if 'text' not in verse or not verse.get('text'):
                    verse_text = self._fetch_verse_text(verse)
                    verse['text'] = verse_text or '[Verse not found]'
            
            # Process children
            for child in node.children:
                populate_node(child)
        
        populate_node(root)
        return root
    
    def _fetch_verse_text(self, verse_ref: Dict) -> Optional[str]:
        """Fetch verse text from database"""
        try:
            book = verse_ref.get('book', '')
            chapter = verse_ref.get('chapter', 0)
            start = verse_ref.get('start_verse', 0)
            end = verse_ref.get('end_verse', start)
            
            if not book or not chapter or not start:
                return None
            
            # Handle None values
            if end is None:
                end = start
            
            # Map common abbreviations to full book names
            book_mapping = {
                'Gen': 'Genesis', 'Ex': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers',
                'Deut': 'Deuteronomy', 'Josh': 'Joshua', 'Judg': 'Judges', 'Ruth': 'Ruth',
                '1 Sam': '1 Samuel', '2 Sam': '2 Samuel', '1 Kings': '1 Kings', '2 Kings': '2 Kings',
                '1 Chron': '1 Chronicles', '2 Chron': '2 Chronicles', 'Ezra': 'Ezra', 'Neh': 'Nehemiah',
                'Esth': 'Esther', 'Job': 'Job', 'Ps': 'Psalms', 'Psalm': 'Psalms', 'Prov': 'Proverbs',
                'Eccl': 'Ecclesiastes', 'Song': 'Song of Solomon', 'Isa': 'Isaiah', 'Jer': 'Jeremiah',
                'Lam': 'Lamentations', 'Ezek': 'Ezekiel', 'Dan': 'Daniel', 'Hos': 'Hosea',
                'Joel': 'Joel', 'Amos': 'Amos', 'Obad': 'Obadiah', 'Jonah': 'Jonah',
                'Mic': 'Micah', 'Nah': 'Nahum', 'Hab': 'Habakkuk', 'Zeph': 'Zephaniah',
                'Hag': 'Haggai', 'Zech': 'Zechariah', 'Mal': 'Malachi',
                'Matt': 'Matthew', 'Mark': 'Mark', 'Luke': 'Luke', 'John': 'John',
                'Acts': 'Acts', 'Rom': 'Romans', '1 Cor': '1 Corinthians', '2 Cor': '2 Corinthians',
                'Gal': 'Galatians', 'Eph': 'Ephesians', 'Phil': 'Philippians', 'Col': 'Colossians',
                '1 Thess': '1 Thessalonians', '2 Thess': '2 Thessalonians', '1 Tim': '1 Timothy',
                '2 Tim': '2 Timothy', 'Titus': 'Titus', 'Philem': 'Philemon', 'Heb': 'Hebrews',
                'James': 'James', '1 Pet': '1 Peter', '2 Pet': '2 Peter', '1 John': '1 John',
                '2 John': '2 John', '3 John': '3 John', 'Jude': 'Jude', 'Rev': 'Revelation',
                # Handle variations
                'Psa': 'Psalms', 'Mt': 'Matthew', 'Mk': 'Mark', 'Lk': 'Luke', 'Jn': 'John',
                'Ro': 'Romans', '1Co': '1 Corinthians', '2Co': '2 Corinthians',
                'Ga': 'Galatians', 'Eph': 'Ephesians', 'Php': 'Philippians', 'Col': 'Colossians',
                '1Th': '1 Thessalonians', '2Th': '2 Thessalonians', '1Ti': '1 Timothy',
                '2Ti': '2 Timothy', 'Tit': 'Titus', 'Phm': 'Philemon', 'Heb': 'Hebrews',
                'Jas': 'James', '1Pe': '1 Peter', '2Pe': '2 Peter', '1Jn': '1 John',
                '2Jn': '2 John', '3Jn': '3 John', 'Jud': 'Jude', 'Re': 'Revelation'
            }
            
            # Map book name if needed
            full_book = book_mapping.get(book, book)
            
            # Fetch from database
            verses = []
            for verse_num in range(start, end + 1):
                text = self.bible_db.get_verse(full_book, chapter, verse_num)
                if text:
                    verses.append(f"{verse_num}. {text}")
                else:
                    # Try with original book name if mapping didn't work
                    text = self.bible_db.get_verse(book, chapter, verse_num)
                    if text:
                        verses.append(f"{verse_num}. {text}")
            
            return ' '.join(verses) if verses else None
            
        except Exception as e:
            print(f"Error fetching verse: {e}")
            return None
    
    def _structure_to_html(self, root: OutlineNode) -> str:
        """Convert structured data back to HTML with verses"""
        html_parts = ['<html><body>']
        
        def render_node(node: OutlineNode, indent: int = 0):
            """Recursively render node to HTML"""
            if node.level == 'root':
                # Skip root, just process children
                for child in node.children:
                    render_node(child, indent)
                return
            
            # Add the outline point
            indent_str = '&nbsp;' * (indent * 4)
            
            if node.level == 'scripture_reading':
                html_parts.append(f'<div class="scripture-reading">{node.text}</div>')
            else:
                # Format outline number/letter with text
                if node.number:
                    html_parts.append(f'<div class="outline-{node.level}">{indent_str}{node.number}. {node.text}</div>')
                else:
                    html_parts.append(f'<div class="text">{indent_str}{node.text}</div>')
            
            # Add verses below the outline point
            if node.verses:
                html_parts.append('<div class="verses" style="margin-left: 40px; color: blue;">')
                for verse in node.verses:
                    if verse.get('text'):
                        html_parts.append(f'<div class="verse">')
                        html_parts.append(f'<span class="verse-ref">{verse["reference"]}:</span> ')
                        html_parts.append(f'<span class="verse-text">{verse["text"]}</span>')
                        html_parts.append('</div>')
                html_parts.append('</div>')
            
            # Process children
            for child in node.children:
                render_node(child, indent + 1)
        
        render_node(root)
        html_parts.append('</body></html>')
        return '\n'.join(html_parts)
    
    def _structure_to_text(self, root: OutlineNode) -> str:
        """Convert structured data to plain text with verses"""
        text_parts = []
        
        def render_node(node: OutlineNode, indent: int = 0):
            """Recursively render node to text"""
            if node.level == 'root':
                # Skip root, just process children
                for child in node.children:
                    render_node(child, indent)
                return
            
            # Add the outline point
            indent_str = '    ' * indent
            
            if node.level == 'scripture_reading':
                text_parts.append(node.text)
            elif node.number:
                text_parts.append(f'{indent_str}{node.number}. {node.text}')
            else:
                text_parts.append(f'{indent_str}{node.text}')
            
            # Add verses below
            if node.verses:
                for verse in node.verses:
                    if verse.get('text'):
                        text_parts.append(f'{indent_str}    {verse["reference"]}: {verse["text"]}')
                text_parts.append('')  # Blank line after verses
            
            # Process children
            for child in node.children:
                render_node(child, indent + 1)
        
        render_node(root)
        return '\n'.join(text_parts)
    
    def _calculate_stats(self, root: OutlineNode) -> Dict:
        """Calculate statistics about the processing"""
        stats = {
            'total_outline_points': 0,
            'total_verses_detected': 0,
            'total_verses_populated': 0,
            'verses_by_level': {}
        }
        
        def count_node(node: OutlineNode):
            if node.level != 'root':
                stats['total_outline_points'] += 1
                stats['total_verses_detected'] += len(node.verses)
                stats['total_verses_populated'] += len([v for v in node.verses if v.get('text')])
                
                if node.level not in stats['verses_by_level']:
                    stats['verses_by_level'][node.level] = 0
                stats['verses_by_level'][node.level] += len(node.verses)
            
            for child in node.children:
                count_node(child)
        
        count_node(root)
        
        # Calculate population rate
        if stats['total_verses_detected'] > 0:
            stats['population_rate'] = (stats['total_verses_populated'] / stats['total_verses_detected']) * 100
        else:
            stats['population_rate'] = 0
        
        return stats