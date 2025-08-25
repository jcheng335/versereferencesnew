"""
Smart Verse Parser - Preserves formatting and text flow
Inserts verses only at appropriate break points while maintaining original structure
"""

import re
import os
import sys
from typing import List, Dict, Tuple, Optional

# Add the src directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.sqlite_bible_database import SQLiteBibleDatabase

class SmartVerseParser:
    def __init__(self, db_path: str):
        self.db = SQLiteBibleDatabase(db_path)
        
        # Book abbreviation mapping
        self.book_abbreviations = {
            'Gen': 'Genesis', 'Exo': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deut': 'Deuteronomy',
            'Josh': 'Joshua', 'Judg': 'Judges', 'Ruth': 'Ruth', '1 Sam': '1 Samuel', '2 Sam': '2 Samuel',
            '1 Kings': '1 Kings', '2 Kings': '2 Kings', '1 Chron': '1 Chronicles', '2 Chron': '2 Chronicles',
            'Ezra': 'Ezra', 'Neh': 'Nehemiah', 'Esth': 'Esther', 'Job': 'Job', 'Psa': 'Psalms',
            'Prov': 'Proverbs', 'Eccl': 'Ecclesiastes', 'S.S.': 'Song of Songs', 'Isa': 'Isaiah',
            'Jer': 'Jeremiah', 'Lam': 'Lamentations', 'Ezek': 'Ezekiel', 'Dan': 'Daniel',
            'Hosea': 'Hosea', 'Joel': 'Joel', 'Amos': 'Amos', 'Obad': 'Obadiah', 'Jonah': 'Jonah',
            'Micah': 'Micah', 'Nahum': 'Nahum', 'Hab': 'Habakkuk', 'Zeph': 'Zephaniah', 'Hag': 'Haggai',
            'Zech': 'Zechariah', 'Mal': 'Malachi',
            'Matt': 'Matthew', 'Mark': 'Mark', 'Luke': 'Luke', 'John': 'John', 'Acts': 'Acts',
            'Rom': 'Romans', '1 Cor': '1 Corinthians', '2 Cor': '2 Corinthians', 'Gal': 'Galatians',
            'Eph': 'Ephesians', 'Phil': 'Philippians', 'Col': 'Colossians', '1 Thes': '1 Thessalonians',
            '2 Thes': '2 Thessalonians', '1 Tim': '1 Timothy', '2 Tim': '2 Timothy', 'Titus': 'Titus',
            'Philem': 'Philemon', 'Heb': 'Hebrews', 'James': 'James', '1 Pet': '1 Peter', '2 Pet': '2 Peter',
            '1 John': '1 John', '2 John': '2 John', '3 John': '3 John', 'Jude': 'Jude', 'Rev': 'Revelation'
        }
        
        # Patterns for different types of verse references
        self.reference_patterns = [
            # Full references with optional "cf." prefix
            r'(?:cf\.\s+)?([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?(?:\s*[,;]\s*(\d+):(\d+)(?:-(\d+))?)*',
            # Verse-only references (v. or vv.)
            r'v{1,2}\.\s*(\d+)(?:-(\d+))?',
            # Chapter:verse ranges within same book
            r'(\d+):(\d+)-(\d+)',
        ]
    
    def find_verse_references(self, text: str) -> List[Dict]:
        """
        Find all verse references in text with their positions and context
        """
        references = []
        
        # Split text into logical segments (sentences, clauses)
        segments = self._split_into_segments(text)
        
        for segment_idx, segment in enumerate(segments):
            segment_refs = self._find_references_in_segment(segment, segment_idx)
            references.extend(segment_refs)
        
        return references
    
    def _split_into_segments(self, text: str) -> List[Dict]:
        """
        Split text into logical segments while preserving formatting
        """
        segments = []
        
        # Split by lines first to preserve structure
        lines = text.split('\n')
        
        for line_idx, line in enumerate(lines):
            if not line.strip():
                segments.append({
                    'text': line,
                    'type': 'empty_line',
                    'line_idx': line_idx,
                    'formatting': self._detect_formatting(line)
                })
                continue
            
            # Detect if this is a heading, outline point, or regular text
            line_type = self._detect_line_type(line)
            
            # For outline points and headings, treat as single segment
            if line_type in ['heading', 'outline_point']:
                segments.append({
                    'text': line,
                    'type': line_type,
                    'line_idx': line_idx,
                    'formatting': self._detect_formatting(line)
                })
            else:
                # For regular text, split by sentences but keep on same line
                sentences = self._split_sentences(line)
                for sent_idx, sentence in enumerate(sentences):
                    segments.append({
                        'text': sentence,
                        'type': 'sentence',
                        'line_idx': line_idx,
                        'sentence_idx': sent_idx,
                        'formatting': self._detect_formatting(line)
                    })
        
        return segments
    
    def _detect_line_type(self, line: str) -> str:
        """
        Detect the type of line (heading, outline point, regular text)
        """
        stripped = line.strip()
        
        # Roman numerals (I., II., III., etc.)
        if re.match(r'^[IVX]+\.\s+', stripped):
            return 'outline_point'
        
        # Capital letters (A., B., C., etc.)
        if re.match(r'^[A-Z]\.\s+', stripped):
            return 'outline_point'
        
        # Numbers (1., 2., 3., etc.)
        if re.match(r'^\d+\.\s+', stripped):
            return 'outline_point'
        
        # Lowercase letters (a., b., c., etc.)
        if re.match(r'^[a-z]\.\s+', stripped):
            return 'outline_point'
        
        # Headings (all caps, or title case without periods)
        if stripped.isupper() or (not stripped.endswith('.') and len(stripped.split()) <= 8):
            return 'heading'
        
        return 'regular_text'
    
    def _detect_formatting(self, line: str) -> Dict:
        """
        Detect formatting in the line (bold, italic, etc.)
        """
        formatting = {
            'bold': False,
            'italic': False,
            'size': 'normal'
        }
        
        # Detect Roman numerals (should be bold and larger)
        if re.match(r'^\s*[IVX]+\.\s+', line.strip()):
            formatting['bold'] = True
            formatting['size'] = 'large'
        
        # Detect italicized text (usually book titles or emphasis)
        if re.search(r'["""].*?["""]', line) or 'cf.' in line:
            formatting['italic'] = True
        
        return formatting
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while being careful about abbreviations
        """
        # Simple sentence splitting that's aware of common abbreviations
        sentences = []
        current = ""
        
        i = 0
        while i < len(text):
            char = text[i]
            current += char
            
            if char in '.!?':
                # Look ahead to see if this is end of sentence
                if i + 1 < len(text):
                    next_char = text[i + 1]
                    # If followed by space and capital letter, likely end of sentence
                    if next_char == ' ' and i + 2 < len(text) and text[i + 2].isupper():
                        # But check for common abbreviations
                        if not self._is_abbreviation(current.strip()):
                            sentences.append(current.strip())
                            current = ""
                else:
                    # End of text
                    sentences.append(current.strip())
                    current = ""
            
            i += 1
        
        if current.strip():
            sentences.append(current.strip())
        
        return [s for s in sentences if s]
    
    def _is_abbreviation(self, text: str) -> bool:
        """
        Check if text ends with a common abbreviation
        """
        abbrevs = ['cf.', 'v.', 'vv.', 'vs.', 'ch.', 'chap.', 'etc.', 'i.e.', 'e.g.']
        return any(text.lower().endswith(abbrev) for abbrev in abbrevs)
    
    def _find_references_in_segment(self, segment: Dict, segment_idx: int) -> List[Dict]:
        """
        Find verse references within a specific segment
        """
        references = []
        text = segment['text']
        
        # Find all reference patterns
        for pattern in self.reference_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                ref_info = self._parse_reference_match(match, segment, segment_idx)
                if ref_info:
                    references.append(ref_info)
        
        return references
    
    def _parse_reference_match(self, match: re.Match, segment: Dict, segment_idx: int) -> Optional[Dict]:
        """
        Parse a regex match into reference information
        """
        groups = match.groups()
        
        # Handle different pattern types
        if len(groups) >= 3 and groups[0] and groups[1] and groups[2]:
            # Full reference pattern
            book_abbrev = groups[0].strip().replace('.', '')
            book_name = self.book_abbreviations.get(book_abbrev, book_abbrev)
            chapter = int(groups[1])
            start_verse = int(groups[2])
            end_verse = int(groups[3]) if groups[3] else start_verse
            
            return {
                'type': 'full_reference',
                'book': book_name,
                'chapter': chapter,
                'start_verse': start_verse,
                'end_verse': end_verse,
                'original_text': match.group(0),
                'position': match.span(),
                'segment_idx': segment_idx,
                'segment': segment,
                'insert_after_segment': True  # Insert after complete segment
            }
        
        elif len(groups) >= 1 and groups[0]:
            # Verse-only reference (needs context)
            start_verse = int(groups[0])
            end_verse = int(groups[1]) if len(groups) > 1 and groups[1] else start_verse
            
            return {
                'type': 'verse_only',
                'start_verse': start_verse,
                'end_verse': end_verse,
                'original_text': match.group(0),
                'position': match.span(),
                'segment_idx': segment_idx,
                'segment': segment,
                'needs_context': True,
                'insert_after_segment': True
            }
        
        return None
    
    def resolve_context_references(self, references: List[Dict], text: str) -> List[Dict]:
        """
        Resolve verse-only references using context from nearby full references
        """
        resolved = []
        current_book = None
        current_chapter = None
        
        for ref in references:
            if ref['type'] == 'full_reference':
                current_book = ref['book']
                current_chapter = ref['chapter']
                resolved.append(ref)
            
            elif ref['type'] == 'verse_only' and current_book and current_chapter:
                # Resolve using current context
                resolved_ref = ref.copy()
                resolved_ref.update({
                    'type': 'resolved_reference',
                    'book': current_book,
                    'chapter': current_chapter
                })
                resolved.append(resolved_ref)
            
            else:
                # Keep unresolved references for now
                resolved.append(ref)
        
        return resolved
    
    def insert_verses_smartly(self, text: str, references: List[Dict]) -> str:
        """
        Insert verses at appropriate points while preserving formatting and flow
        """
        # Split text into segments
        segments = self._split_into_segments(text)
        
        # Group references by segment
        refs_by_segment = {}
        for ref in references:
            segment_idx = ref['segment_idx']
            if segment_idx not in refs_by_segment:
                refs_by_segment[segment_idx] = []
            refs_by_segment[segment_idx].append(ref)
        
        # Build output with verses inserted at segment boundaries
        output_lines = []
        
        for i, segment in enumerate(segments):
            # Add the original segment
            output_lines.append(segment['text'])
            
            # Check if we should insert verses after this segment
            if i in refs_by_segment and segment['type'] in ['outline_point', 'sentence']:
                # Insert verses after this segment
                verse_lines = self._format_verses_for_segment(refs_by_segment[i], segment)
                output_lines.extend(verse_lines)
        
        return '\n'.join(output_lines)
    
    def _format_verses_for_segment(self, references: List[Dict], segment: Dict) -> List[str]:
        """
        Format verses for insertion after a segment
        """
        verse_lines = []
        
        # Add empty line before verses
        verse_lines.append("")
        
        for ref in references:
            if 'book' in ref and 'chapter' in ref:
                # Get verses for this reference
                for verse_num in range(ref['start_verse'], ref['end_verse'] + 1):
                    verse_data = self.db.lookup_verse(ref['book'], ref['chapter'], verse_num)
                    if verse_data and 'text' in verse_data:
                        # Format reference
                        book_abbrev = self._get_book_abbreviation(ref['book'])
                        ref_line = f"<span class='verse-ref'>{book_abbrev} {ref['chapter']}:{verse_num}</span>"
                        verse_text = f"<span class='verse-text'>{verse_data['text']}</span>"
                        
                        verse_lines.append(ref_line)
                        verse_lines.append(verse_text)
        
        # Add empty line after verses
        verse_lines.append("")
        
        return verse_lines
    
    def _get_book_abbreviation(self, book_name: str) -> str:
        """
        Get standard abbreviation for book name
        """
        abbrev_map = {v: k for k, v in self.book_abbreviations.items()}
        return abbrev_map.get(book_name, book_name)

