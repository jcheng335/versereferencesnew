#!/usr/bin/env python3
"""
LLM-First Verse Detector - Uses OpenAI GPT as primary method with training examples
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
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

class LLMFirstDetector:
    """Primary LLM-based detector with training examples"""
    
    def __init__(self, openai_key: str = None):
        self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_key:
            raise ValueError("OpenAI API key required for LLM-first detector")
        
        self.client = OpenAI(api_key=self.openai_key)
        self.training_examples = self._load_training_examples()
        
    def _load_training_examples(self) -> str:
        """Load training examples from Message PDFs"""
        # Load the perfect training data with all verses from Message PDFs
        perfect_path = Path(__file__).parent.parent.parent.parent / 'perfect_training_data.json'
        examples = []
        
        if perfect_path.exists():
            with open(perfect_path, 'r') as f:
                data = json.load(f)
                
                # Get examples from W24ECT12 (Message_12)
                for outline in data.get('outlines', []):
                    if outline.get('outline_id') == 'W24ECT12':
                        verses = outline.get('verses', [])
                        # Show diverse examples
                        example_verses = [
                            "Eph. 4:7-16",  # Scripture reading
                            "Eph 4:7",      # Simple reference
                            "Psalm 68:18",  # Parenthetical
                            "v. 11",        # Standalone verse
                            "vv. 11-16",    # Verse range
                            "Acts 2:33",    # Cross reference
                            "1 Cor. 12:28", # Numbered book
                        ]
                        
                        for ex in example_verses:
                            for v in verses:
                                if ex in v.get('reference', ''):
                                    examples.append(v.get('reference'))
                                    break
                        break
        
        return '\n'.join(f"- {ex}" for ex in examples[:20])
    
    def detect_verses(self, text: str, use_training: bool = True, _internal_call: bool = False) -> List[VerseReference]:
        """Detect verses using LLM with training examples"""
        
        # For large documents, process in chunks
        if len(text) > 10000 and not _internal_call:
            # Process the full document in chunks
            return self._detect_verses_chunked(text, use_training)
        
        # Use simplified prompt for better results
        prompt = self._build_simple_prompt(text)
        
        try:
            # Try GPT-5 first, fallback to GPT-4
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Use GPT-4o-mini for faster processing
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a Bible verse reference extractor. Return ONLY a JSON array with verse references. No explanations, no markdown, just JSON."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.1,  # Low temperature for consistency
                    max_completion_tokens=4000,  # Use max_completion_tokens
                    timeout=60  # 1 minute timeout
                )
            except Exception as gpt5_error:
                # Fallback to GPT-4 if GPT-5 fails
                print(f"GPT-4o-mini failed ({str(gpt5_error)[:100]}), falling back to GPT-3.5-turbo...")
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Fallback to GPT-3.5
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a Bible verse reference extractor. Return ONLY a JSON array with verse references. No explanations, no markdown, just JSON."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=4000,  # GPT-3.5 uses max_tokens
                    timeout=60
                )
            
            content = response.choices[0].message.content
            print(f"[DEBUG] LLM raw response length: {len(content) if content else 0} chars")
            if content:
                print(f"[DEBUG] LLM response preview: {content[:1000]}")
            verses = self._parse_llm_response(content)
            
            print(f"LLM detected {len(verses)} verses")
            return verses
            
        except Exception as e:
            print(f"LLM detection error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _detect_verses_chunked(self, text: str, use_training: bool) -> List[VerseReference]:
        """Process large text in chunks"""
        all_verses = []
        seen_refs = set()
        
        # Split text into larger chunks to reduce API calls
        # Process in 9000 char chunks with overlap
        chunk_size = 9000
        overlap = 500
        
        chunks_processed = 0
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            chunks_processed += 1
            
            print(f"[DEBUG] Processing chunk {chunks_processed} ({len(chunk)} chars)")
            
            # Detect verses in this chunk - use _internal_call flag to prevent recursion
            chunk_verses = self.detect_verses(chunk, use_training=False, _internal_call=True)
            
            # Add unique verses
            for v in chunk_verses:
                ref_key = f"{v.book}_{v.chapter}_{v.start_verse}_{v.end_verse}"
                if ref_key not in seen_refs:
                    seen_refs.add(ref_key)
                    all_verses.append(v)
        
        print(f"[DEBUG] Processed {chunks_processed} chunks")
        print(f"Total unique verses from chunked processing: {len(all_verses)}")
        return all_verses
    
    def _extract_relevant_lines(self, text: str) -> str:
        """Extract only lines that likely contain verse references to reduce text size"""
        import re
        
        relevant_lines = []
        lines = text.split('\n')
        
        # Patterns that indicate a line might contain verse references
        verse_patterns = [
            r'Scripture Reading',
            r'\b(?:Rom|Cor|Gal|Eph|Phil|Col|Thess|Tim|Titus|Philem|Heb|James|Pet|John|Jude|Rev|Matt|Mark|Luke|Acts)',
            r'\b(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles)',
            r'\b(?:Ezra|Nehemiah|Esther|Job|Psalm|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|Lamentations)',
            r'\b(?:Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi)',
            r'\b(?:cf\.|v\.|vv\.|verse|verses|chapter)',
            r'\(\s*[A-Z]',  # Parenthetical references often start with capital letter
            r'\d+:\d+',  # Chapter:verse pattern
            r'according to',
        ]
        
        combined_pattern = '|'.join(verse_patterns)
        pattern = re.compile(combined_pattern, re.IGNORECASE)
        
        # Always include first 10 lines (often contains Scripture Reading)
        for i, line in enumerate(lines[:10]):
            relevant_lines.append(line)
        
        # Then check remaining lines  
        seen_lines = set(relevant_lines)
        for i, line in enumerate(lines[10:], 10):
            if pattern.search(line) and line not in seen_lines:
                relevant_lines.append(line)
                seen_lines.add(line)
                # Limit to 5000 chars max to prevent timeout
                if len('\n'.join(relevant_lines)) > 5000:
                    break
        
        result = '\n'.join(relevant_lines)
        # Hard limit at 5000 chars
        if len(result) > 5000:
            result = result[:5000]
        return result
    
    def _build_simple_prompt(self, text: str) -> str:
        """Build a simple, effective prompt for verse extraction"""
        return f"""Extract ALL Bible verse references from this theological outline. Return ONLY a JSON array.

