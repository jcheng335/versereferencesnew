#!/usr/bin/env python3
"""
Margin Format Generator - Creates proper margin-style output like Message_2.pdf
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class MarginFormatter:
    """Formats outline with verses in left margin style"""
    
    def __init__(self):
        self.verse_column_width = 12  # Width for verse references in left margin
        
    def format_html(self, structured_data: Dict, title: str = None) -> str:
        """Generate HTML output with proper margin format"""
        html_parts = []
        
        # HTML header with proper styles
        html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bible Outline with Verses</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            line-height: 1.6;
        }
        h1 { 
            text-align: center; 
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            margin-bottom: 5px;
        }
        .hymns {
            text-align: right;
            font-style: italic;
            margin-bottom: 15px;
        }
        .scripture-reading { 
            font-weight: bold; 
            margin: 20px 0 10px 0;
            text-align: center;
        }
        .outline-point { 
            margin: 10px 0; 
            clear: both;
            min-height: 20px;
        }
        .verse-ref { 
            color: blue; 
            float: left; 
            width: 100px; 
            margin-right: 20px; 
            font-size: 12px;
            clear: left;
        }
        .outline-text { 
            margin-left: 120px;
            display: block;
        }
        .verse-text {
            margin-left: 120px;
            display: block;
            margin-bottom: 5px;
        }
        .roman-numeral {
            font-weight: bold;
            margin-top: 20px;
        }
        .sub-point { 
            margin-left: 20px; 
        }
        .clear { 
            clear: both; 
        }
    </style>
</head>
<body>
""")
        
        # Add title section
        if title:
            html_parts.append(f'<h1>{title}</h1>')
        
        # Process structured data
        if isinstance(structured_data, dict):
            # Extract metadata
            if 'metadata' in structured_data:
                meta = structured_data['metadata']
                if 'message_number' in meta:
                    html_parts.append(f'<h1>{meta["message_number"]}</h1>')
                if 'title' in meta:
                    html_parts.append(f'<div class="subtitle">{meta["title"]}</div>')
                if 'subtitle' in meta:
                    html_parts.append(f'<div class="subtitle">{meta["subtitle"]}</div>')
                if 'hymns' in meta:
                    html_parts.append(f'<div class="hymns">EM Hymns: {meta["hymns"]}</div>')
            
            # Process content based on what's available
            if 'content' in structured_data and structured_data['content']:
                self._process_content(structured_data['content'], html_parts)
            elif 'outline_structure' in structured_data and structured_data['outline_structure']:
                # Convert outline_structure to content format
                self._process_outline_structure(structured_data['outline_structure'], structured_data.get('verses', []), html_parts)
            elif 'structured_data' in structured_data:
                self._process_node(structured_data['structured_data'], html_parts)
            elif 'verses' in structured_data:
                # If only verses available, display them
                for verse in structured_data['verses']:
                    if isinstance(verse, dict) and 'original_text' in verse:
                        self._add_verse_line({'reference': verse['original_text'], 'text': ''}, html_parts)
        
        html_parts.append('</body></html>')
        return '\n'.join(html_parts)
    
    def _process_outline_structure(self, outline_structure: List[Dict], verses: List, html_parts: List[str]):
        """Process outline_structure from pure LLM detector"""
        # Process Scripture Reading first if present
        scripture_reading_found = False
        for item in outline_structure:
            if item.get('type') == 'scripture_reading':
                html_parts.append(f'<div class="scripture-reading">Scripture Reading: {item.get("text", "")}</div>')
                scripture_reading_found = True
                # Add expanded verses for Scripture Reading
                scripture_text = item.get("text", "")
                # Display all verses that are marked as Scripture Reading context
                for verse in verses:
                    if isinstance(verse, dict):
                        # Check context field for Scripture Reading
                        if verse.get('context', '').lower() == 'scripture reading':
                            verse_ref = f"{verse.get('book', '')} {verse.get('chapter', '')}:{verse.get('start_verse', '')}"
                            if verse.get('original_text'):
                                verse_ref = verse.get('original_text')
                            self._add_verse_line({'reference': verse_ref, 'text': ''}, html_parts)
                break
        
        # Process outline items
        for item in outline_structure:
            if item.get('type') in ['outline', 'roman', 'letter', 'number']:
                # Simplified processing for outline items
                number = item.get('number', '')
                text = item.get('text', '')
                
                if item.get('type') == 'roman' or (number and re.match(r'^[IVX]+$', str(number))):
                    html_parts.append(f'<div class="outline-point roman-numeral">')
                    html_parts.append(f'<span class="outline-text">{number}. {text}</span>')
                    html_parts.append('</div>')
                else:
                    html_parts.append(f'<div class="outline-point">')
                    html_parts.append(f'<span class="outline-text">{number}. {text}</span>')
                    html_parts.append('</div>')
                    html_parts.append('<div class="clear"></div>')
    
    def _process_content(self, content: List[Dict], html_parts: List[str]):
        """Process content array with proper formatting"""
        for item in content:
            if item.get('type') == 'scripture_reading':
                html_parts.append(f'<div class="scripture-reading">Scripture Reading: {item.get("text", "")}</div>')
                # Add expanded verses
                if 'verses' in item:
                    for verse in item['verses']:
                        self._add_verse_line(verse, html_parts)
            
            elif item.get('type') == 'outline':
                self._process_outline_item(item, html_parts)
    
    def _process_outline_item(self, item: Dict, html_parts: List[str], indent_level: int = 0):
        """Process an outline item with proper formatting"""
        outline_num = item.get('number', '')
        text = item.get('text', '')
        verses = item.get('verses', [])
        
        # Determine outline level and formatting
        if re.match(r'^[IVX]+$', outline_num):
            # Roman numeral - major section
            html_parts.append(f'<div class="outline-point roman-numeral">')
            html_parts.append(f'<span class="outline-text">{outline_num}. {text}</span>')
            html_parts.append('</div>')
        else:
            # Regular outline point
            indent_class = 'sub-point' if indent_level > 0 else ''
            html_parts.append(f'<div class="outline-point {indent_class}">')
            
            # Add verses in margin if present
            if verses:
                for verse in verses:
                    html_parts.append(f'<span class="verse-ref">{verse.get("reference", "")}</span>')
            
            # Add outline text
            html_parts.append(f'<span class="outline-text">{outline_num}. {text}</span>')
            html_parts.append('</div>')
            html_parts.append('<div class="clear"></div>')
            
            # Add verse texts below if available
            if verses:
                for verse in verses:
                    if verse.get('text'):
                        self._add_verse_text(verse, html_parts)
        
        # Process sub-items
        if 'children' in item:
            for child in item['children']:
                self._process_outline_item(child, html_parts, indent_level + 1)
    
    def _add_verse_line(self, verse: Dict, html_parts: List[str]):
        """Add a single verse line with reference in margin"""
        ref = verse.get('reference', '')
        text = verse.get('text', '')
        
        html_parts.append('<div class="outline-point">')
        html_parts.append(f'<span class="verse-ref">{ref}</span>')
        html_parts.append(f'<span class="verse-text">{text}</span>')
        html_parts.append('</div>')
        html_parts.append('<div class="clear"></div>')
    
    def _add_verse_text(self, verse: Dict, html_parts: List[str]):
        """Add verse text below outline point"""
        text = verse.get('text', '')
        if text:
            html_parts.append(f'<div class="verse-text">{text}</div>')
    
    def _process_node(self, node: Any, html_parts: List[str], indent: int = 0):
        """Process a structured node recursively"""
        if hasattr(node, 'level'):
            if node.level == 'root':
                # Process title/metadata from first children
                for i, child in enumerate(node.children):
                    if i < 3 and child.level == 'title_text':
                        if i == 0:
                            html_parts.append(f'<h1>{child.text}</h1>')
                        else:
                            html_parts.append(f'<div class="subtitle">{child.text}</div>')
                    else:
                        self._process_node(child, html_parts, indent)
            
            elif node.level == 'scripture_reading':
                html_parts.append(f'<div class="scripture-reading">{node.text}</div>')
                # Process verses
                if hasattr(node, 'verses') and node.verses:
                    for verse in node.verses:
                        self._add_verse_line(verse, html_parts)
            
            elif node.level == 'I':  # Roman numeral
                html_parts.append(f'<div class="outline-point roman-numeral">')
                html_parts.append(f'<span class="outline-text">{node.number}. {node.text}</span>')
                html_parts.append('</div>')
                
                # Add verses if present
                if hasattr(node, 'verses') and node.verses:
                    for verse in node.verses:
                        html_parts.append('<div class="outline-point">')
                        html_parts.append(f'<span class="verse-ref">{verse.get("reference", "")}</span>')
                        if verse.get('text'):
                            html_parts.append(f'<span class="outline-text">{verse.get("text", "")}</span>')
                        html_parts.append('</div>')
                        html_parts.append('<div class="clear"></div>')
                
                # Process children
                if hasattr(node, 'children'):
                    for child in node.children:
                        self._process_node(child, html_parts, indent + 1)
            
            else:
                # Regular outline points
                indent_class = 'sub-point' if indent > 0 else ''
                html_parts.append(f'<div class="outline-point {indent_class}">')
                
                # Add verses in margin
                if hasattr(node, 'verses') and node.verses:
                    for verse in node.verses:
                        html_parts.append(f'<span class="verse-ref">{verse.get("reference", "")}</span>')
                
                # Add text
                if hasattr(node, 'number') and node.number:
                    html_parts.append(f'<span class="outline-text">{node.number}. {node.text}</span>')
                else:
                    html_parts.append(f'<span class="outline-text">{node.text}</span>')
                
                html_parts.append('</div>')
                html_parts.append('<div class="clear"></div>')
                
                # Add verse texts
                if hasattr(node, 'verses') and node.verses:
                    for verse in node.verses:
                        if verse.get('text'):
                            html_parts.append(f'<div class="verse-text">{verse.get("text", "")}</div>')
                
                # Process children
                if hasattr(node, 'children'):
                    for child in node.children:
                        self._process_node(child, html_parts, indent + 1)