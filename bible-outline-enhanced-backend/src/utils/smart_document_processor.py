"""
Smart Document Processor - Preserves formatting and structure
Uses intelligent verse insertion that maintains text flow and original formatting
"""

import os
import uuid
import fitz  # PyMuPDF
from docx import Document
from typing import Dict, List, Optional, Any
import sys
import re

# Add the src directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.smart_verse_parser import SmartVerseParser

class SmartDocumentProcessor:
    def __init__(self, db_path: str):
        self.verse_parser = SmartVerseParser(db_path)
        self.sessions = {}
    
    def upload_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Upload and process a document, preserving original formatting
        """
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                content = self._extract_pdf_with_formatting(file_path)
            elif filename.lower().endswith(('.docx', '.doc')):
                content = self._extract_docx_with_formatting(file_path)
            else:
                # Plain text
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Find verse references
            references = self.verse_parser.find_verse_references(content)
            resolved_references = self.verse_parser.resolve_context_references(references, content)
            
            # Store session data
            self.sessions[session_id] = {
                'original_content': content,
                'original_filename': filename,
                'references': resolved_references,
                'populated_content': None,
                'stats': self._calculate_stats(resolved_references)
            }
            
            return {
                'success': True,
                'session_id': session_id,
                'content': content,
                'references_found': len(resolved_references),
                'total_verses': sum((ref.get('end_verse') or ref.get('start_verse', 0)) - ref.get('start_verse', 0) + 1 
                                  for ref in resolved_references 
                                  if 'book' in ref and 'chapter' in ref),
                'filename': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing document: {str(e)}'
            }
    
    def _extract_pdf_with_formatting(self, file_path: str) -> str:
        """
        Extract text from PDF while preserving basic formatting cues
        """
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                # Get text with formatting information
                blocks = page.get_text("dict")
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                span_text = span["text"]
                                font_size = span["size"]
                                font_flags = span["flags"]
                                
                                # Detect formatting based on font properties
                                is_bold = font_flags & 2**4  # Bold flag
                                is_italic = font_flags & 2**1  # Italic flag
                                
                                # Add formatting markers for preservation
                                if is_bold and font_size > 12:
                                    span_text = f"**{span_text}**"  # Mark as bold heading
                                elif is_italic:
                                    span_text = f"*{span_text}*"  # Mark as italic
                                
                                line_text += span_text
                            
                            if line_text.strip():
                                text += line_text + "\n"
                        text += "\n"  # Add line break between blocks
            
            doc.close()
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
        
        return self._clean_extracted_text(text)
    
    def _extract_docx_with_formatting(self, file_path: str) -> str:
        """
        Extract text from DOCX while preserving formatting
        """
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                para_text = ""
                
                for run in paragraph.runs:
                    run_text = run.text
                    
                    # Preserve formatting
                    if run.bold:
                        run_text = f"**{run_text}**"
                    if run.italic:
                        run_text = f"*{run_text}*"
                    
                    para_text += run_text
                
                if para_text.strip():
                    text += para_text + "\n"
            
            return self._clean_extracted_text(text)
            
        except Exception as e:
            raise Exception(f"Error extracting DOCX text: {str(e)}")
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean extracted text while preserving important formatting
        """
        # Remove excessive whitespace but preserve structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive spaces within lines
            cleaned_line = re.sub(r' +', ' ', line.strip())
            cleaned_lines.append(cleaned_line)
        
        # Remove excessive empty lines but preserve paragraph breaks
        result_lines = []
        empty_count = 0
        
        for line in cleaned_lines:
            if not line:
                empty_count += 1
                if empty_count <= 2:  # Allow max 2 consecutive empty lines
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def process_document(self, session_id: str, format_type: str = 'inline') -> Dict[str, Any]:
        """
        Process document with smart verse insertion
        """
        if session_id not in self.sessions:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        try:
            session_data = self.sessions[session_id]
            original_content = session_data['original_content']
            references = session_data['references']
            
            # Use smart verse insertion
            populated_content = self.verse_parser.insert_verses_smartly(original_content, references)
            
            # Convert formatting markers to HTML for display
            populated_content = self._convert_formatting_to_html(populated_content)
            
            # Update session
            session_data['populated_content'] = populated_content
            
            # Calculate statistics
            total_verses = sum((ref.get('end_verse') or ref.get('start_verse', 0)) - ref.get('start_verse', 0) + 1 
                             for ref in references 
                             if 'book' in ref and 'chapter' in ref)
            
            context_resolved = sum(1 for ref in references if ref.get('type') == 'resolved_reference')
            
            return {
                'success': True,
                'populated_content': populated_content,
                'verse_count': total_verses,
                'context_resolved': context_resolved,
                'format': format_type,
                'message': f'Successfully populated {total_verses} unique verses inline (with {context_resolved} context-resolved references)',
                'stats': session_data['stats']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error populating verses: {str(e)}'
            }
    
    def _convert_formatting_to_html(self, text: str) -> str:
        """
        Convert formatting markers to HTML while preserving structure
        """
        # Convert bold markers to HTML
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Convert italic markers to HTML
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Detect and format Roman numerals
        text = re.sub(r'^(\s*[IVX]+\.\s+)', r'<strong class="roman-numeral">\1</strong>', text, flags=re.MULTILINE)
        
        # Detect and format outline points
        text = re.sub(r'^(\s*[A-Z]\.\s+)', r'<strong class="outline-point">\1</strong>', text, flags=re.MULTILINE)
        text = re.sub(r'^(\s*\d+\.\s+)', r'<strong class="numbered-point">\1</strong>', text, flags=re.MULTILINE)
        
        return text
    
    def _calculate_stats(self, references: List[Dict]) -> Dict:
        """
        Calculate statistics about found references
        """
        stats = {
            'total_references': len(references),
            'full_references': 0,
            'verse_only_references': 0,
            'resolved_references': 0,
            'references_by_book': {},
            'context_resolved': 0
        }
        
        for ref in references:
            if ref['type'] == 'full_reference':
                stats['full_references'] += 1
            elif ref['type'] == 'verse_only':
                stats['verse_only_references'] += 1
            elif ref['type'] == 'resolved_reference':
                stats['resolved_references'] += 1
                stats['context_resolved'] += 1
            
            if 'book' in ref:
                book = ref['book']
                if book not in stats['references_by_book']:
                    stats['references_by_book'][book] = 0
                stats['references_by_book'][book] += (ref.get('end_verse') or ref.get('start_verse', 0)) - ref.get('start_verse', 0) + 1
        
        return stats
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """
        Get session data
        """
        return self.sessions.get(session_id)
    
    def export_clean_text(self, session_id: str) -> Optional[str]:
        """
        Export clean text without HTML tags for OneNote
        """
        if session_id not in self.sessions:
            return None
        
        populated_content = self.sessions[session_id].get('populated_content')
        if not populated_content:
            return None
        
        # Remove HTML tags but keep content
        clean_text = populated_content
        
        # Remove verse span tags but keep content
        clean_text = re.sub(r'<span class=[\'"]verse-ref[\'"]>(.*?)</span>', r'\1', clean_text)
        clean_text = re.sub(r'<span class=[\'"]verse-text[\'"]>(.*?)</span>', r'\1', clean_text)
        
        # Remove other HTML tags but keep content
        clean_text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\1', clean_text)
        clean_text = re.sub(r'<em>(.*?)</em>', r'\1', clean_text)
        clean_text = re.sub(r'<[^>]*>', '', clean_text)
        
        # Clean up whitespace
        clean_text = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_text)
        
        return clean_text.strip()

