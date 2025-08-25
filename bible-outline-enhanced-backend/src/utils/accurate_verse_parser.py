"""
Accurate Verse Parser for Bible Outline Verse Populator
Designed to match the exact format shown in MSG12VerseReferences.pdf
"""

import re
from typing import List, Dict, Tuple, Set
from .sqlite_bible_database import SQLiteBibleDatabase

class AccurateVerseParser:
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
    
    def detect_verse_references(self, text: str) -> List[Dict]:
        """
        Detect all verse references in the text and return them with their positions
        """
        references = []
        
        # Pattern for verse references - much more comprehensive
        patterns = [
            # Main pattern: Book Chapter:Verse-Verse; Chapter:Verse-Verse
            r'([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?(?:;\s*(\d+):(\d+)(?:-(\d+))?)*',
            
            # Pattern for "v. X" or "vv. X-Y" 
            r'vv?\.\s*(\d+)(?:-(\d+))?',
            
            # Pattern for "cf. Book Chapter:Verse"
            r'cf\.\s+([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?',
            
            # Pattern for multiple books: "Book Chapter:Verse; Book Chapter:Verse"
            r'([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?(?:;\s*([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?)*'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start_pos = match.start()
                end_pos = match.end()
                reference_text = match.group(0)
                
                # Parse the reference to extract individual verses
                individual_verses = self._parse_reference_to_verses(reference_text)
                
                references.append({
                    'text': reference_text,
                    'start': start_pos,
                    'end': end_pos,
                    'verses': individual_verses
                })
        
        # Sort by position in text
        references.sort(key=lambda x: x['start'])
        return references
    
    def _parse_reference_to_verses(self, reference_text: str) -> List[Dict]:
        """
        Parse a reference text into individual verse objects
        Example: "Eph. 4:7-16; 6:10-20" -> [Eph 4:7, Eph 4:8, ..., Eph 4:16, Eph 6:10, ..., Eph 6:20]
        """
        verses = []
        
        # Clean up the reference text
        ref_text = reference_text.replace('cf.', '').strip()
        
        # Split by semicolons for multiple references
        parts = [part.strip() for part in ref_text.split(';')]
        
        current_book = None
        
        for part in parts:
            # Check if this part has a book name
            book_match = re.match(r'^([123]?\s*[A-Za-z]+\.?)', part)
            if book_match:
                current_book = self._normalize_book_name(book_match.group(1))
                remaining = part[book_match.end():].strip()
            else:
                remaining = part.strip()
            
            if not current_book:
                continue
                
            # Extract chapter:verse patterns
            chapter_verse_pattern = r'(\d+):(\d+)(?:-(\d+))?'
            for match in re.finditer(chapter_verse_pattern, remaining):
                chapter = int(match.group(1))
                start_verse = int(match.group(2))
                end_verse = int(match.group(3)) if match.group(3) else start_verse
                
                # Add all verses in the range
                for verse_num in range(start_verse, end_verse + 1):
                    verses.append({
                        'book': current_book,
                        'chapter': chapter,
                        'verse': verse_num,
                        'reference': f"{current_book} {chapter}:{verse_num}"
                    })
        
        return verses
    
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
        # Detect all verse references
        references = self.detect_verse_references(text)
        
        if not references:
            return text
        
        # Build the output with verses inserted at the beginning
        output_lines = []
        
        # First, add all the verse references at the top
        all_verses = []
        for ref in references:
            for verse_info in ref['verses']:
                verse_text = self.get_verse_text(
                    verse_info['book'], 
                    verse_info['chapter'], 
                    verse_info['verse']
                )
                if verse_text:
                    # Format exactly like MSG12VerseReferences.pdf
                    book_abbrev = self._get_book_abbreviation(verse_info['book'])
                    verse_ref = f"{book_abbrev} {verse_info['chapter']}:{verse_info['verse']}"
                    all_verses.append({
                        'reference': verse_ref,
                        'text': verse_text
                    })
        
        # Remove duplicates while preserving order
        seen_refs = set()
        unique_verses = []
        for verse in all_verses:
            if verse['reference'] not in seen_refs:
                unique_verses.append(verse)
                seen_refs.add(verse['reference'])
        
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

