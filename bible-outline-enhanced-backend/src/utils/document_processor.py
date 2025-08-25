import sqlite3
import re
from typing import List, Dict, Tuple
import os

class DocumentProcessor:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'bible_verses.db')
    
    def extract_verse_references(self, text: str) -> List[str]:
        """Extract ALL Bible verse references from text, including complex patterns"""
        if not text:
            return []
        
        references = set()
        
        # Split into lines for better processing
        lines = text.split('\n')
        
        for line in lines:
            # Pattern 1: Standard references (Eph. 4:7-16, 1 Cor. 12:14-22, etc.)
            pattern1 = r'\b([A-Za-z0-9]+\.?\s*\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*(?:;\s*\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)*)\b'
            matches1 = re.findall(pattern1, line)
            references.update(matches1)
            
            # Pattern 2: Cross-book references (Rom. 12:4-5; 1 Cor. 12:14-22)
            pattern2 = r'\b([A-Za-z0-9]+\.?\s*\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*(?:;\s*[A-Za-z0-9]+\.?\s*\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)*)\b'
            matches2 = re.findall(pattern2, line)
            references.update(matches2)
            
            # Pattern 3: References with "v." (v. 7; 1 Cor. 12:14-22)
            pattern3 = r'v\.\s*(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)'
            matches3 = re.findall(pattern3, line)
            for match in matches3:
                references.add(f"v. {match}")
            
            # Pattern 4: References with "cf." (cf. 2 Cor. 1:15)
            pattern4 = r'cf\.\s+([A-Za-z0-9]+\.?\s*\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)'
            matches4 = re.findall(pattern4, line)
            references.update(matches4)
            
            # Pattern 5: References in parentheses
            pattern5 = r'\(([^)]*[A-Za-z0-9]+\.?\s*\d+:\d+[^)]*)\)'
            matches5 = re.findall(pattern5, line)
            for match in matches5:
                inner_refs = self.extract_verse_references(match)
                references.update(inner_refs)
            
            # Pattern 6: References after dashes (—Eph. 4:8-12)
            pattern6 = r'[—\-]\s*([A-Za-z0-9]+\.?\s*\d+:\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)'
            matches6 = re.findall(pattern6, line)
            references.update(matches6)
            
            # Pattern 7: Line break references (John\n1:12-13)
            pattern7 = r'([A-Za-z0-9]+)\s*\n\s*(\d+:\d+(?:-\d+)?)'
            matches7 = re.findall(pattern7, line)
            for book, verse in matches7:
                references.add(f"{book} {verse}")
        
        # Clean and validate references
        cleaned_refs = []
        for ref in references:
            cleaned_ref = self._clean_reference(ref)
            if cleaned_ref and self._is_valid_reference(cleaned_ref):
                cleaned_refs.append(cleaned_ref)
        
        return sorted(list(set(cleaned_refs)))
    
    def _clean_reference(self, ref: str) -> str:
        """Clean and normalize a reference"""
        if not ref:
            return ""
        
        # Remove extra whitespace
        ref = re.sub(r'\s+', ' ', ref.strip())
        
        # Remove leading/trailing punctuation except periods in abbreviations
        ref = ref.strip(',;:')
        
        # Handle line breaks
        ref = ref.replace('\n', ' ')
        ref = re.sub(r'\s+', ' ', ref)
        
        return ref
    
    def _is_valid_reference(self, ref: str) -> bool:
        """Check if a reference is valid"""
        if not ref:
            return False
        
        # Skip "v." references for now (need context)
        if ref.startswith('v.'):
            return False
        
        # Must contain at least one colon (for chapter:verse)
        if ':' not in ref:
            return False
        
        # Must have some alphabetic characters (book name)
        if not re.search(r'[A-Za-z]', ref):
            return False
        
        return True
    
    def lookup_verses(self, references: List[str]) -> List[Dict]:
        """Look up verses from the database"""
        if not references:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_verses = []
        
        for ref in references:
            verses = self._lookup_single_reference(cursor, ref)
            all_verses.extend(verses)
        
        conn.close()
        return all_verses
    
    def _lookup_single_reference(self, cursor, ref: str) -> List[Dict]:
        """Look up a single reference"""
        verses = []
        
        # Parse the reference
        parsed_refs = self._parse_reference(ref)
        
        for book_name, chapter, verse_start, verse_end in parsed_refs:
            # Find book ID
            cursor.execute('''
                SELECT b.id, b.name FROM books b 
                LEFT JOIN book_abbreviations ba ON b.id = ba.book_id 
                WHERE LOWER(b.name) = LOWER(?) OR LOWER(ba.abbreviation) = LOWER(?)
            ''', (book_name, book_name))
            
            book_result = cursor.fetchone()
            if not book_result:
                continue
            
            book_id, full_book_name = book_result
            
            # Get verses
            if verse_end:
                cursor.execute('''
                    SELECT chapter, verse, text FROM verses 
                    WHERE book_id = ? AND chapter = ? AND verse BETWEEN ? AND ?
                    ORDER BY verse
                ''', (book_id, chapter, verse_start, verse_end))
            else:
                cursor.execute('''
                    SELECT chapter, verse, text FROM verses 
                    WHERE book_id = ? AND chapter = ? AND verse = ?
                ''', (book_id, chapter, verse_start))
            
            verse_results = cursor.fetchall()
            
            for v_chapter, v_verse, v_text in verse_results:
                verses.append({
                    'reference': f"{full_book_name} {v_chapter}:{v_verse}",
                    'book': full_book_name,
                    'chapter': v_chapter,
                    'verse': v_verse,
                    'text': v_text,
                    'original_reference': ref
                })
        
        return verses
    
    def _parse_reference(self, ref: str) -> List[Tuple[str, int, int, int]]:
        """Parse a reference into components"""
        results = []
        
        # Handle complex references like "Eph. 4:7-16; 6:10-20"
        parts = ref.split(';')
        
        current_book = None
        
        for part in parts:
            part = part.strip()
            
            # Check if this part has a book name
            book_match = re.match(r'^([A-Za-z0-9]+\.?)\s+(.+)', part)
            if book_match:
                current_book = book_match.group(1).rstrip('.')
                verse_part = book_match.group(2)
            else:
                # No book name, use current book
                verse_part = part
            
            if not current_book:
                continue
            
            # Parse verse part (e.g., "4:7-16", "1:5,9", "6:10-20")
            chapter_verse_matches = re.findall(r'(\d+):(\d+)(?:-(\d+))?', verse_part)
            
            for match in chapter_verse_matches:
                chapter = int(match[0])
                verse_start = int(match[1])
                verse_end = int(match[2]) if match[2] else None
                
                results.append((current_book, chapter, verse_start, verse_end))
        
        return results
    
    def process_document_text(self, text: str) -> Dict:
        """Process document text and return with verse references"""
        references = self.extract_verse_references(text)
        verses = self.lookup_verses(references)
        
        return {
            'original_text': text,
            'references_found': references,
            'verses': verses,
            'populated_text': self.populate_text_with_verses(text, verses, format_type='integrated')
        }
    
    def populate_text_with_verses(self, text: str, verses: List[Dict], format_type: str = 'integrated') -> str:
        """Populate text with verse content in the target style"""
        
        if format_type == 'integrated':
            # Format like the completed outline with verses integrated
            return self._format_integrated_style(text, verses)
        else:
            # Format with verses at bottom
            return self._format_bottom_style(text, verses)
    
    def _format_integrated_style(self, text: str, verses: List[Dict]) -> str:
        """Format in the integrated style like the completed outline"""
        
        # Create verse mapping by original reference
        verse_map = {}
        for verse in verses:
            original_ref = verse.get('original_reference', verse['reference'])
            if original_ref not in verse_map:
                verse_map[original_ref] = []
            verse_map[original_ref].append(verse)
        
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            formatted_lines.append(line)
            
            # Check if this line contains verse references
            line_refs = self.extract_verse_references(line)
            
            for ref in line_refs:
                if ref in verse_map:
                    # Add the verse reference and text in blue format
                    for verse in verse_map[ref]:
                        formatted_lines.append(f"<span style='color: blue'>{verse['reference']}</span>")
                        formatted_lines.append(f"<span style='color: blue'>{verse['text']}</span>")
        
        return '\n'.join(formatted_lines)
    
    def _format_bottom_style(self, text: str, verses: List[Dict]) -> str:
        """Format with verses listed at the bottom"""
        
        formatted_text = text + "\n\n--- Bible Verses ---\n\n"
        
        # Group verses by original reference
        verse_groups = {}
        for verse in verses:
            original_ref = verse.get('original_reference', verse['reference'])
            if original_ref not in verse_groups:
                verse_groups[original_ref] = []
            verse_groups[original_ref].append(verse)
        
        for ref, verse_list in verse_groups.items():
            formatted_text += f"{ref}:\n"
            for verse in verse_list:
                formatted_text += f"  {verse['reference']}: {verse['text']}\n"
            formatted_text += "\n"
        
        return formatted_text


    
    def process_uploaded_file(self, file_path: str, filename: str, text_content: str = None) -> Dict:
        """Process uploaded file and extract text"""
        
        if text_content:
            # Use provided text content (e.g., from OCR)
            text = text_content
        else:
            # Extract text from file
            text = self._extract_text_from_file(file_path, filename)
        
        # Process the text
        result = self.process_document_text(text)
        
        # Add session management
        import uuid
        session_id = str(uuid.uuid4())
        
        result['session_id'] = session_id
        result['filename'] = filename
        result['success'] = True
        
        return result
    
    def _extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text from uploaded file"""
        
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return self._extract_pdf_text(file_path)
        elif file_ext in ['doc', 'docx']:
            return self._extract_word_text(file_path)
        else:
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def _extract_word_text(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting Word text: {e}")
            return ""

