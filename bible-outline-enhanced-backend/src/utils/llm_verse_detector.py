"""
LLM-first verse detection system
Uses OpenAI to understand outline structure and extract verse references
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import sqlite3

load_dotenv()

class LLMVerseDetector:
    def __init__(self):
        """Initialize the LLM-based verse detector"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required in .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bible_verses.db')
    
    def extract_outline_with_verses(self, text: str) -> List[Dict]:
        """
        Use LLM to extract outline points and their verse references
        """
        system_prompt = """You are a Bible outline analyzer. Your task is to analyze church message outlines and extract:
1. Each outline point (main points, sub-points, sub-sub-points)
2. ALL Bible verse references associated with each point

IMPORTANT RULES:
- Extract EVERY verse reference, including:
  - Full references like "Rom. 5:1-11", "John 3:16"
  - Contextual references like "v. 5", "vv. 1-11" (resolve using Scripture Reading context)
  - References in parentheses like "(Acts 10:43)"
  - Multiple references like "Rom. 3:24, 26" or "Isa. 61:10; Luke 15:22"
- When you see "according to Luke 7" followed later by "vv. 47-48", resolve it to "Luke 7:47-48"
- Preserve the exact outline structure and hierarchy

Return a JSON array where each element has:
{
  "outline_number": "I.A.1" (or "I", "II.B", etc),
  "outline_text": "The actual outline point text",
  "verses": ["Rom. 5:1", "John 3:16", ...] (list of all verse references for this point)
}

Be thorough - missing even one verse reference is a failure."""

        user_prompt = f"""Extract all outline points and verse references from this text:

{text}

Remember to:
1. Include ALL verse references (explicit and contextual)
2. Resolve v./vv. references using the Scripture Reading context
3. Split combined references (e.g., "Rom. 3:24, 26" becomes ["Rom. 3:24", "Rom. 3:26"])"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure we have the right structure
            if isinstance(result, dict) and 'outline' in result:
                return result['outline']
            elif isinstance(result, list):
                return result
            else:
                # Try to extract outline array from various possible structures
                for key in ['points', 'outline_points', 'data']:
                    if key in result and isinstance(result[key], list):
                        return result[key]
                
                # If still no luck, wrap in array
                return [result] if isinstance(result, dict) else []
                
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return []
    
    def normalize_reference(self, ref: str) -> str:
        """Normalize a verse reference for database lookup"""
        # Remove extra spaces and standardize book abbreviations
        ref = ref.strip()
        
        # Handle special cases
        ref = ref.replace('1 John', '1John')
        ref = ref.replace('2 Tim.', '2Tim')
        ref = ref.replace('1 Thes.', '1Thess')
        ref = ref.replace('2 Cor.', '2Cor')
        ref = ref.replace('1 Pet.', '1Pet')
        ref = ref.replace('2 Pet.', '2Pet')
        
        # Remove periods after book names
        ref = re.sub(r'([A-Za-z])\.(\s+\d)', r'\1\2', ref)
        
        return ref
    
    def lookup_verse_text(self, reference: str) -> Optional[str]:
        """Look up verse text from the database"""
        try:
            normalized = self.normalize_reference(reference)
            
            # Parse the reference
            match = re.match(r'([123]?[A-Za-z]+)\s+(\d+):(\d+(?:[-,]\d+)*)', normalized)
            if not match:
                return None
            
            book = match.group(1)
            chapter = int(match.group(2))
            verses_part = match.group(3)
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            verse_texts = []
            
            # Handle verse ranges and lists
            if '-' in verses_part:
                # Range like 1-11
                parts = verses_part.split('-')
                start_verse = int(parts[0])
                end_verse = int(parts[1])
                
                for verse_num in range(start_verse, end_verse + 1):
                    cursor.execute("""
                        SELECT verse_text FROM verses 
                        WHERE book = ? AND chapter = ? AND verse = ?
                    """, (book, chapter, verse_num))
                    result = cursor.fetchone()
                    if result:
                        verse_texts.append(f"{verse_num}. {result[0]}")
            
            elif ',' in verses_part:
                # List like 1,10,11 or 1,4-5,16,20
                parts = verses_part.split(',')
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # Sub-range
                        subparts = part.split('-')
                        start = int(subparts[0])
                        end = int(subparts[1])
                        for v in range(start, end + 1):
                            cursor.execute("""
                                SELECT verse_text FROM verses 
                                WHERE book = ? AND chapter = ? AND verse = ?
                            """, (book, chapter, v))
                            result = cursor.fetchone()
                            if result:
                                verse_texts.append(f"{v}. {result[0]}")
                    else:
                        # Single verse
                        verse_num = int(part)
                        cursor.execute("""
                            SELECT verse_text FROM verses 
                            WHERE book = ? AND chapter = ? AND verse = ?
                        """, (book, chapter, verse_num))
                        result = cursor.fetchone()
                        if result:
                            verse_texts.append(f"{verse_num}. {result[0]}")
            else:
                # Single verse
                verse_num = int(verses_part)
                cursor.execute("""
                    SELECT text FROM bible_verses 
                    WHERE book = ? AND chapter = ? AND verse_number = ?
                """, (book, chapter, verse_num))
                result = cursor.fetchone()
                if result:
                    verse_texts.append(result[0])
            
            conn.close()
            
            if verse_texts:
                return ' '.join(verse_texts)
            
            return None
            
        except Exception as e:
            print(f"Database lookup error for {reference}: {e}")
            return None
    
    def process_document(self, text: str) -> Dict:
        """
        Process a document using LLM-first approach
        Returns outline points with verse references and text
        """
        # Step 1: Extract outline structure with verse references using LLM
        outline_points = self.extract_outline_with_verses(text)
        
        if not outline_points:
            return {
                'success': False,
                'error': 'Failed to extract outline structure',
                'outline_points': []
            }
        
        # Step 2: Look up verse texts from database
        enriched_points = []
        total_verses = 0
        verses_found = 0
        
        for point in outline_points:
            enriched_point = {
                'outline_number': point.get('outline_number', ''),
                'outline_text': point.get('outline_text', ''),
                'verses': []
            }
            
            for verse_ref in point.get('verses', []):
                total_verses += 1
                verse_text = self.lookup_verse_text(verse_ref)
                
                verse_data = {
                    'reference': verse_ref,
                    'text': verse_text or '[Verse text not found in database]'
                }
                
                if verse_text:
                    verses_found += 1
                
                enriched_point['verses'].append(verse_data)
            
            enriched_points.append(enriched_point)
        
        return {
            'success': True,
            'outline_points': enriched_points,
            'total_verses': total_verses,
            'verses_found': verses_found,
            'success_rate': (verses_found / total_verses * 100) if total_verses > 0 else 0
        }
    
    def format_for_margin_display(self, outline_points: List[Dict]) -> str:
        """
        Format the outline with verses in margin format
        Similar to MSG12VerseReferences.pdf
        """
        lines = []
        
        for point in outline_points:
            # Format verse references for margin
            if point['verses']:
                refs = ', '.join([v['reference'] for v in point['verses']])
                # Left column for references (15 chars), right column for outline text
                formatted_line = f"{refs:<15} {point['outline_number']}. {point['outline_text']}"
            else:
                formatted_line = f"{'':15} {point['outline_number']}. {point['outline_text']}"
            
            lines.append(formatted_line)
            
            # Optionally add verse texts below (commented out for margin format)
            # for verse in point['verses']:
            #     lines.append(f"{'':17} {verse['reference']}: {verse['text'][:80]}...")
        
        return '\n'.join(lines)