#!/usr/bin/env python3
"""
Pure LLM-based Verse Detector - No regex, only intelligent LLM detection
Based on comprehensive analysis of 12 outline PDFs with 3,311 verse references
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class VerseReference:
    """Represents a Bible verse reference"""
    book: str
    chapter: int
    start_verse: int
    end_verse: Optional[int]
    original_text: str
    confidence: float = 1.0
    pattern: str = "llm"
    context: str = ""

class PureLLMDetector:
    """Pure LLM-based detector without any regex patterns"""
    
    def __init__(self, openai_key: str = None):
        self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_key:
            raise ValueError("OpenAI API key required for LLM detector")
        
        self.client = OpenAI(api_key=self.openai_key)
    
    def detect_verses(self, text: str) -> List[VerseReference]:
        """Detect verses using pure LLM intelligence"""
        
        # Process in chunks for large documents
        if len(text) > 8000:
            return self._detect_verses_chunked(text)
        
        prompt = self._build_comprehensive_prompt(text)
        
        try:
            # Use GPT-4o-mini for optimal speed and accuracy
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Bible verse reference extractor. Return ONLY valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_completion_tokens=8000,  # Increased for comprehensive detection
                timeout=90  # 90 second timeout
            )
            
            content = response.choices[0].message.content
            verses = self._parse_llm_response(content)
            
            print(f"Pure LLM detected {len(verses)} verses")
            return verses
            
        except Exception as e:
            print(f"LLM detection error: {e}")
            # Fallback to GPT-3.5-turbo
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Extract Bible verses. Return JSON array only."
                        },
                        {
                            "role": "user", 
                            "content": self._build_simple_prompt(text)
                        }
                    ],
                    temperature=0.1,
                    max_tokens=4000,
                    timeout=60
                )
                content = response.choices[0].message.content
                return self._parse_llm_response(content)
            except Exception as e2:
                print(f"Fallback LLM also failed: {e2}")
                return []
    
    def _detect_verses_chunked(self, text: str) -> List[VerseReference]:
        """Process large text in overlapping chunks"""
        all_verses = []
        seen_refs = set()
        
        # Process in 7000 char chunks with 1000 char overlap
        chunk_size = 7000
        overlap = 1000
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            
            # Add context from previous chunk for continuity
            if i > 0:
                chunk = text[max(0, i-200):i] + "\n[...]\n" + chunk
            
            chunk_verses = self.detect_verses(chunk)
            
            # Add unique verses
            for v in chunk_verses:
                ref_key = f"{v.book}_{v.chapter}_{v.start_verse}_{v.end_verse}"
                if ref_key not in seen_refs:
                    seen_refs.add(ref_key)
                    all_verses.append(v)
        
        return all_verses
    
    def _build_comprehensive_prompt(self, text: str) -> str:
        """Build comprehensive prompt based on analysis of 3,311 verse references"""
        return f"""You are analyzing a theological outline document that contains Bible verse references.
Based on analysis of 12 similar documents with 3,311 verse references, extract ALL verses.

DOCUMENT STRUCTURE TO RECOGNIZE:
1. Title section (may contain "Message [Number]", title, subtitle, hymn references)
2. Scripture Reading section (contains main verses, often with ranges like "Rom. 8:2, 31-39")
3. Outline points (I., II., A., B., 1., 2., a., b.) with embedded verses
4. Body text with verse references throughout

VERSE FORMATS TO DETECT (all 1,797 variations found):

1. SCRIPTURE READING PATTERNS:
   - "Scripture Reading: Rom. 8:2, 31-39" → Expand to ALL verses
   - "Scripture Reading: Eph. 4:7-16; 6:10-20" → Multiple books/chapters
   - Ranges MUST be expanded: "31-39" = verses 31, 32, 33, 34, 35, 36, 37, 38, 39

2. STANDARD REFERENCES (422 formats):
   - "John 3:16" - simple format
   - "1 John 4:8, 16" - numbered book with list
   - "Matt. 5:3-12" - abbreviated with range
   - "Romans 8:28-30" - full name with range
   - "Eph. 1:5, 9" - abbreviated with comma list
   - "2 Cor. 5:17-21" - numbered book with range

3. PARENTHETICAL (41 formats):
   - "(Acts 10:43)" - simple parenthetical
   - "(cf. Rom. 12:3)" - cross-reference
   - "(see Gal. 2:20)" - with "see"
   - "(vv. 47-48)" - verses in parentheses
   - "(Num. 10:35; Psalm 68:1)" - multiple in parentheses

4. STANDALONE VERSES (48 formats):
   - "v. 7" - single verse (resolve from context)
   - "vv. 31-39" - verse range (resolve from context)
   - "verses 23-24" - written out
   - "verse 16a" - with letter suffix
   - Context: If Scripture Reading mentions "Rom. 8", then "v. 2" = "Rom. 8:2"

5. CROSS-REFERENCES (37 formats):
   - "cf. Luke 4:18" - compare with
   - "cf. Rom. 12:3, 6-8" - with list
   - "cf. 1 Cor. 12:14-22" - numbered book

6. COMPLEX PATTERNS (224 formats):
   - "Gen. 3:15; Isa. 7:14; Matt. 1:16, 20-21, 23" - multi-book chain
   - "Rom. 16:1, 4-5, 16, 20" - complex list with ranges
   - "John 1:1, 14; Heb. 2:14" - semicolon separated books
   - "Psalm 68:18a; Acts 2:33; Eph. 4:8" - with letter suffixes

7. SPECIAL CASES:
   - Letter suffixes: "John 14:6a" (verse 6, part a)
   - Split across lines (text may break mid-reference)
   - Embedded in sentences: "according to Romans 8:28-30"
   - Written forms: "First Corinthians" = "1 Corinthians"