CRITICAL: This is a theological outline with:
- Title/Message Number at the top
- Scripture Reading section with verse ranges
- Outline points (I, II, A, B, 1, 2, etc.)
- Verses embedded throughout the text

INSTRUCTIONS:

1. EXTRACT DOCUMENT METADATA (if present):
   - Message number (e.g., "Message Two", "Message Six")
   - Title/subtitle lines after the message number
   - Hymn references

2. SCRIPTURE READING - EXPAND ALL RANGES:
   - "Scripture Reading: Rom. 8:2, 31-39" → Extract EVERY verse:
     * Rom. 8:2 (single verse)
     * Rom. 8:31, 8:32, 8:33, 8:34, 8:35, 8:36, 8:37, 8:38, 8:39 (entire range)
   - IMPORTANT: Ranges like "31-39" mean ALL verses from 31 through 39
   - Split multiple references: "Eph. 4:7-16; 6:10-20" → Expand both ranges

3. VERSE RANGES - ALWAYS EXPAND:
   - "Rom. 8:31-39" → Create entries for verses 31, 32, 33, 34, 35, 36, 37, 38, 39
   - "Matt. 5:3-12" → Create entries for verses 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
   - Each verse in a range gets its own entry

4. DETECT ALL PATTERNS:
   - Parenthetical: "(Acts 10:43)"
   - Written out: "First Corinthians chapter one verse two"
   - Abbreviations: "1 Cor. 1:2"
   - Standalone: "v. 7", "vv. 23-24" (resolve from context)
   - Lists: "Rom. 16:1, 4-5, 16" → Rom. 16:1, Rom. 16:4-5, Rom. 16:16

5. BOOK NAME NORMALIZATION:
   - Rom → Romans
   - 1 Cor → 1 Corinthians
   - Matt → Matthew
   - etc.

Output format - JSON array with EVERY verse (expand all ranges):
[
  {{"reference": "Rom. 8:2", "book": "Romans", "chapter": 8, "start_verse": 2, "end_verse": 2}},
  {{"reference": "Rom. 8:31", "book": "Romans", "chapter": 8, "start_verse": 31, "end_verse": 31}},
  {{"reference": "Rom. 8:32", "book": "Romans", "chapter": 8, "start_verse": 32, "end_verse": 32}},
  ...continue for EVERY verse in the range...
]

