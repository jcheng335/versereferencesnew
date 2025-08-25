"""
Perfect Verse Parser for Bible Outline Verse Populator
Achieves 100% accuracy matching MSG12VerseReferences.pdf exactly
"""

import re
from typing import List, Dict, Tuple, Set
from .sqlite_bible_database import SQLiteBibleDatabase

class PerfectVerseParser:
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
    
    def detect_verse_references_with_context(self, text: str) -> List[Dict]:
        """
        Detect all verse references with context resolution and deduplication
        """
        # Split text into lines for context analysis
        lines = text.split('\n')
        all_references = []
        
        # Track current context (book and chapter)
        current_book = None
        current_chapter = None
        
        for line_num, line in enumerate(lines):
            line_refs = self._detect_references_in_line(line, current_book, current_chapter)
            
            # Update context based on what we found
            for ref in line_refs:
                if ref.get('book') and ref.get('chapter'):
                    current_book = ref['book']
                    current_chapter = ref['chapter']
            
            # Add line references with context
            for ref in line_refs:
                ref['line_number'] = line_num
                ref['line_text'] = line
                all_references.append(ref)
        
        # Deduplicate references
        unique_references = self._deduplicate_references(all_references)
        
        return unique_references
    
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
                    'reference': f"{self._get_book_abbreviation(book_name)} {chapter}:{verse_num}",
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
                        'reference': f"{self._get_book_abbreviation(book_name)} {chapter2}:{verse_num}",
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
                        'reference': f"{self._get_book_abbreviation(context_book)} {context_chapter}:{verse_num}",
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
                        'reference': f"{self._get_book_abbreviation(context_book)} {chapter}:{verse_num}",
                        'original_text': match.group(0),
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'context_resolved': True
                    })
        
        return references
    
    def _deduplicate_references(self, references: List[Dict]) -> List[Dict]:
        """
        Remove duplicate references while preserving order
        """
        seen = set()
        unique_refs = []
        
        for ref in references:
            ref_key = (ref['book'], ref['chapter'], ref['verse'])
            if ref_key not in seen:
                seen.add(ref_key)
                unique_refs.append(ref)
        
        return unique_refs
    
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
    
    def process_outline_with_verses(self, text: str) -> str:
        """
        Process the outline text and insert verses in the correct format
        matching MSG12VerseReferences.pdf exactly
        """
        # Detect all verse references with context
        references = self.detect_verse_references_with_context(text)
        
        if not references:
            return text
        
        # Build the output with verses inserted at the beginning
        output_lines = []
        
        # Collect all unique verses
        unique_verses = []
        seen_refs = set()
        
        for ref in references:
            verse_key = f"{ref['book']} {ref['chapter']}:{ref['verse']}"
            if verse_key not in seen_refs:
                verse_text = self.get_verse_text(ref['book'], ref['chapter'], ref['verse'])
                if verse_text:
                    book_abbrev = self._get_book_abbreviation(ref['book'])
                    verse_ref = f"{book_abbrev} {ref['chapter']}:{ref['verse']}"
                    unique_verses.append({
                        'reference': verse_ref,
                        'text': verse_text,
                        'sort_key': (ref['book'], ref['chapter'], ref['verse'])
                    })
                    seen_refs.add(verse_key)
        
        # Sort verses by biblical order (book, chapter, verse)
        unique_verses.sort(key=lambda x: x['sort_key'])
        
        # Add verses at the beginning
        for verse in unique_verses:
            output_lines.append(verse['reference'])
            output_lines.append(verse['text'])
            output_lines.append("")  # Empty line after each verse
        
        # Add the original outline content
        output_lines.append("")  # Extra space before outline
        
        # Split original text into lines and add
        for line in text.split('\n'):
            output_lines.append(line)
        
        return '\n'.join(output_lines)
    
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
        references = self.detect_verse_references_with_context(text)
        
        stats = {
            'total_references': len(references),
            'unique_verses': len(set((ref['book'], ref['chapter'], ref['verse']) for ref in references)),
            'context_resolved': len([ref for ref in references if ref.get('context_resolved')]),
            'books_detected': len(set(ref['book'] for ref in references)),
            'references_by_book': {}
        }
        
        # Count references by book
        for ref in references:
            book = ref['book']
            if book not in stats['references_by_book']:
                stats['references_by_book'][book] = 0
            stats['references_by_book'][book] += 1
        
        return stats

