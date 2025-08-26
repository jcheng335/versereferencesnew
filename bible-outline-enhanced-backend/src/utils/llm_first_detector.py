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
    
    def detect_verses(self, text: str, use_training: bool = True) -> List[VerseReference]:
        """Detect verses using LLM with training examples"""
        
        # Process in chunks if text is too long
        if len(text) > 3000:
            return self._detect_verses_chunked(text, use_training)
        
        prompt = self._build_prompt(text, use_training)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Use GPT-4 for best accuracy
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
        
        # Split text into chunks of ~2500 chars with overlap
        chunk_size = 2500
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            
            # Detect verses in this chunk
            chunk_verses = self.detect_verses(chunk, use_training=False)  # Avoid recursion
            
            # Add unique verses
            for v in chunk_verses:
                if v.original_text not in seen_refs:
                    seen_refs.add(v.original_text)
                    all_verses.append(v)
        
        print(f"Total verses from chunked processing: {len(all_verses)}")
        return all_verses
    
    def _build_prompt(self, text: str, use_training: bool) -> str:
        """Build the prompt for GPT"""
        
        training_section = ""
        if use_training and self.training_examples:
            training_section = f"""
Based on our training data from 12 complete outlines, here are examples of verses to find:
{self.training_examples}
"""
        
        return f"""Extract ALL Bible verse references from this outline text. 

CRITICAL INSTRUCTIONS:
1. Find EVERY verse reference - we need 100% detection
2. Include verses in ALL formats:
   - Scripture Reading (e.g., "Scripture Reading: Eph. 4:7-16; 6:10-20")
   - Parenthetical (e.g., "(Psalm 68:18)")
   - Inline references (e.g., "according to Acts 2:33")
   - Standalone verses (e.g., "v. 11" or "vv. 11-16") - resolve these using context
   - Complex lists (e.g., "1 Cor. 12:28; Eph. 4:11")
   - Cross references (e.g., "cf. Rom. 12:3")

{training_section}

For standalone verses like "v. 11", determine the book and chapter from:
1. The Scripture Reading at the beginning
2. Recent references in the same outline point
3. Context clues in surrounding text

Return a JSON array with this EXACT structure:
[
  {{
    "reference": "Eph. 4:7-16",
    "book": "Eph",
    "chapter": 4,
    "start_verse": 7,
    "end_verse": 16,
    "context": "Scripture Reading"
  }},
  {{
    "reference": "v. 11",
    "book": "Eph",
    "chapter": 4,
    "start_verse": 11,
    "end_verse": null,
    "context": "Resolved from Scripture Reading"
  }}
]

Text to analyze:
{text}

REMEMBER: Find ALL verses. Missing any is a failure."""
    
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