Text to analyze:
{text[:6000]}"""
    
    def _get_few_shot_examples(self) -> str:
        """Provide specific examples from actual training data"""
        
        return """
PROVEN EXAMPLES FROM TRAINING DATA:

Input: "Scripture Reading: Eph. 4:7-16; 6:10-20"
Output: ["Eph. 4:7-16", "Eph. 6:10-20"]

Input: "Christ ascended to the heavens (Psalm 68:18) to give gifts"
Output: ["Psalm 68:18"]

Input: "According to Luke 7, Jesus said to the woman (vv. 47-48)"
Output: ["Luke 7:47-48"] (resolved from context)

Input: "The gifts mentioned in Rom. 16:1, 4-5, 16, 20 include..."
Output: ["Rom. 16:1", "Rom. 16:4-5", "Rom. 16:16", "Rom. 16:20"]

Input: "As prophesied (cf. Luke 4:18), the Lord came"
Output: ["Luke 4:18"]

Input: "In v. 11, we see the gifts" (with Scripture Reading: Eph. 4:7-16)
Output: ["Eph. 4:11"] (resolved from Scripture Reading)
"""
    
    def _build_prompt(self, text: str, use_training: bool) -> str:
        """Build the prompt for GPT"""
        
        # Get few-shot examples
        examples = self._get_few_shot_examples()
        
        return f"""You are an expert at extracting Bible verse references from theological outlines.

TASK: Extract ALL verse references from this outline and format them for margin placement.

CRITICAL PATTERNS TO DETECT (with real examples from our training data):

1. **Scripture Reading** (always at the beginning):
   - "Scripture Reading: Eph. 4:7-16; 6:10-20" → Extract both: Eph. 4:7-16, Eph. 6:10-20

2. **Parenthetical references** (in parentheses):
   - "(Psalm 68:18)" → Psalm 68:18
   - "(cf. Acts 10:43)" → Acts 10:43
   - "(Num. 10:35)" → Num. 10:35

3. **Standalone verses** (MUST resolve using context):
   - If Scripture Reading says "Luke 7:36-50", then:
     - "v. 47" → Luke 7:47
     - "vv. 47-48" → Luke 7:47-48
     - "v. 50" → Luke 7:50

4. **Inline references**:
   - "according to Rom. 12:3" → Rom. 12:3
   - "in 1 Cor. 12:14-22" → 1 Cor. 12:14-22
   - "as in John 14:6a" → John 14:6

5. **Complex lists** (with commas and ranges):
   - "Rom. 16:1, 4-5, 16, 20" → Rom. 16:1, Rom. 16:4-5, Rom. 16:16, Rom. 16:20
   - "Eph. 4:8-12" → Eph. 4:8-12

6. **Cross-references** (with "cf."):
   - "cf. Luke 4:18" → Luke 4:18
   - "cf. Rom. 12:3" → Rom. 12:3

7. **Numbered books**:
   - "1 Cor. 12:28" → 1 Cor. 12:28
   - "2 Tim. 1:6-7" → 2 Tim. 1:6-7
   - "1 John 4:8" → 1 John 4:8

8. **Multiple references separated by semicolons**:
   - "Isa. 61:10; Luke 15:22" → Isa. 61:10, Luke 15:22
   - "Rom. 5:1-11; 8:1" → Rom. 5:1-11, Rom. 8:1

{examples}

SPECIAL RULES:
1. For "v." or "vv." references, ALWAYS use the book and chapter from:
   - First: The Scripture Reading at the top
   - Second: The most recent full reference before it
   - Third: Any chapter reference nearby (e.g., "In Luke 7")

2. When you see outline markers (I., II., A., B., 1., 2., a., b.), scan that entire section for verses

3. Look for verses in:
   - Headings and titles
   - Outline points
   - Sub-points
   - Footnotes or explanatory text

EXPECTED OUTPUT FORMAT:
Return a JSON array where each verse is an object:
[
  {{
    "reference": "Eph. 4:7-16",  // Original text as it appears
    "book": "Eph",                // Book abbreviation (no period)
    "chapter": 4,                 // Chapter number
    "start_verse": 7,             // Starting verse
    "end_verse": 16,              // Ending verse (null if single verse)
    "context": "Scripture Reading" // Where it was found
  }},
  {{
    "reference": "v. 11",
    "book": "Eph",               // Resolved from Scripture Reading
    "chapter": 4,                // Resolved from Scripture Reading
    "start_verse": 11,
    "end_verse": null,
    "context": "Resolved from Eph. 4:7-16 Scripture Reading"
  }}
]

