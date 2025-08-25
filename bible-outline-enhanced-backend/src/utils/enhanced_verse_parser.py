import re
from typing import List, Dict, Tuple, Optional

class EnhancedVerseParser:
    def __init__(self):
        # Common Bible book abbreviations and their full names
        self.book_mappings = {
            # Old Testament
            'Gen': 'Genesis', 'Genesis': 'Genesis',
            'Exo': 'Exodus', 'Exodus': 'Exodus', 'Exod': 'Exodus',
            'Lev': 'Leviticus', 'Leviticus': 'Leviticus',
            'Num': 'Numbers', 'Numbers': 'Numbers',
            'Deut': 'Deuteronomy', 'Deuteronomy': 'Deuteronomy',
            'Josh': 'Joshua', 'Joshua': 'Joshua',
            'Judg': 'Judges', 'Judges': 'Judges',
            'Ruth': 'Ruth',
            '1 Sam': '1 Samuel', '1 Samuel': '1 Samuel', '1Sam': '1 Samuel',
            '2 Sam': '2 Samuel', '2 Samuel': '2 Samuel', '2Sam': '2 Samuel',
            '1 Kings': '1 Kings', '1Kings': '1 Kings', '1 Kgs': '1 Kings',
            '2 Kings': '2 Kings', '2Kings': '2 Kings', '2 Kgs': '2 Kings',
            '1 Chr': '1 Chronicles', '1 Chronicles': '1 Chronicles',
            '2 Chr': '2 Chronicles', '2 Chronicles': '2 Chronicles',
            'Ezra': 'Ezra',
            'Neh': 'Nehemiah', 'Nehemiah': 'Nehemiah',
            'Esth': 'Esther', 'Esther': 'Esther',
            'Job': 'Job',
            'Psa': 'Psalms', 'Psalms': 'Psalms', 'Ps': 'Psalms',
            'Prov': 'Proverbs', 'Proverbs': 'Proverbs',
            'Eccl': 'Ecclesiastes', 'Ecclesiastes': 'Ecclesiastes',
            'S.S.': 'Song of Songs', 'Song': 'Song of Songs', 'Song of Songs': 'Song of Songs',
            'Isa': 'Isaiah', 'Isaiah': 'Isaiah',
            'Jer': 'Jeremiah', 'Jeremiah': 'Jeremiah',
            'Lam': 'Lamentations', 'Lamentations': 'Lamentations',
            'Ezek': 'Ezekiel', 'Ezekiel': 'Ezekiel',
            'Dan': 'Daniel', 'Daniel': 'Daniel',
            'Hosea': 'Hosea', 'Hos': 'Hosea',
            'Joel': 'Joel',
            'Amos': 'Amos',
            'Obad': 'Obadiah', 'Obadiah': 'Obadiah',
            'Jonah': 'Jonah',
            'Micah': 'Micah', 'Mic': 'Micah',
            'Nah': 'Nahum', 'Nahum': 'Nahum',
            'Hab': 'Habakkuk', 'Habakkuk': 'Habakkuk',
            'Zeph': 'Zephaniah', 'Zephaniah': 'Zephaniah',
            'Hag': 'Haggai', 'Haggai': 'Haggai',
            'Zech': 'Zechariah', 'Zechariah': 'Zechariah',
            'Mal': 'Malachi', 'Malachi': 'Malachi',
            
            # New Testament
            'Matt': 'Matthew', 'Matthew': 'Matthew', 'Mt': 'Matthew',
            'Mark': 'Mark', 'Mk': 'Mark',
            'Luke': 'Luke', 'Lk': 'Luke',
            'John': 'John', 'Jn': 'John',
            'Acts': 'Acts',
            'Rom': 'Romans', 'Romans': 'Romans',
            '1 Cor': '1 Corinthians', '1 Corinthians': '1 Corinthians', '1Cor': '1 Corinthians',
            '2 Cor': '2 Corinthians', '2 Corinthians': '2 Corinthians', '2Cor': '2 Corinthians',
            'Gal': 'Galatians', 'Galatians': 'Galatians',
            'Eph': 'Ephesians', 'Ephesians': 'Ephesians',
            'Phil': 'Philippians', 'Philippians': 'Philippians',
            'Col': 'Colossians', 'Colossians': 'Colossians',
            '1 Thes': '1 Thessalonians', '1 Thessalonians': '1 Thessalonians', '1Thes': '1 Thessalonians',
            '2 Thes': '2 Thessalonians', '2 Thessalonians': '2 Thessalonians', '2Thes': '2 Thessalonians',
            '1 Tim': '1 Timothy', '1 Timothy': '1 Timothy', '1Tim': '1 Timothy',
            '2 Tim': '2 Timothy', '2 Timothy': '2 Timothy', '2Tim': '2 Timothy',
            'Titus': 'Titus',
            'Philem': 'Philemon', 'Philemon': 'Philemon',
            'Heb': 'Hebrews', 'Hebrews': 'Hebrews',
            'James': 'James', 'Jas': 'James',
            '1 Pet': '1 Peter', '1 Peter': '1 Peter', '1Pet': '1 Peter',
            '2 Pet': '2 Peter', '2 Peter': '2 Peter', '2Pet': '2 Peter',
            '1 John': '1 John', '1John': '1 John', '1 Jn': '1 John', '1Jo': '1 John',
            '2 John': '2 John', '2John': '2 John', '2 Jn': '2 John', '2Jo': '2 John',
            '3 John': '3 John', '3John': '3 John', '3 Jn': '3 John', '3Jo': '3 John',
            'Jude': 'Jude',
            'Rev': 'Revelation', 'Revelation': 'Revelation'
        }
    
    def extract_references_from_text(self, text: str) -> List[str]:
        """Extract all verse references from text with enhanced patterns"""
        references = []
        
        # Pattern 1: Standard references like "John 3:16", "1 John 4:8", "Eph. 1:5"
        pattern1 = r'\b([1-3]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+(?:[-,]\s*\d+)*(?:\s*[;]\s*\d+:\d+(?:[-,]\s*\d+)*)*)\b'
        
        # Pattern 2: Cross-references like "cf. 2 Cor. 1:15"
        pattern2 = r'\bcf\.\s+([1-3]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+(?:[-,]\s*\d+)*)\b'
        
        # Pattern 3: Verse abbreviations like "v. 6", "vv. 15-16"
        pattern3 = r'\bvv?\.\s+(\d+(?:[-,]\s*\d+)*)\b'
        
        # Pattern 4: Complex multi-book references like "Eph 4:7-16; 6:10-20"
        pattern4 = r'\b([1-3]?\s*[A-Za-z]+\.?)\s+(\d+:\d+(?:[-,]\s*\d+)*(?:\s*[;]\s*\d+:\d+(?:[-,]\s*\d+)*)*)\b'
        
        # Pattern 5: References in parentheses like "(v. 6)", "(vv. 15-16)"
        pattern5 = r'\(\s*vv?\.\s+(\d+(?:[-,]\s*\d+)*)\s*\)'
        
        # Pattern 6: References after dashes (subpoints)
        pattern6 = r'—\s*([1-3]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+(?:[-,]\s*\d+)*)\b'
        
        # Find all matches
        for pattern in [pattern1, pattern2, pattern4, pattern6]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 3:
                    book = match.group(1).strip()
                    chapter_verse = f"{match.group(2)}:{match.group(3)}"
                    full_ref = f"{book} {chapter_verse}"
                    if full_ref not in references:
                        references.append(full_ref)
                elif len(match.groups()) == 2:
                    book = match.group(1).strip()
                    chapter_verse = match.group(2)
                    full_ref = f"{book} {chapter_verse}"
                    if full_ref not in references:
                        references.append(full_ref)
        
        # Handle verse abbreviations (need context for book/chapter)
        # This would need additional context processing
        
        return references
    
    def parse_reference(self, reference_string: str) -> List[Dict]:
        """Parse a verse reference string into structured data"""
        try:
            references = []
            reference_string = reference_string.strip()
            
            # Remove "cf." prefix if present
            if reference_string.lower().startswith('cf.'):
                reference_string = reference_string[3:].strip()
            
            # Handle multiple books separated by semicolons
            if ';' in reference_string:
                parts = reference_string.split(';')
                current_book = None
                
                for i, part in enumerate(parts):
                    part = part.strip()
                    
                    # Check if this part has a book name
                    book_match = re.match(r'^([1-3]?\s*[A-Za-z]+\.?)\s+(.+)$', part)
                    if book_match:
                        current_book = book_match.group(1).strip()
                        chapter_verse = book_match.group(2).strip()
                    else:
                        # No book name, use the current book
                        if current_book:
                            chapter_verse = part
                        else:
                            continue
                    
                    # Parse this part
                    single_ref = f"{current_book} {chapter_verse}"
                    references.extend(self._parse_single_reference(single_ref))
                
                return references
            else:
                return self._parse_single_reference(reference_string)
        
        except Exception as e:
            print(f"Error parsing reference '{reference_string}': {e}")
            return []
    
    def _parse_single_reference(self, reference_string: str) -> List[Dict]:
        """Parse a single reference without semicolons"""
        try:
            # Match pattern like "John 3:16-18" or "Eph. 1:5, 9"
            pattern = r'^([1-3]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+(?:[-,]\s*\d+)*(?:\s*[;]\s*\d+:\d+(?:[-,]\s*\d+)*)*)$'
            match = re.match(pattern, reference_string.strip())
            
            if not match:
                return []
            
            book_name = match.group(1).strip()
            chapter = int(match.group(2))
            verse_part = match.group(3)
            
            # Normalize book name
            normalized_book = self._normalize_book_name(book_name)
            
            # Parse verse numbers
            verses = self._parse_verse_numbers(verse_part)
            
            # Create reference objects
            references = []
            for verse in verses:
                references.append({
                    'book': normalized_book,
                    'chapter': chapter,
                    'verse': verse,
                    'reference': f"{normalized_book} {chapter}:{verse}",
                    'original_book': book_name
                })
            
            return references
        
        except Exception as e:
            print(f"Error parsing single reference '{reference_string}': {e}")
            return []
    
    def _parse_verse_numbers(self, verse_part: str) -> List[int]:
        """Parse verse numbers from a string like '5, 9' or '1-3, 5'"""
        verses = []
        
        for verse_str in verse_part.split(','):
            verse_str = verse_str.strip()
            if '-' in verse_str:
                # Handle ranges like "5-8"
                try:
                    start, end = map(int, verse_str.split('-'))
                    verses.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    verses.append(int(verse_str))
                except ValueError:
                    continue
        
        return sorted(set(verses))
    
    def _normalize_book_name(self, book_name: str) -> str:
        """Normalize book name to full canonical name"""
        # Remove periods and normalize spacing
        clean_name = re.sub(r'\.', '', book_name).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        # Try exact match first
        if clean_name in self.book_mappings:
            return self.book_mappings[clean_name]
        
        # Try with period
        with_period = clean_name + '.'
        if with_period in self.book_mappings:
            return self.book_mappings[with_period]
        
        # Try case-insensitive match
        for key, value in self.book_mappings.items():
            if key.lower() == clean_name.lower():
                return value
        
        # Return original if no match found
        return book_name
    
    def format_references_for_output(self, references: List[Dict], format_type: str = "bottom") -> str:
        """Format references for output according to user preferences"""
        if not references:
            return ""
        
        if format_type == "bottom":
            # Group references by book and chapter
            grouped = {}
            for ref in references:
                book = ref['book']
                chapter = ref['chapter']
                verse = ref['verse']
                
                if book not in grouped:
                    grouped[book] = {}
                if chapter not in grouped[book]:
                    grouped[book][chapter] = []
                
                grouped[book][chapter].append(verse)
            
            # Format output
            output_lines = []
            for book, chapters in grouped.items():
                for chapter, verses in chapters.items():
                    verses = sorted(set(verses))
                    verse_ranges = self._compress_verse_list(verses)
                    ref_string = f"{book} {chapter}:{verse_ranges}"
                    output_lines.append(ref_string)
            
            return "\n".join(output_lines)
        
        return ""
    
    def _compress_verse_list(self, verses: List[int]) -> str:
        """Compress a list of verses into ranges where possible"""
        if not verses:
            return ""
        
        verses = sorted(set(verses))
        ranges = []
        start = verses[0]
        end = verses[0]
        
        for i in range(1, len(verses)):
            if verses[i] == end + 1:
                end = verses[i]
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = verses[i]
        
        # Add the last range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        
        return ', '.join(ranges)

