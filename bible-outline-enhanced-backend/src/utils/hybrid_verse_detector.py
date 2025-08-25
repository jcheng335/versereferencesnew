"""
Hybrid Verse Detection System
Combines regex patterns, OpenAI LLM, and ML models for accurate verse detection and placement
"""

import os
import re
import json
import pickle
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from openai import OpenAI

# ML components are optional - system works with just regex + LLM
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    import pandas as pd
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML libraries not available - using regex + LLM only")
from datetime import datetime

@dataclass
class VerseReference:
    """Data class for verse references"""
    book: str
    chapter: int
    start_verse: int
    end_verse: int
    context: str
    confidence: float
    insertion_point: int
    original_text: str

class HybridVerseDetector:
    def __init__(self, openai_api_key: str = None, model_path: str = None):
        """
        Initialize the hybrid verse detector
        
        Args:
            openai_api_key: OpenAI API key for LLM validation (REQUIRED for hybrid approach)
            model_path: Path to trained ML model
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for hybrid verse detection. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        print("OpenAI LLM validation enabled for hybrid verse detection")
        
        self.model_path = model_path
        self.ml_model = None
        self.vectorizer = None
        
        # Load ML model if exists
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        # Comprehensive regex patterns for verse detection - ORDER MATTERS!
        self.verse_patterns = [
            # 1. Standalone verse references FIRST (v. 5 or vv. 5-10 or vv. 1, 10-11 or vv. 47-48)
            r'\bv{1,2}\.\s*(\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*)',
            
            # 2. Books with complex verse lists (Rom. 16:1, 4-5, 16, 20)
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+(?:,\s*\d+[-–]\d+)?(?:,\s*\d+)*)',
            
            # 3. Books with verse ranges and additional verses (Rom. 5:3-4, 11)
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+[-–]\d+(?:,\s*\d+)+)',
            
            # 4. Books with letters after verse (John 14:6a, 2 Cor. 4:6b)
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+[a-z])',
            
            # 5. Books with multiple verses separated by commas (1 John 4:8, 16)
            r'([123]?\s*[A-Z][a-z]+)\s+(\d+):(\d+(?:,\s*\d+)+)',
            
            # 6. Standard book:chapter:verse-verse (Rom. 5:1-11, Matt. 24:45-51)
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+[-–]\d+)',
            
            # 7. Standard book:chapter:verse (Rom. 5:10)
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+)',
            
            # 8. Books with chapter only (Luke 7)
            r'\b([123]?\s*[A-Z][a-z]+)\s+(\d+)(?![:])(?=[\s,;.\)–—]|$)',
            
            # 9. Special with parentheses (Acts 10:43)
            r'\(([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+(?:[-–]\d+)?(?:,\s*\d+)?)\)',
            
            # 10. Multiple references with semicolons (Isa. 61:10; Luke 15:22)
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+:\d+(?:[-–]\d+)?(?:[,;]\s*\d+:\d+(?:[-–]\d+)?)*)',
            
            # 11. With "cf." prefix
            r'cf\.\s+([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+(?:[-–]\d+)?)',
            
            # 12. Complex chapter:verse,verse format (Rev. 21:18, 23)
            r'([A-Z][a-z]+\.?)\s+(\d+):(\d+),\s*(\d+)(?!:)',
        ]
        
        # Book name variations
        self.book_variations = self._load_book_variations()
        
        # Training data storage
        self.training_data = []
        self.feedback_data = []
    
    def _load_book_variations(self) -> Dict[str, str]:
        """Load comprehensive book name variations for all 66 books"""
        return {
            # Old Testament (39 books)
            'Gen': 'Genesis', 'Genesis': 'Genesis', 'Ge': 'Genesis',
            'Exo': 'Exodus', 'Exodus': 'Exodus', 'Ex': 'Exodus', 'Exod': 'Exodus',
            'Lev': 'Leviticus', 'Leviticus': 'Leviticus', 'Le': 'Leviticus',
            'Num': 'Numbers', 'Numbers': 'Numbers', 'Nu': 'Numbers',
            'Deut': 'Deuteronomy', 'Deuteronomy': 'Deuteronomy', 'De': 'Deuteronomy', 'Deu': 'Deuteronomy', 'Dt': 'Deuteronomy',
            'Josh': 'Joshua', 'Joshua': 'Joshua', 'Jos': 'Joshua',
            'Judg': 'Judges', 'Judges': 'Judges', 'Jdg': 'Judges',
            'Ruth': 'Ruth', 'Ru': 'Ruth', 'Rut': 'Ruth',
            '1Sam': '1 Samuel', '1 Sam': '1 Samuel', '1 Samuel': '1 Samuel', '1Sa': '1 Samuel',
            '2Sam': '2 Samuel', '2 Sam': '2 Samuel', '2 Samuel': '2 Samuel', '2Sa': '2 Samuel',
            '1Kings': '1 Kings', '1 Kings': '1 Kings', '1Ki': '1 Kings', '1Kgs': '1 Kings',
            '2Kings': '2 Kings', '2 Kings': '2 Kings', '2Ki': '2 Kings', '2Kgs': '2 Kings',
            '1Chron': '1 Chronicles', '1 Chron': '1 Chronicles', '1 Chronicles': '1 Chronicles', '1Ch': '1 Chronicles',
            '2Chron': '2 Chronicles', '2 Chron': '2 Chronicles', '2 Chronicles': '2 Chronicles', '2Ch': '2 Chronicles',
            'Ezra': 'Ezra', 'Ezr': 'Ezra',
            'Neh': 'Nehemiah', 'Nehemiah': 'Nehemiah', 'Ne': 'Nehemiah',
            'Esth': 'Esther', 'Esther': 'Esther', 'Est': 'Esther',
            'Job': 'Job',
            'Psa': 'Psalms', 'Psalm': 'Psalms', 'Psalms': 'Psalms', 'Ps': 'Psalms',
            'Prov': 'Proverbs', 'Proverbs': 'Proverbs', 'Prv': 'Proverbs', 'Pro': 'Proverbs',
            'Eccl': 'Ecclesiastes', 'Ecclesiastes': 'Ecclesiastes', 'Ecc': 'Ecclesiastes',
            'Song': 'Song of Songs', 'Songs': 'Song of Songs', 'SoS': 'Song of Songs', 'SS': 'Song of Songs', 'S.S': 'Song of Songs',
            'Isa': 'Isaiah', 'Isaiah': 'Isaiah', 'Is': 'Isaiah',
            'Jer': 'Jeremiah', 'Jeremiah': 'Jeremiah', 'Je': 'Jeremiah',
            'Lam': 'Lamentations', 'Lamentations': 'Lamentations', 'La': 'Lamentations',
            'Ezek': 'Ezekiel', 'Ezekiel': 'Ezekiel', 'Eze': 'Ezekiel', 'Ezk': 'Ezekiel',
            'Dan': 'Daniel', 'Daniel': 'Daniel', 'Da': 'Daniel',
            'Hos': 'Hosea', 'Hosea': 'Hosea', 'Ho': 'Hosea',
            'Joel': 'Joel', 'Joe': 'Joel',
            'Amos': 'Amos', 'Am': 'Amos',
            'Obad': 'Obadiah', 'Obadiah': 'Obadiah', 'Oba': 'Obadiah',
            'Jonah': 'Jonah', 'Jon': 'Jonah',
            'Mic': 'Micah', 'Micah': 'Micah', 'Mi': 'Micah',
            'Nah': 'Nahum', 'Nahum': 'Nahum', 'Na': 'Nahum',
            'Hab': 'Habakkuk', 'Habakkuk': 'Habakkuk',
            'Zeph': 'Zephaniah', 'Zephaniah': 'Zephaniah', 'Zep': 'Zephaniah',
            'Hag': 'Haggai', 'Haggai': 'Haggai',
            'Zech': 'Zechariah', 'Zechariah': 'Zechariah', 'Zec': 'Zechariah',
            'Mal': 'Malachi', 'Malachi': 'Malachi',
            
            # New Testament (27 books)
            'Matt': 'Matthew', 'Matthew': 'Matthew', 'Mt': 'Matthew', 'Mat': 'Matthew',
            'Mark': 'Mark', 'Mk': 'Mark', 'Mr': 'Mark', 'Mrk': 'Mark',
            'Luke': 'Luke', 'Lk': 'Luke', 'Lu': 'Luke', 'Luk': 'Luke',
            'John': 'John', 'Jn': 'John', 'Joh': 'John',
            'Acts': 'Acts', 'Act': 'Acts', 'Ac': 'Acts',
            'Rom': 'Romans', 'Romans': 'Romans', 'Ro': 'Romans',
            '1Cor': '1 Corinthians', '1 Cor': '1 Corinthians', '1 Corinthians': '1 Corinthians', '1Co': '1 Corinthians',
            '2Cor': '2 Corinthians', '2 Cor': '2 Corinthians', '2 Corinthians': '2 Corinthians', '2Co': '2 Corinthians',
            'Gal': 'Galatians', 'Galatians': 'Galatians', 'Ga': 'Galatians',
            'Eph': 'Ephesians', 'Ephesians': 'Ephesians', 'Ephes': 'Ephesians',
            'Phil': 'Philippians', 'Philippians': 'Philippians', 'Php': 'Philippians', 'Phi': 'Philippians',
            'Col': 'Colossians', 'Colossians': 'Colossians',
            '1Thess': '1 Thessalonians', '1 Thess': '1 Thessalonians', '1 Thessalonians': '1 Thessalonians', '1Th': '1 Thessalonians', '1 Thes': '1 Thessalonians',
            '2Thess': '2 Thessalonians', '2 Thess': '2 Thessalonians', '2 Thessalonians': '2 Thessalonians', '2Th': '2 Thessalonians', '2 Thes': '2 Thessalonians',
            '1Tim': '1 Timothy', '1 Tim': '1 Timothy', '1 Timothy': '1 Timothy', '1Ti': '1 Timothy',
            '2Tim': '2 Timothy', '2 Tim': '2 Timothy', '2 Timothy': '2 Timothy', '2Ti': '2 Timothy',
            'Titus': 'Titus', 'Tit': 'Titus',
            'Philem': 'Philemon', 'Philemon': 'Philemon', 'Phm': 'Philemon', 'Phlm': 'Philemon',
            'Heb': 'Hebrews', 'Hebrews': 'Hebrews', 'He': 'Hebrews',
            'James': 'James', 'Jam': 'James', 'Jas': 'James',
            '1Pet': '1 Peter', '1 Pet': '1 Peter', '1 Peter': '1 Peter', '1Pe': '1 Peter',
            '2Pet': '2 Peter', '2 Pet': '2 Peter', '2 Peter': '2 Peter', '2Pe': '2 Peter',
            '1John': '1 John', '1 John': '1 John', '1Jn': '1 John', '1Jo': '1 John',
            '2John': '2 John', '2 John': '2 John', '2Jn': '2 John', '2Jo': '2 John',
            '3John': '3 John', '3 John': '3 John', '3Jn': '3 John', '3Jo': '3 John',
            'Jude': 'Jude', 'Jud': 'Jude',
            'Rev': 'Revelation', 'Revelation': 'Revelation', 'Re': 'Revelation', 'Rv': 'Revelation',
        }
    
    def detect_verses(self, text: str, use_llm: bool = True) -> List[VerseReference]:
        """
        Detect verse references using hybrid approach
        
        Args:
            text: Input text to analyze
            use_llm: Whether to use LLM for validation
        
        Returns:
            List of detected verse references
        """
        # Extract Scripture Reading context (e.g., "Scripture Reading: Rom. 5:1-11")
        scripture_context = self._extract_scripture_context(text)
        
        # Step 1: Regex-based initial detection
        candidates = self._regex_detection(text)
        
        # Resolve context for standalone v. and vv. references
        candidates = self._resolve_context_references(candidates, scripture_context)
        
        # Step 2: ML model scoring (if available)
        if ML_AVAILABLE and self.ml_model:
            candidates = self._ml_scoring(candidates, text)
        
        # Step 3: LLM validation and context understanding
        if use_llm and self.openai_client:
            candidates = self._llm_validation(candidates, text)
        
        # Step 4: Determine optimal insertion points
        references = self._determine_insertion_points(candidates, text)
        
        return references
    
    def _extract_scripture_context(self, text: str) -> Dict:
        """Extract the main Scripture Reading reference"""
        lines = text.split('\n')
        for line in lines:
            if 'Scripture Reading:' in line:
                # Extract the reference after "Scripture Reading:"
                ref_part = line.split('Scripture Reading:')[1].strip()
                # Parse it to get book and chapter
                match = re.match(r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+)', ref_part)
                if match:
                    return {
                        'book': match.group(1).strip(),
                        'chapter': int(match.group(2))
                    }
        return {'book': None, 'chapter': None}
    
    def _resolve_context_references(self, candidates: List[Dict], scripture_context: Dict) -> List[Dict]:
        """Resolve 'context' book references to actual book names"""
        for candidate in candidates:
            if candidate.get('book') == 'context' and scripture_context['book']:
                candidate['book'] = scripture_context['book']
                if candidate['chapter'] == 0:
                    candidate['chapter'] = scripture_context['chapter']
        return candidates
    
    def _regex_detection(self, text: str) -> List[Dict]:
        """Initial regex-based verse detection with complex reference parsing"""
        candidates = []
        lines = text.split('\n')
        seen_references = set()  # Track unique references per line
        
        for line_idx, line in enumerate(lines):
            line_references = set()  # Track references found on this line
            
            # Process each pattern
            for pattern in self.verse_patterns:
                for match in re.finditer(pattern, line):
                    match_text = match.group(0)
                    
                    # Skip if we've already found this exact reference on this line
                    ref_key = f"{line_idx}:{match_text}"
                    if ref_key in seen_references:
                        continue
                    seen_references.add(ref_key)
                    
                    # Parse complex references (e.g., "Rom. 5:10; 12:5; 16:1, 4-5, 16, 20")
                    parsed_refs = self._parse_complex_reference(match_text)
                    
                    for ref_data in parsed_refs:
                        # Create unique key for this specific reference
                        unique_key = f"{ref_data['book']}_{ref_data['chapter']}_{ref_data['start_verse']}_{ref_data['end_verse']}"
                        
                        # Skip if we've already added this exact reference for this line
                        if f"{line_idx}:{unique_key}" in line_references:
                            continue
                        line_references.add(f"{line_idx}:{unique_key}")
                        
                        candidate = {
                            'match': match,
                            'match_text': match_text,
                            'line_idx': line_idx,
                            'line': line,
                            'pattern': pattern,
                            'confidence': 0.5,  # Base confidence
                            'book': ref_data['book'],
                            'chapter': ref_data['chapter'],
                            'start_verse': ref_data['start_verse'],
                            'end_verse': ref_data['end_verse'],
                            'original_text': ref_data['original_text']
                        }
                        candidates.append(candidate)
        
        return candidates
    
    def _parse_complex_reference(self, ref_text: str) -> List[Dict]:
        """Parse complex verse references with multiple chapters/verses"""
        references = []
        
        # Clean the reference text
        ref_text = ref_text.strip()
        
        # Handle standalone verse references (v. or vv.)
        if ref_text.startswith('v.') or ref_text.startswith('vv.'):
            # These refer to the current book context (usually the Scripture Reading)
            verse_part = ref_text.replace('vv.', '').replace('v.', '').strip()
            
            # Parse verse ranges and lists
            if ',' in verse_part:
                # Handle vv. 1, 10-11 or vv. 47-48
                parts = verse_part.split(',')
                for part in parts:
                    part = part.strip()
                    if '-' in part or '–' in part:
                        range_parts = re.split(r'[-–]', part)
                        if len(range_parts) == 2:
                            start = int(range_parts[0].strip()) if range_parts[0].strip().isdigit() else 0
                            end = int(range_parts[1].strip()) if range_parts[1].strip().isdigit() else start
                            references.append({
                                'book': 'context',  # Will be resolved based on context
                                'chapter': 0,
                                'start_verse': start,
                                'end_verse': end,
                                'original_text': ref_text
                            })
                    elif part.isdigit():
                        verse = int(part)
                        references.append({
                            'book': 'context',
                            'chapter': 0,
                            'start_verse': verse,
                            'end_verse': verse,
                            'original_text': ref_text
                        })
            elif '-' in verse_part or '–' in verse_part:
                # Handle v. 5-10
                range_parts = re.split(r'[-–]', verse_part)
                if len(range_parts) == 2:
                    start = int(range_parts[0].strip()) if range_parts[0].strip().isdigit() else 0
                    end = int(range_parts[1].strip()) if range_parts[1].strip().isdigit() else start
                    references.append({
                        'book': 'context',
                        'chapter': 0,
                        'start_verse': start,
                        'end_verse': end,
                        'original_text': ref_text
                    })
            elif verse_part.isdigit():
                # Single verse
                verse = int(verse_part)
                references.append({
                    'book': 'context',
                    'chapter': 0,
                    'start_verse': verse,
                    'end_verse': verse,
                    'original_text': ref_text
                })
            
            return references
        
        # Extract book name (everything before first number)
        book_match = re.match(r'^([123]?\s*[A-Z][a-z]+\.?)\s*', ref_text)
        if not book_match:
            return references
        
        book = book_match.group(1).strip()
        remainder = ref_text[len(book_match.group(0)):]
        
        # Handle multiple references separated by semicolons
        # e.g., "5:10; 12:5; 16:1, 4-5, 16, 20"
        parts = remainder.split(';')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if this has a chapter:verse format
            if ':' in part:
                chapter_verse = part.split(':')
                if len(chapter_verse) == 2:
                    chapter = int(chapter_verse[0].strip()) if chapter_verse[0].strip().isdigit() else 0
                    verse_part = chapter_verse[1].strip()
                    
                    # Parse verse ranges and comma-separated verses
                    # e.g., "1, 4-5, 16, 20"
                    verse_segments = verse_part.split(',')
                    
                    for segment in verse_segments:
                        segment = segment.strip()
                        if not segment:
                            continue
                        
                        # Remove any trailing letters (e.g., "6b")
                        segment = re.sub(r'[a-z]+$', '', segment)
                        
                        # Check for verse range (e.g., "4-5")
                        if '-' in segment or '–' in segment:
                            verse_range = re.split(r'[-–]', segment)
                            if len(verse_range) == 2:
                                start = int(verse_range[0].strip()) if verse_range[0].strip().isdigit() else 0
                                end = int(verse_range[1].strip()) if verse_range[1].strip().isdigit() else start
                                references.append({
                                    'book': book,
                                    'chapter': chapter,
                                    'start_verse': start,
                                    'end_verse': end,
                                    'original_text': f"{book} {chapter}:{start}-{end}" if start != end else f"{book} {chapter}:{start}"
                                })
                        elif segment.isdigit():
                            # Single verse
                            verse = int(segment)
                            references.append({
                                'book': book,
                                'chapter': chapter,
                                'start_verse': verse,
                                'end_verse': verse,
                                'original_text': f"{book} {chapter}:{verse}"
                            })
            elif part.strip().isdigit():
                # Chapter only (e.g., "John 14")
                chapter = int(part.strip())
                references.append({
                    'book': book,
                    'chapter': chapter,
                    'start_verse': 0,
                    'end_verse': 0,
                    'original_text': f"{book} {chapter}"
                })
        
        # If no references were parsed, return the original as a single reference
        if not references:
            references.append({
                'book': book,
                'chapter': 0,
                'start_verse': 0,
                'end_verse': 0,
                'original_text': ref_text
            })
        
        return references
    
    def _ml_scoring(self, candidates: List[Dict], text: str) -> List[Dict]:
        """Score candidates using ML model"""
        if not ML_AVAILABLE or not self.ml_model or not candidates:
            return candidates
        
        # Extract features for each candidate
        features = []
        for candidate in candidates:
            feature_vec = self._extract_features(candidate, text)
            features.append(feature_vec)
        
        # Predict confidence scores
        if features:
            X = self.vectorizer.transform(features)
            scores = self.ml_model.predict_proba(X)[:, 1]  # Probability of being valid
            
            for i, candidate in enumerate(candidates):
                candidate['confidence'] = scores[i]
        
        return candidates
    
    def _llm_validation(self, candidates: List[Dict], text: str) -> List[Dict]:
        """Validate and enhance candidates using OpenAI LLM"""
        if not candidates:
            return candidates
        
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(candidates, text)
            
            # Call OpenAI API
            if not self.openai_client:
                print("OpenAI client not initialized")
                return candidates
                
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Bible verse reference expert analyzing sermon outlines. 
                        CRITICAL RULES:
                        1. Verses should be inserted on the SAME LINE as the outline point they reference
                        2. NEVER insert verses in the middle of a sentence
                        3. For outline points (I., II., A., B., 1., 2., etc.), place verses at the END of that outline point's text
                        4. If an outline point spans multiple lines, place the verse at the end of the LAST line of that point
                        5. Example: "II. A. The church is the Body of Christ" becomes "II. A. The church is the Body of Christ Eph 1:23 - verse text"
                        
                        Return JSON with:
                        - validated_references: array of {original_text, line_number, should_insert_at_line}
                        - The line_number where the verse appears and should_insert_at_line where it should be placed"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Parse LLM response
            llm_result = json.loads(response.choices[0].message.content)
            
            # Update candidates based on LLM feedback
            validated_candidates = self._process_llm_response(candidates, llm_result)
            
            return validated_candidates
            
        except Exception as e:
            print(f"LLM validation error: {e}")
            return candidates
    
    def _prepare_llm_context(self, candidates: List[Dict], text: str) -> str:
        """Prepare context for LLM analysis"""
        context = {
            "full_text": text,
            "detected_references": [
                {
                    "text": c['match'].group(0),
                    "line": c['line'],
                    "line_number": c['line_idx']
                }
                for c in candidates
            ],
            "instructions": "Validate these references and determine optimal insertion points"
        }
        return json.dumps(context)
    
    def _process_llm_response(self, candidates: List[Dict], llm_result: Dict) -> List[Dict]:
        """Process LLM response and update candidates"""
        validated = []
        
        for candidate in candidates:
            # Check if LLM validated this reference
            match_text = candidate['match'].group(0)
            
            for llm_ref in llm_result.get('validated_references', []):
                if llm_ref.get('original_text') == match_text:
                    candidate['confidence'] = llm_ref.get('confidence', 0.9)
                    candidate['insertion_line'] = llm_ref.get('insertion_line', candidate['line_idx'])
                    candidate['llm_validated'] = True
                    validated.append(candidate)
                    break
        
        return validated
    
    def _determine_insertion_points(self, candidates: List[Dict], text: str) -> List[VerseReference]:
        """Determine optimal insertion points for verses"""
        references = []
        lines = text.split('\n')
        
        for candidate in candidates:
            if candidate.get('confidence', 0) < 0.3:  # Skip low confidence
                continue
            
            line_idx = candidate['line_idx']
            
            # Find the line where this verse reference appears
            ref_line = lines[line_idx] if line_idx < len(lines) else ""
            
            # Determine where to insert the verse text
            # For margin format, keep it on the same line as the reference
            insertion_point = line_idx
            
            # Check if we need to find the end of an outline section
            if ref_line.strip():
                # Look backwards to find the start of this outline section
                outline_start = line_idx
                for i in range(line_idx - 1, -1, -1):
                    prev_line = lines[i].strip()
                    if re.match(r'^(?:[IVX]+\.|[A-Z]\.|[1-9]\d*\.|[a-z]\.)\s*', prev_line):
                        outline_start = i
                        break
                    if not prev_line:  # Empty line might indicate section break
                        break
                
                # For margin format, keep insertion at the line with the reference
                insertion_point = line_idx
            
            # Use pre-parsed book, chapter, verse information
            book = self._normalize_book_name(candidate.get('book', ''))
            
            if book:
                ref = VerseReference(
                    book=book,
                    chapter=candidate.get('chapter', 0),
                    start_verse=candidate.get('start_verse', 0),
                    end_verse=candidate.get('end_verse', candidate.get('start_verse', 0)),
                    context=candidate['line'],
                    confidence=candidate.get('confidence', 0.5),
                    insertion_point=insertion_point,
                    original_text=candidate.get('original_text', candidate.get('match_text', ''))
                )
                references.append(ref)
        
        return references
    
    def _find_sentence_end(self, lines: List[str], start_idx: int) -> int:
        """Find the end of a complete outline point, not just a sentence"""
        current_idx = start_idx
        current_line = lines[start_idx].strip() if start_idx < len(lines) else ""
        
        # Check if this line starts with an outline marker
        outline_pattern = r'^(?:[IVX]+\.|[A-Z]\.|[1-9]\d*\.|[a-z]\.)\s*'
        current_has_marker = bool(re.match(outline_pattern, current_line))
        
        # If this is an outline point, find where it ends
        if current_has_marker:
            # Look ahead to find the next outline marker or end of section
            test_idx = start_idx + 1
            while test_idx < len(lines):
                next_line = lines[test_idx].strip()
                
                # If we hit another outline marker, the previous line was the end
                if next_line and re.match(outline_pattern, next_line):
                    return test_idx - 1
                
                # If we hit a blank line followed by text, check if it's a new section
                if not next_line and test_idx + 1 < len(lines):
                    following_line = lines[test_idx + 1].strip()
                    if following_line and re.match(outline_pattern, following_line):
                        return test_idx - 1
                
                test_idx += 1
            
            # If we reached the end without finding another marker
            return len(lines) - 1
        
        # For non-outline lines, just return the same line
        return start_idx
    
    def _normalize_book_name(self, book_text: str) -> Optional[str]:
        """Normalize book name to standard form"""
        if not book_text:
            return None
        
        book_text = book_text.strip().replace('.', '')
        return self.book_variations.get(book_text, book_text)
    
    def _extract_features(self, candidate: Dict, full_text: str) -> str:
        """Extract features for ML model"""
        # Simple feature extraction - can be enhanced
        features = {
            'line_text': candidate['line'],
            'has_colon': ':' in candidate['line'],
            'has_dash': '-' in candidate['line'],
            'line_length': len(candidate['line']),
            'position_in_text': candidate['line_idx'] / len(full_text.split('\n')),
            'starts_with_outline': bool(re.match(r'^[A-Z]\.|^[IVX]+\.|^\d+\.', candidate['line'].strip()))
        }
        return ' '.join([f"{k}:{v}" for k, v in features.items()])
    
    def train_model(self, training_data: List[Dict]):
        """
        Train ML model on labeled data
        
        Args:
            training_data: List of dictionaries with 'text', 'references', and 'correct_placements'
        """
        if not ML_AVAILABLE:
            print("ML libraries not available - cannot train model")
            return
            
        if not training_data:
            print("No training data provided")
            return
        
        # Prepare training dataset
        X = []
        y = []
        
        for sample in training_data:
            text = sample['text']
            correct_refs = sample['correct_references']
            
            # Extract features from correct references
            for ref in correct_refs:
                features = self._extract_features({'line': ref['context'], 'line_idx': ref['line_idx']}, text)
                X.append(features)
                y.append(1)  # Correct reference
            
            # Add negative samples (incorrect references)
            if 'incorrect_references' in sample:
                for ref in sample['incorrect_references']:
                    features = self._extract_features({'line': ref['context'], 'line_idx': ref['line_idx']}, text)
                    X.append(features)
                    y.append(0)  # Incorrect reference
        
        # Vectorize features
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=100)
            X_vec = self.vectorizer.fit_transform(X)
            
            # Train Random Forest model
            self.ml_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.ml_model.fit(X_vec, y)
        else:
            print("ML libraries not available - cannot train model")
        
        # Save model
        self.save_model()
        
        print(f"Model trained on {len(training_data)} samples")
    
    def save_model(self, path: str = None):
        """Save trained model and vectorizer"""
        if not self.ml_model:
            print("No model to save")
            return
        
        save_path = path or self.model_path or 'verse_detector_model.pkl'
        
        model_data = {
            'model': self.ml_model,
            'vectorizer': self.vectorizer,
            'book_variations': self.book_variations,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {save_path}")
    
    def load_model(self, path: str):
        """Load trained model and vectorizer"""
        if not os.path.exists(path):
            print(f"Model file not found: {path}")
            return
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.ml_model = model_data.get('model')
        self.vectorizer = model_data.get('vectorizer')
        self.book_variations.update(model_data.get('book_variations', {}))
        
        print(f"Model loaded from {path}")
    
    def add_feedback(self, original_text: str, corrected_references: List[Dict]):
        """
        Add user feedback for continuous improvement
        
        Args:
            original_text: Original input text
            corrected_references: User-corrected reference placements
        """
        feedback = {
            'text': original_text,
            'timestamp': datetime.now().isoformat(),
            'corrected_references': corrected_references
        }
        
        self.feedback_data.append(feedback)
        
        # Auto-retrain if enough feedback collected
        if len(self.feedback_data) >= 10:
            self.retrain_with_feedback()
    
    def retrain_with_feedback(self):
        """Retrain model with accumulated feedback"""
        if not self.feedback_data:
            return
        
        # Convert feedback to training data format
        training_data = []
        for feedback in self.feedback_data:
            training_sample = {
                'text': feedback['text'],
                'correct_references': feedback['corrected_references']
            }
            training_data.append(training_sample)
        
        # Retrain model
        self.train_model(training_data)
        
        # Clear processed feedback
        self.feedback_data = []
        
        print(f"Model retrained with {len(training_data)} feedback samples")
    
    def export_training_data(self, path: str = 'training_data.json'):
        """Export training data for analysis or backup"""
        data = {
            'training_samples': self.training_data,
            'feedback_samples': self.feedback_data,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Training data exported to {path}")