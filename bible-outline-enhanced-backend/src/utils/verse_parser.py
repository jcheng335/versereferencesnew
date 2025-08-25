import re
from typing import List, Dict, Tuple, Optional

class VerseParser:
    def __init__(self):
        pass
    
    def parse_reference(self, reference_string: str) -> List[Dict]:
        """
        Parse a verse reference string into structured data
        Examples:
        - "John 3:16" -> [{"book": "John", "chapter": 3, "verse": 16}]
        - "John 3:16-18" -> [{"book": "John", "chapter": 3, "verse": 16}, ...]
        - "Eph. 1:5, 9" -> [{"book": "Ephesians", "chapter": 1, "verse": 5}, ...]
        """
        try:
            references = []
            
            # Clean up the reference
            reference_string = reference_string.strip()
            
            # Handle multiple references separated by semicolons
            if ';' in reference_string:
                for ref in reference_string.split(';'):
                    references.extend(self.parse_reference(ref.strip()))
                return references
            
            # Match patterns like "John 3:16", "1 John 4:8", "Eph. 1:5, 9"
            pattern = r'(\d?\s*\w+\.?)\s+(\d+):(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)'
            match = re.match(pattern, reference_string)
            
            if not match:
                return []
            
            book_name = match.group(1).strip()
            chapter = int(match.group(2))
            verse_part = match.group(3)
            
            # Parse verse numbers (handle ranges and lists)
            verses = []
            for verse_str in verse_part.split(','):
                verse_str = verse_str.strip()
                if '-' in verse_str:
                    # Handle ranges like "5-8"
                    start, end = map(int, verse_str.split('-'))
                    verses.extend(range(start, end + 1))
                else:
                    verses.append(int(verse_str))
            
            # Create reference objects
            for verse in verses:
                references.append({
                    'book': book_name,
                    'chapter': chapter,
                    'verse': verse,
                    'reference': f"{book_name} {chapter}:{verse}"
                })
            
            return references
        
        except Exception as e:
            print(f"Error parsing reference '{reference_string}': {e}")
            return []
    
    def extract_references_from_text(self, text: str) -> List[str]:
        """Extract all verse references from a text"""
        # Pattern to match verse references
        # This matches patterns like "John 3:16", "1 John 4:8", "Eph. 1:5, 9; 5:1-14"
        pattern = r'\b([1-3]?\s*[A-Za-z]+\.?\s+\d+:\d+(?:[-,]\s*\d+)*(?:\s*[;]\s*\d+:\d+(?:[-,]\s*\d+)*)*)\b'
        
        matches = re.findall(pattern, text)
        return [match.strip() for match in matches if match.strip()]
    
    def normalize_reference(self, reference: str) -> str:
        """Normalize a reference to a standard format"""
        parsed = self.parse_reference(reference)
        if not parsed:
            return reference
        
        # Group by book and chapter
        grouped = {}
        for ref in parsed:
            book_name = ref['book']
            chapter = ref['chapter']
            verse = ref['verse']
            
            if book_name not in grouped:
                grouped[book_name] = {}
            if chapter not in grouped[book_name]:
                grouped[book_name][chapter] = []
            
            grouped[book_name][chapter].append(verse)
        
        # Build normalized string
        parts = []
        for book_name, chapters in grouped.items():
            book_parts = []
            for chapter, verses in chapters.items():
                verses.sort()
                verse_ranges = self._compress_verse_list(verses)
                book_parts.append(f"{chapter}:{verse_ranges}")
            
            parts.append(f"{book_name} {'; '.join(book_parts)}")
        
        return '; '.join(parts)
    
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

