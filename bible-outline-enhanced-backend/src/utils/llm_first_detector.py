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
        
        # For large documents, use smart extraction to reduce text size
        if len(text) > 8000 and not _internal_call:
            # Extract only the lines that likely contain verse references
            text = self._extract_relevant_lines(text)
            print(f"[DEBUG] Reduced text from original to {len(text)} chars for LLM processing")
        
        prompt = self._build_prompt(text, use_training)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use GPT-3.5 for faster processing
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert Bible verse reference extractor. 
                        Your task is to find ALL verse references in Bible study outlines.
                        Be extremely thorough - missing verses is unacceptable."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=4000
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
        # GPT-4 can handle up to 8000 chars comfortably
        chunk_size = 7500
        overlap = 500
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            
            # Detect verses in this chunk - use _internal_call flag to prevent recursion
            chunk_verses = self.detect_verses(chunk, use_training=False, _internal_call=True)
            
            # Add unique verses
            for v in chunk_verses:
                if v.original_text not in seen_refs:
                    seen_refs.add(v.original_text)
                    all_verses.append(v)
        
        print(f"Total verses from chunked processing: {len(all_verses)}")
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
        for i, line in enumerate(lines[10:], 10):
            if pattern.search(line):
                # Include this line and context (one line before and after)
                if i > 0 and lines[i-1] not in relevant_lines:
                    relevant_lines.append(lines[i-1])
                relevant_lines.append(line)
                if i < len(lines) - 1:
                    relevant_lines.append(lines[i+1])
        
        return '\n'.join(relevant_lines)
    
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
    
    def _parse_llm_response(self, content: str) -> List[VerseReference]:
        """Parse the LLM response into VerseReference objects"""
        verses = []
        
        try:
            # Extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                verse_data = json.loads(json_str)
                
                for v in verse_data:
                    # Handle both formats (with periods and without)
                    book = v.get('book', '').replace('.', '')
                    
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
        
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
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
        """Fallback regex parsing if JSON fails"""
        verses = []
        
        # Simple pattern to find references
        pattern = r'([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)(?:-(\d+))?'
        
        for match in re.finditer(pattern, text):
            book = match.group(1).strip()
            chapter = int(match.group(2))
            start = int(match.group(3))
            end = int(match.group(4)) if match.group(4) else None
            
            verses.append(VerseReference(
                book=book,
                chapter=chapter,
                start_verse=start,
                end_verse=end,
                original_text=match.group(0),
                confidence=0.85,
                pattern='llm_fallback'
            ))
        
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