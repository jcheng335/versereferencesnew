"""
Inline Verse Parser for Bible Outline Verse Populator
Places verses INLINE after each reference, matching MSG12VerseReferences.pdf exactly
"""

import re
from typing import List, Dict, Tuple, Set
from .sqlite_bible_database import SQLiteBibleDatabase

class InlineVerseParser:
    def __init__(self, db_path: str):
        self.db = SQLiteBibleDatabase(db_path)
        
        # Bible book abbreviations mapping
        self.book_abbreviations = {
            # Old Testament
            'Gen': 'Genesis', 'Exo': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deu': 'Deuteronomy',
            'Jos': 'Joshua', 'Jdg': 'Judges', 'Rut': 'Ruth', '1Sa': '1 Samuel', '2Sa': '2 Samuel',
            '1Ki': '1 Kings', '2Ki': '2 Kings', '1Ch': '1 Chronicles', '2Ch': '2 Chronicles',
            'Ezr': 'Ezra', 'Neh': 'Nehemiah', 'Est': 'Esther', 'Job': 'Job', 'Psa': 'Psalms',
            'Pro': 'Proverbs', 'Ecc': 'Ecclesiastes', 'Son': 'Song of Songs', 'Isa': 'Isaiah',
            'Jer': 'Jeremiah', 'Lam': 'Lamentations', 'Eze': 'Ezekiel', 'Dan': 'Daniel',
            'Hos': 'Hosea', 'Joe': 'Joel', 'Amo': 'Amos', 'Oba': 'Obadiah', 'Jon': 'Jonah',
            'Mic': 'Micah', 'Nah': 'Nahum', 'Hab': 'Habakkuk', 'Zep': 'Zephaniah',
            'Hag': 'Haggai', 'Zec': 'Zechariah', 'Mal': 'Malachi',
            
            # New Testament
            'Mat': 'Matthew', 'Mar': 'Mark', 'Luk': 'Luke', 'Joh': 'John', 'Act': 'Acts',
            'Rom': 'Romans', '1Co': '1 Corinthians', '2Co': '2 Corinthians', 'Gal': 'Galatians',
            'Eph': 'Ephesians', 'Phi': 'Philippians', 'Col': 'Colossians', '1Th': '1 Thessalonians',
            '2Th': '2 Thessalonians', '1Ti': '1 Timothy', '2Ti': '2 Timothy', 'Tit': 'Titus',
            'Phm': 'Philemon', 'Heb': 'Hebrews', 'Jam': 'James', '1Pe': '1 Peter', '2Pe': '2 Peter',
            '1Jo': '1 John', '2Jo': '2 John', '3Jo': '3 John', 'Jud': 'Jude', 'Rev': 'Revelation',
            
            # Alternative abbreviations
            'Ps': 'Psalms', 'Psalm': 'Psalms', 'Prov': 'Proverbs', 'Eccl': 'Ecclesiastes',
            'Song': 'Song of Songs', 'Is': 'Isaiah', 'Isa': 'Isaiah', 'Jer': 'Jeremiah',
            'Ezek': 'Ezekiel', 'Dan': 'Daniel', 'Matt': 'Matthew', 'Mk': 'Mark', 'Luke': 'Luke',
            'John': 'John', 'Acts': 'Acts', 'Rom': 'Romans', '1Cor': '1 Corinthians', '2Cor': '2 Corinthians',
            'Gal': 'Galatians', 'Eph': 'Ephesians', 'Phil': 'Philippians', 'Col': 'Colossians',
            '1Thess': '1 Thessalonians', '2Thess': '2 Thessalonians', '1Tim': '1 Timothy',
            '2Tim': '2 Timothy', 'Titus': 'Titus', 'Philem': 'Philemon', 'Heb': 'Hebrews',
            'James': 'James', '1Pet': '1 Peter', '2Pet': '2 Peter', '1John': '1 John',
            '2John': '2 John', '3John': '3 John', 'Jude': 'Jude', 'Rev': 'Revelation'
        }
        
        # Reverse mapping for lookup
        self.book_names_to_abbrev = {v: k for k, v in self.book_abbreviations.items()}
    
    def process_outline_with_inline_verses(self, text: str) -> str:
        """
        Process the outline text and insert verses INLINE after each reference
        matching MSG12VerseReferences.pdf exactly
        """
        lines = text.split('\n')
        output_lines = []
        
        # Track current context for verse resolution
        current_book = None
        current_chapter = None
        
        for line in lines:
            # Add the original line first
            output_lines.append(line)
            
            # Detect verse references in this line
            line_refs = self._detect_references_in_line(line, current_book, current_chapter)
            
            if line_refs:
                # Update context based on what we found
                for ref in line_refs:
                    if ref.get('book') and ref.get('chapter'):
                        current_book = ref['book']
                        current_chapter = ref['chapter']
                
                # Get unique verses for this line
                unique_verses = self._get_unique_verses_for_line(line_refs)
                
                # Insert verses immediately after this line
                if unique_verses:
                    output_lines.append("")  # Empty line before verses
                    
                    for verse in unique_verses:
                        # Format: "Eph 4:20    But you did not so learn Christ,"
                        verse_ref = f"{self._get_book_abbreviation(verse['book'])} {verse['chapter']}:{verse['verse']}"
                        verse_text = verse['text']
                        
                        # Add verse reference and text (will be styled blue in frontend)
                        output_lines.append(f"<span class='verse-ref'>{verse_ref}</span>")
                        output_lines.append(f"<span class='verse-text'>{verse_text}</span>")
                    
                    output_lines.append("")  # Empty line after verses
        
        return '\n'.join(output_lines)
    
    def _detect_references_in_line(self, line: str, context_book: str = None, context_chapter: int = None) -> List[Dict]:
        """
        Detect verse references in a single line with context
        """
        references = []
        
        # Pattern 1: Full references with book name
        # Examples: "Eph. 4:7-16", "1 Cor. 12:14-22", "cf. 2 Cor. 1:15"
        full_pattern = r'(?:cf\.\s+)?([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?(?:;\s*(\d+):(\d+)(?:-(\d+))?)*'
        
        for match in re.finditer(full_pattern, line, re.IGNORECASE):
            book_text = match.group(1)
            book_name = self._normalize_book_name(book_text)
            chapter = int(match.group(2))
            start_verse = int(match.group(3))
            end_verse = int(match.group(4)) if match.group(4) else start_verse
            
            # Add verses in range
            for verse_num in range(start_verse, end_verse + 1):
                references.append({
                    'book': book_name,
                    'chapter': chapter,
                    'verse': verse_num,
                    'original_text': match.group(0),
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
            
            # Handle additional chapter:verse pairs in the same match
            if match.group(5) and match.group(6):
                chapter2 = int(match.group(5))
                start_verse2 = int(match.group(6))
                end_verse2 = int(match.group(7)) if match.group(7) else start_verse2
                
                for verse_num in range(start_verse2, end_verse2 + 1):
                    references.append({
                        'book': book_name,
                        'chapter': chapter2,
                        'verse': verse_num,
                        'original_text': match.group(0),
                        'start_pos': match.start(),
                        'end_pos': match.end()
                    })
        
        # Pattern 2: Verse-only references (v. X, vv. X-Y)
        # These need context resolution
        verse_only_pattern = r'vv?\.\s*(\d+)(?:-(\d+))?'
        
        for match in re.finditer(verse_only_pattern, line, re.IGNORECASE):
            if context_book and context_chapter:
                start_verse = int(match.group(1))
                end_verse = int(match.group(2)) if match.group(2) else start_verse
                
                for verse_num in range(start_verse, end_verse + 1):
                    references.append({
                        'book': context_book,
                        'chapter': context_chapter,
                        'verse': verse_num,
                        'original_text': match.group(0),
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'context_resolved': True
                    })
        
        # Pattern 3: Chapter:verse only (when book is in context)
        # Examples: "12:14-22" when we know we're in 1 Corinthians
        chapter_verse_pattern = r'(?<![A-Za-z])(\d+):(\d+)(?:-(\d+))?(?![A-Za-z])'
        
        for match in re.finditer(chapter_verse_pattern, line):
            # Only use this if we don't already have a full reference covering this position
            pos = match.start()
            covered = any(ref['start_pos'] <= pos <= ref['end_pos'] for ref in references)
            
            if not covered and context_book:
                chapter = int(match.group(1))
                start_verse = int(match.group(2))
                end_verse = int(match.group(3)) if match.group(3) else start_verse
                
                for verse_num in range(start_verse, end_verse + 1):
                    references.append({
                        'book': context_book,
                        'chapter': chapter,
                        'verse': verse_num,
                        'original_text': match.group(0),
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'context_resolved': True
                    })
        
        return references
    
    def _get_unique_verses_for_line(self, references: List[Dict]) -> List[Dict]:
        """
        Get unique verses for a line with their text content
        """
        unique_verses = []
        seen_refs = set()
        
        for ref in references:
            verse_key = (ref['book'], ref['chapter'], ref['verse'])
            if verse_key not in seen_refs:
                verse_text = self.get_verse_text(ref['book'], ref['chapter'], ref['verse'])
                if verse_text:
                    unique_verses.append({
                        'book': ref['book'],
                        'chapter': ref['chapter'],
                        'verse': ref['verse'],
                        'text': verse_text,
                        'sort_key': verse_key
                    })
                    seen_refs.add(verse_key)
        
        # Sort verses by biblical order (book, chapter, verse)
        unique_verses.sort(key=lambda x: x['sort_key'])
        
        return unique_verses
    
    def _normalize_book_name(self, book_text: str) -> str:
        """
        Normalize book name to standard format
        """
        # Remove periods and extra spaces
        book_clean = book_text.replace('.', '').strip()
        
        # Handle numbered books
        if book_clean.startswith('1 '):
            book_clean = '1' + book_clean[2:]
        elif book_clean.startswith('2 '):
            book_clean = '2' + book_clean[2:]
        elif book_clean.startswith('3 '):
            book_clean = '3' + book_clean[2:]
        
        # Look up in abbreviations
        if book_clean in self.book_abbreviations:
            return self.book_abbreviations[book_clean]
        
        # Try case-insensitive lookup
        for abbrev, full_name in self.book_abbreviations.items():
            if abbrev.lower() == book_clean.lower():
                return full_name
            if full_name.lower() == book_clean.lower():
                return full_name
        
        return book_clean
    
    def get_verse_text(self, book: str, chapter: int, verse: int) -> str:
        """
        Get the text for a specific verse
        """
        verse_data = self.db.lookup_verse(book, chapter, verse)
        if verse_data and 'text' in verse_data:
            return verse_data['text']
        return ""
    
    def _get_book_abbreviation(self, book_name: str) -> str:
        """
        Get the abbreviation for a book name
        """
        if book_name in self.book_names_to_abbrev:
            return self.book_names_to_abbrev[book_name]
        
        # Try to find a match
        for abbrev, full_name in self.book_abbreviations.items():
            if full_name.lower() == book_name.lower():
                return abbrev
        
        return book_name  # Return as-is if not found
    
    def get_detection_stats(self, text: str) -> Dict:
        """
        Get statistics about verse detection for debugging
        """
        lines = text.split('\n')
        all_references = []
        
        current_book = None
        current_chapter = None
        
        for line in lines:
            line_refs = self._detect_references_in_line(line, current_book, current_chapter)
            
            # Update context
            for ref in line_refs:
                if ref.get('book') and ref.get('chapter'):
                    current_book = ref['book']
                    current_chapter = ref['chapter']
            
            all_references.extend(line_refs)
        
        # Deduplicate for stats
        unique_verses = set((ref['book'], ref['chapter'], ref['verse']) for ref in all_references)
        
        stats = {
            'total_references': len(all_references),
            'unique_verses': len(unique_verses),
            'context_resolved': len([ref for ref in all_references if ref.get('context_resolved')]),
            'books_detected': len(set(ref['book'] for ref in all_references)),
            'references_by_book': {}
        }
        
        # Count references by book
        for ref in all_references:
            book = ref['book']
            if book not in stats['references_by_book']:
                stats['references_by_book'][book] = 0
            stats['references_by_book'][book] += 1
        
        return stats