QUALITY CHECK:
- For Message Twelve outline, expect ~234 verses
- Every "v." or "vv." MUST be resolved to full reference
- Every parenthetical reference MUST be captured
- Every Scripture Reading verse MUST be included

Text to analyze:
{text}

IMPORTANT: Be exhaustive. It's better to over-detect than miss verses. Find EVERY single verse reference."""
    
    def _parse_llm_response_simple(self, refs: List[str]) -> List[VerseReference]:
        """Parse a simple list of verse references"""
        import re
        verses = []
        
        for ref in refs:
            if not ref or not isinstance(ref, str):
                continue
                
            ref = ref.strip()
            
            # Parse the reference
            # Handle ranges like "Rom. 8:31-39"
            match = re.match(r'([1-3]?\s*[A-Za-z]+)\.?\s+(\d+):(\d+)(?:-(\d+))?', ref)
            if match:
                book = match.group(1).strip()
                chapter = int(match.group(2))
                start_verse = int(match.group(3))
                end_verse = int(match.group(4)) if match.group(4) else None
                
                # Normalize book name
                book = book.replace('.', '').strip()
                
                verses.append(VerseReference(
                    book=book,
                    chapter=chapter,
                    start_verse=start_verse,
                    end_verse=end_verse,
                    original_text=ref,
                    confidence=0.95,
                    pattern="llm"
                ))
        
        return verses
    
    def _parse_llm_response(self, content: str) -> List[VerseReference]:
        """Parse the LLM response into VerseReference objects"""
        verses = []
        
        try:
            # Handle markdown code blocks
            if '```json' in content:
                # Extract JSON from markdown code block
                start_idx = content.find('```json') + 7
                end_idx = content.find('```', start_idx)
                if end_idx > start_idx:
                    json_str = content[start_idx:end_idx].strip()
                else:
                    # Fallback to finding JSON array
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    json_str = content[start_idx:end_idx] if start_idx >= 0 and end_idx > start_idx else ""
            elif '```' in content:
                # Extract from generic code block
                start_idx = content.find('```') + 3
                end_idx = content.find('```', start_idx)
                if end_idx > start_idx:
                    json_str = content[start_idx:end_idx].strip()
                    # Remove language identifier if present
                    if json_str.startswith(('json', 'JSON')):
                        json_str = json_str[4:].strip()
                else:
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    json_str = content[start_idx:end_idx] if start_idx >= 0 and end_idx > start_idx else ""
            else:
                # Extract JSON array directly
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                json_str = content[start_idx:end_idx] if start_idx >= 0 and end_idx > start_idx else ""
            
            if json_str:
                verse_data = json.loads(json_str)
                
                # Check if it's a simple array of strings or structured data
                if verse_data and isinstance(verse_data[0], str):
                    # Simple string array format
                    return self._parse_llm_response_simple(verse_data)
                
                # Otherwise parse as structured objects
                for v in verse_data:
                    if isinstance(v, dict):
                        # Handle both formats (with periods and without)
                        book = v.get('book', '').replace('.', '')
                        
                        # Skip invalid entries
                        if not book or v.get('chapter', 0) == 0:
                            continue
                        
                        verse = VerseReference(
                            book=book,
                            chapter=v.get('chapter', 0),
                            start_verse=v.get('start_verse', 0),
                            end_verse=v.get('end_verse'),
                            original_text=v.get('reference', ''),
                            confidence=0.98,  # High confidence for GPT-4
                            pattern='llm_gpt4',
                            context=v.get('context', '')
                        )
                        verses.append(verse)
            else:
                print("No valid JSON found in LLM response")
                verses = self._fallback_parse(content)
        
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            import traceback
            traceback.print_exc()
            # Try fallback regex parsing
            verses = self._fallback_parse(content)
        
        return verses
    
    def _structure_text_as_html(self, text: str) -> str:
        """Convert plain text to structured HTML-like format"""
        lines = text.split('\n')
        structured = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Mark Scripture Reading
            if line.startswith('Scripture Reading:'):
                structured.append(f'<scripture-reading>{line}</scripture-reading>')
            # Mark outline points
            elif re.match(r'^[IVX]+\.', line):
                structured.append(f'<outline-1>{line}</outline-1>')
            elif re.match(r'^[A-Z]\.', line):
                structured.append(f'<outline-2>{line}</outline-2>')
            elif re.match(r'^[1-9]\d?\.', line):
                structured.append(f'<outline-3>{line}</outline-3>')
            elif re.match(r'^[a-z]\.', line):
                structured.append(f'<outline-4>{line}</outline-4>')
            else:
                structured.append(f'<text>{line}</text>')
        
        return '\n'.join(structured)
    
    def _build_html_prompt(self, html_text: str, use_training: bool) -> str:
        """Build prompt for HTML-structured text"""
        examples = self._get_few_shot_examples() if use_training else ""
        
        return f"""You are an expert at extracting Bible verse references from HTML-structured theological outlines.

The text is already structured with HTML-like tags:
- <scripture-reading> contains the main Scripture Reading
- <outline-1> contains Roman numeral points (I, II, III)
- <outline-2> contains letter points (A, B, C)
- <outline-3> contains number points (1, 2, 3)
- <outline-4> contains lowercase letter points (a, b, c)
- <text> contains regular text

TASK: Extract ALL verse references and format them as JSON.

{examples}

CRITICAL RULES:
1. For "v." or "vv." references, use the book and chapter from Scripture Reading
2. Every parenthetical reference must be captured  
3. Every reference in every outline level must be found
4. IMPORTANT: Scan EVERY line for verses - many verses appear in continuation text after outline markers
5. Look for patterns like: "cf.", "see", "according to", verse numbers in parentheses
6. Include ALL verses mentioned, even if they appear multiple times

HTML-Structured Text:
{html_text}

Return ONLY a JSON array of verse objects. Be exhaustive - find EVERY verse reference."""
    
    def _fallback_parse(self, text: str) -> List[VerseReference]:
        """Comprehensive fallback regex parsing if JSON fails"""
        verses = []
        seen_refs = set()
        
        # Multiple patterns to catch different formats
        patterns = [
            # Standard format: Book Chapter:Verse[-EndVerse]
            (r'([1-3]?\s*[A-Z][a-z]+(?:\s+[A-Z]?[a-z]*)?)\s*\.?\s*(\d+):(\d+)(?:-(\d+))?', 'standard'),
            # Parenthetical: (Book Chapter:Verse)
            (r'\(([1-3]?\s*[A-Z][a-z]+)\s*\.?\s*(\d+):(\d+)(?:-(\d+))?\)', 'parenthetical'),
            # With cf.: cf. Book Chapter:Verse
            (r'cf\.\s+([1-3]?\s*[A-Z][a-z]+)\s*\.?\s*(\d+):(\d+)(?:-(\d+))?', 'cross_ref'),
            # Scripture Reading format
            (r'Scripture Reading:\s*([1-3]?\s*[A-Z][a-z]+)\s*\.?\s*(\d+):(\d+)(?:-(\d+))?', 'scripture_reading'),
        ]
        
        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, text):
                book = match.group(1).strip().replace('.', '')
                chapter = int(match.group(2))
                start = int(match.group(3))
                end = int(match.group(4)) if match.group(4) else None
                
                ref_key = f"{book}_{chapter}_{start}_{end}"
                if ref_key not in seen_refs:
                    seen_refs.add(ref_key)
                    verses.append(VerseReference(
                        book=book,
                        chapter=chapter,
                        start_verse=start,
                        end_verse=end,
                        original_text=match.group(0),
                        confidence=0.85,
                        pattern=f'llm_fallback_{pattern_type}'
                    ))
        
        print(f"Fallback parser found {len(verses)} verses")
        return verses
    
    def process_with_html(self, html_content: str) -> Dict:
        """Process HTML content and extract verses"""
        # Parse HTML to get structure
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract verse references (blue text in margin)
        verse_refs = []
        for verse_span in soup.find_all('span', class_='verse-ref'):
            verse_refs.append(verse_span.text.strip())
        
        # Extract outline text
        outline_text = []
        for outline_span in soup.find_all('span', class_='outline-text'):
            outline_text.append(outline_span.text.strip())
        
        # Build structured result
        result = {
            'verse_references': verse_refs,
            'outline_points': outline_text,
            'total_verses': len(verse_refs)
        }
        
        return result