CRITICAL EXPANSION RULES:
- ALWAYS expand ranges: "Rom. 8:31-39" → create 9 separate verse entries
- ALWAYS resolve context: "v. 2" needs book/chapter from Scripture Reading
- ALWAYS split semicolons: "Eph. 4:7-16; 6:10-20" → two separate ranges
- ALWAYS normalize books: "Rom" → "Romans", "1 Cor" → "1 Corinthians"

OUTPUT FORMAT (JSON array with expanded verses):
[
  {{"reference": "Rom. 8:2", "book": "Romans", "chapter": 8, "start_verse": 2, "end_verse": null}},
  {{"reference": "Rom. 8:31", "book": "Romans", "chapter": 8, "start_verse": 31, "end_verse": null}},
  {{"reference": "Rom. 8:32", "book": "Romans", "chapter": 8, "start_verse": 32, "end_verse": null}},
  ... (continue for EVERY verse in ranges)
]

IMPORTANT: 
- Extract EVERY verse reference, no matter how it appears
- Expand ALL ranges into individual verses
- Use context to resolve incomplete references
- Return ONLY the JSON array, no explanations

Text to analyze:
{text[:7000]}"""
    
    def _build_simple_prompt(self, text: str) -> str:
        """Simplified prompt for fallback"""
        return f"""Extract all Bible verse references from this outline.

Common formats:
- Scripture Reading: Rom. 8:2, 31-39
- Standard: John 3:16, Matt. 5:3-12
- Parenthetical: (Acts 10:43)
- Standalone: v. 7, vv. 31-39
- Lists: Rom. 16:1, 4-5, 16

Expand ALL ranges (31-39 = 31,32,33,34,35,36,37,38,39).
Return JSON array only.

Text: {text[:4000]}"""
    
    def _parse_llm_response(self, content: str) -> List[VerseReference]:
        """Parse the LLM response into VerseReference objects"""
        verses = []
        
        try:
            # Clean up response
            if '```json' in content:
                start_idx = content.find('```json') + 7
                end_idx = content.find('```', start_idx)
                json_str = content[start_idx:end_idx].strip()
            elif '```' in content:
                start_idx = content.find('```') + 3
                end_idx = content.find('```', start_idx)
                json_str = content[start_idx:end_idx].strip()
                if json_str.startswith(('json', 'JSON')):
                    json_str = json_str[4:].strip()
            else:
                # Find JSON array
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                json_str = content[start_idx:end_idx] if start_idx >= 0 and end_idx > start_idx else ""
            
            if json_str:
                verse_data = json.loads(json_str)
                
                for v in verse_data:
                    if isinstance(v, dict):
                        book = v.get('book', '').strip()
                        chapter = v.get('chapter', 0)
                        start = v.get('start_verse', 0)
                        end = v.get('end_verse')
                        
                        # Skip invalid entries
                        if not book or chapter == 0 or start == 0:
                            continue
                        
                        # Normalize book names
                        book = self._normalize_book_name(book)
                        
                        verse = VerseReference(
                            book=book,
                            chapter=chapter,
                            start_verse=start,
                            end_verse=end,
                            original_text=v.get('reference', ''),
                            confidence=0.95,
                            pattern='pure_llm',
                            context=v.get('context', '')
                        )
                        verses.append(verse)
        
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
        
        return verses
    
    def _normalize_book_name(self, book: str) -> str:
        """Normalize book names to standard format"""
        book = book.replace('.', '').strip()
        
        # Common abbreviations to full names
        book_map = {
            'Rom': 'Romans', 'Matt': 'Matthew', 'Mk': 'Mark', 'Lk': 'Luke',
            'Jn': 'John', '1 Cor': '1 Corinthians', '2 Cor': '2 Corinthians',
            'Gal': 'Galatians', 'Eph': 'Ephesians', 'Phil': 'Philippians',
            'Col': 'Colossians', '1 Thess': '1 Thessalonians', '2 Thess': '2 Thessalonians',
            '1 Tim': '1 Timothy', '2 Tim': '2 Timothy', 'Tit': 'Titus',
            'Philem': 'Philemon', 'Heb': 'Hebrews', 'Jas': 'James',
            '1 Pet': '1 Peter', '2 Pet': '2 Peter', '1 Jn': '1 John',
            '2 Jn': '2 John', '3 Jn': '3 John', 'Rev': 'Revelation',
            'Gen': 'Genesis', 'Ex': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers',
            'Deut': 'Deuteronomy', 'Josh': 'Joshua', 'Judg': 'Judges',
            '1 Sam': '1 Samuel', '2 Sam': '2 Samuel', 'Ps': 'Psalms', 'Psalm': 'Psalms',
            'Prov': 'Proverbs', 'Eccl': 'Ecclesiastes', 'Song': 'Song of Solomon',
            'Isa': 'Isaiah', 'Jer': 'Jeremiah', 'Lam': 'Lamentations',
            'Ezek': 'Ezekiel', 'Dan': 'Daniel', 'Hos': 'Hosea', 'Obad': 'Obadiah',
            'Mic': 'Micah', 'Nah': 'Nahum', 'Hab': 'Habakkuk', 'Zeph': 'Zephaniah',
            'Hag': 'Haggai', 'Zech': 'Zechariah', 'Mal': 'Malachi'
        }
        
        # First try exact match
        if book in book_map:
            return book_map[book]
        
        # Try without spaces
        book_no_space = book.replace(' ', '')
        for abbr, full in book_map.items():
            if abbr.replace(' ', '') == book_no_space:
                return full
        
        # Return as-is if not found
        return book