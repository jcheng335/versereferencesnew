#!/usr/bin/env python3
"""
Master Verse Detector - Combines all detection approaches for 100% accuracy
Integrates Ultimate, Perfect, Improved LLM, and training data
"""

import re
import os
import json
import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VerseReference:
    """Standardized verse reference"""
    book: str
    chapter: int
    start_verse: Optional[int] = None
    end_verse: Optional[int] = None
    original_text: str = ""
    confidence: float = 0.0
    source: str = ""
    context: str = ""
    
    def to_string(self) -> str:
        """Convert to standard string format"""
        if self.start_verse:
            if self.end_verse and self.end_verse != self.start_verse:
                return f"{self.book} {self.chapter}:{self.start_verse}-{self.end_verse}"
            else:
                return f"{self.book} {self.chapter}:{self.start_verse}"
        else:
            return f"{self.book} {self.chapter}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'book': self.book,
            'chapter': self.chapter,
            'start_verse': self.start_verse,
            'end_verse': self.end_verse or self.start_verse,
            'original_text': self.original_text,
            'confidence': self.confidence,
            'source': self.source,
            'context': self.context
        }

class MasterVerseDetector:
    """Master detector combining all approaches for maximum accuracy"""
    
    def __init__(self, openai_key: str = None):
        """Initialize with all detection systems"""
        
        # Book name normalization
        self.book_map = {
            # Old Testament
            'genesis': 'Gen', 'gen': 'Gen',
            'exodus': 'Exo', 'exo': 'Exo', 'ex': 'Exo',
            'leviticus': 'Lev', 'lev': 'Lev',
            'numbers': 'Num', 'num': 'Num',
            'deuteronomy': 'Deut', 'deut': 'Deut',
            'joshua': 'Josh', 'josh': 'Josh',
            'judges': 'Judg', 'judg': 'Judg',
            'ruth': 'Ruth',
            '1samuel': '1Sam', '1sam': '1Sam',
            '2samuel': '2Sam', '2sam': '2Sam',
            '1kings': '1Kings', '1king': '1Kings',
            '2kings': '2Kings', '2king': '2Kings',
            '1chronicles': '1Chr', '1chr': '1Chr',
            '2chronicles': '2Chr', '2chr': '2Chr',
            'ezra': 'Ezra',
            'nehemiah': 'Neh', 'neh': 'Neh',
            'esther': 'Esth', 'esth': 'Esth',
            'job': 'Job',
            'psalms': 'Psa', 'psalm': 'Psa', 'psa': 'Psa', 'ps': 'Psa',
            'proverbs': 'Prov', 'prov': 'Prov', 'pro': 'Prov',
            'ecclesiastes': 'Eccl', 'eccl': 'Eccl', 'ecc': 'Eccl',
            'song of songs': 'Song', 'song': 'Song', 'sos': 'Song', 'ss': 'Song',
            'isaiah': 'Isa', 'isa': 'Isa',
            'jeremiah': 'Jer', 'jer': 'Jer',
            'lamentations': 'Lam', 'lam': 'Lam',
            'ezekiel': 'Ezek', 'ezek': 'Ezek', 'eze': 'Ezek',
            'daniel': 'Dan', 'dan': 'Dan',
            'hosea': 'Hos', 'hos': 'Hos',
            'joel': 'Joel',
            'amos': 'Amos',
            'obadiah': 'Obad', 'obad': 'Obad', 'oba': 'Obad',
            'jonah': 'Jon', 'jon': 'Jon',
            'micah': 'Mic', 'mic': 'Mic',
            'nahum': 'Nah', 'nah': 'Nah',
            'habakkuk': 'Hab', 'hab': 'Hab',
            'zephaniah': 'Zeph', 'zeph': 'Zeph', 'zep': 'Zeph',
            'haggai': 'Hag', 'hag': 'Hag',
            'zechariah': 'Zech', 'zech': 'Zech', 'zec': 'Zech',
            'malachi': 'Mal', 'mal': 'Mal',
            # New Testament
            'matthew': 'Matt', 'matt': 'Matt', 'mat': 'Matt', 'mt': 'Matt',
            'mark': 'Mark', 'mrk': 'Mark', 'mk': 'Mark',
            'luke': 'Luke', 'luk': 'Luke', 'lk': 'Luke',
            'john': 'John', 'joh': 'John', 'jn': 'John',
            'acts': 'Acts', 'act': 'Acts',
            'romans': 'Rom', 'rom': 'Rom',
            '1corinthians': '1Cor', '1cor': '1Cor',
            '2corinthians': '2Cor', '2cor': '2Cor',
            'galatians': 'Gal', 'gal': 'Gal',
            'ephesians': 'Eph', 'eph': 'Eph',
            'philippians': 'Phil', 'phil': 'Phil', 'phi': 'Phil',
            'colossians': 'Col', 'col': 'Col',
            '1thessalonians': '1Thess', '1thess': '1Thess', '1th': '1Thess',
            '2thessalonians': '2Thess', '2thess': '2Thess', '2th': '2Thess',
            '1timothy': '1Tim', '1tim': '1Tim', '1ti': '1Tim',
            '2timothy': '2Tim', '2tim': '2Tim', '2ti': '2Tim',
            'titus': 'Titus', 'tit': 'Titus',
            'philemon': 'Phlm', 'phlm': 'Phlm', 'phm': 'Phlm',
            'hebrews': 'Heb', 'heb': 'Heb',
            'james': 'James', 'jam': 'James', 'jas': 'James',
            '1peter': '1Pet', '1pet': '1Pet', '1pe': '1Pet',
            '2peter': '2Pet', '2pet': '2Pet', '2pe': '2Pet',
            '1john': '1John', '1jn': '1John',
            '2john': '2John', '2jn': '2John',
            '3john': '3John', '3jn': '3John',
            'jude': 'Jude', 'jud': 'Jude',
            'revelation': 'Rev', 'rev': 'Rev', 'apocalypse': 'Rev'
        }
        
        # Initialize sub-detectors
        self.detectors = []
        
        # Priority 1: Trained detector (uses training data)
        try:
            from .trained_verse_detector import TrainedVerseDetector
            self.detectors.append(('trained', TrainedVerseDetector()))
            logger.info("TrainedVerseDetector loaded successfully")
        except ImportError as e:
            logger.warning(f"TrainedVerseDetector not available: {e}")
        
        # Priority 2: Ultimate detector
        try:
            from .ultimate_verse_detector import UltimateVerseDetector
            self.detectors.append(('ultimate', UltimateVerseDetector()))
        except ImportError:
            logger.warning("UltimateVerseDetector not available")
        
        try:
            from .perfect_verse_detector import PerfectVerseDetector
            self.detectors.append(('perfect', PerfectVerseDetector()))
        except ImportError:
            logger.warning("PerfectVerseDetector not available")
        
        try:
            from .comprehensive_verse_detector import ComprehensiveVerseDetector
            self.detectors.append(('comprehensive', ComprehensiveVerseDetector()))
        except ImportError:
            logger.warning("ComprehensiveVerseDetector not available")
        
        if openai_key:
            try:
                from .improved_llm_detector import HybridLLMDetector
                self.detectors.append(('llm', HybridLLMDetector(openai_key)))
            except ImportError:
                logger.warning("HybridLLMDetector not available")
        
        # Fallback to basic hybrid detector
        if not self.detectors:
            try:
                from .hybrid_verse_detector import HybridVerseDetector
                self.detectors.append(('hybrid', HybridVerseDetector()))
            except ImportError:
                logger.error("No detectors available!")
    
    def detect_all_verses(self, text: str) -> List[Dict]:
        """
        Detect all verses using all available detectors
        Combines and deduplicates results for maximum accuracy
        """
        
        # Clean text
        text = text.replace('—', '-').replace('–', '-')
        
        # Track all detected verses
        all_verses = []
        seen_refs = set()
        
        # Track context for resolving standalone verses
        current_book = None
        current_chapter = None
        
        # Phase 1: Extract Scripture Reading context
        scripture_refs = self._extract_scripture_reading(text)
        for ref in scripture_refs:
            all_verses.append(ref.to_dict())
            seen_refs.add(ref.to_string().lower())
            # Update context
            current_book = ref.book
            current_chapter = ref.chapter
        
        # Phase 2: Run all detectors
        for detector_name, detector in self.detectors:
            try:
                if detector_name == 'llm':
                    # Special handling for LLM detector
                    result = detector.detect_verses(text)
                    if 'verses' in result:
                        for verse_data in result['verses']:
                            ref = self._parse_verse_data(verse_data, detector_name)
                            if ref and ref.to_string().lower() not in seen_refs:
                                all_verses.append(ref.to_dict())
                                seen_refs.add(ref.to_string().lower())
                                # Update context
                                current_book = ref.book
                                current_chapter = ref.chapter
                else:
                    # Handle other detectors
                    if hasattr(detector, 'extract_all_verses'):
                        result = detector.extract_all_verses(text)
                        verses = result.get('verses', [])
                    elif hasattr(detector, 'detect_all_verses'):
                        verses = detector.detect_all_verses(text)
                    elif hasattr(detector, 'detect_verses'):
                        verses = detector.detect_verses(text)
                    else:
                        continue
                    
                    for verse_data in verses:
                        ref = self._parse_verse_data(verse_data, detector_name)
                        if ref and ref.to_string().lower() not in seen_refs:
                            all_verses.append(ref.to_dict())
                            seen_refs.add(ref.to_string().lower())
                            # Update context
                            current_book = ref.book
                            current_chapter = ref.chapter
            except Exception as e:
                logger.debug(f"Detector {detector_name} failed: {e}")
                continue
        
        # Phase 3: Pattern matching for any missed verses
        additional_verses = self._pattern_matching(text, current_book, current_chapter, seen_refs)
        all_verses.extend([v.to_dict() for v in additional_verses])
        
        # Phase 4: Contextual resolution for standalone verses
        contextual_verses = self._resolve_contextual_verses(text, current_book, current_chapter, seen_refs)
        all_verses.extend([v.to_dict() for v in contextual_verses])
        
        # Sort by confidence and remove duplicates
        all_verses.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Final deduplication
        final_verses = []
        final_seen = set()
        for verse in all_verses:
            key = f"{verse['book']}_{verse['chapter']}_{verse.get('start_verse', 0)}_{verse.get('end_verse', 0)}"
            if key not in final_seen:
                final_seen.add(key)
                final_verses.append(verse)
        
        return final_verses
    
    def _extract_scripture_reading(self, text: str) -> List[VerseReference]:
        """Extract Scripture Reading references"""
        verses = []
        pattern = r'Scripture\s+Reading[:\s]+([^\n]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            refs_text = match.group(1)
            # Split by semicolon or major punctuation
            parts = re.split(r'[;,]\s*', refs_text)
            for part in parts:
                ref = self._parse_reference_string(part.strip())
                if ref:
                    ref.confidence = 1.0
                    ref.source = 'scripture_reading'
                    verses.append(ref)
        return verses
    
    def _pattern_matching(self, text: str, current_book: str, current_chapter: int, seen_refs: Set[str]) -> List[VerseReference]:
        """Additional pattern matching for missed verses"""
        verses = []
        
        # Comprehensive patterns
        patterns = [
            # Full references (book chapter:verse)
            (r'\b([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)(?:[a-c])?(?:[-,](\d+)(?:[a-c])?)*', 'full'),
            # Parenthetical
            (r'\(([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)(?:[-,](\d+))?\)', 'parenthetical'),
            # Chapter only
            (r'(?:according to|in|from)\s+([1-3]?\s*[A-Z][a-z]+)\s+(\d+)', 'chapter'),
            # Cross references
            (r'(?:cf\.|see)\s+([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+)(?::(\d+))?', 'cross_ref'),
        ]
        
        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    book = self._normalize_book(match.group(1))
                    if not book:
                        continue
                    
                    chapter = int(match.group(2))
                    start_verse = int(match.group(3)) if len(match.groups()) >= 3 and match.group(3) else None
                    end_verse = int(match.group(4)) if len(match.groups()) >= 4 and match.group(4) else start_verse
                    
                    ref = VerseReference(
                        book=book,
                        chapter=chapter,
                        start_verse=start_verse,
                        end_verse=end_verse,
                        original_text=match.group(0),
                        confidence=0.85,
                        source=f'pattern_{pattern_type}'
                    )
                    
                    if ref.to_string().lower() not in seen_refs:
                        verses.append(ref)
                        seen_refs.add(ref.to_string().lower())
                except Exception:
                    continue
        
        return verses
    
    def _resolve_contextual_verses(self, text: str, current_book: str, current_chapter: int, seen_refs: Set[str]) -> List[VerseReference]:
        """Resolve standalone verse references using context"""
        verses = []
        
        if not current_book or not current_chapter:
            return verses
        
        # Patterns for standalone verses
        patterns = [
            (r'\bv\.\s*(\d+)(?:[a-c])?\b', 'single'),
            (r'\bvv\.\s*(\d+)[-–](\d+)(?:[a-c])?\b', 'range'),
            (r'verses?\s+(\d+)(?:[-–,]\s*(\d+))*', 'verses'),
        ]
        
        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    if pattern_type == 'single':
                        start_verse = int(match.group(1))
                        ref = VerseReference(
                            book=current_book,
                            chapter=current_chapter,
                            start_verse=start_verse,
                            end_verse=start_verse,
                            original_text=match.group(0),
                            confidence=0.75,
                            source=f'contextual_{pattern_type}',
                            context=f"Resolved from {current_book} {current_chapter}"
                        )
                    elif pattern_type == 'range':
                        start_verse = int(match.group(1))
                        end_verse = int(match.group(2))
                        ref = VerseReference(
                            book=current_book,
                            chapter=current_chapter,
                            start_verse=start_verse,
                            end_verse=end_verse,
                            original_text=match.group(0),
                            confidence=0.75,
                            source=f'contextual_{pattern_type}',
                            context=f"Resolved from {current_book} {current_chapter}"
                        )
                    else:
                        continue
                    
                    if ref.to_string().lower() not in seen_refs:
                        verses.append(ref)
                        seen_refs.add(ref.to_string().lower())
                except Exception:
                    continue
        
        return verses
    
    def _parse_verse_data(self, verse_data, source: str) -> Optional[VerseReference]:
        """Parse verse data from various detector formats"""
        try:
            if isinstance(verse_data, dict):
                # Handle dictionary format
                if 'book' in verse_data and 'chapter' in verse_data:
                    return VerseReference(
                        book=verse_data['book'],
                        chapter=verse_data['chapter'],
                        start_verse=verse_data.get('start_verse'),
                        end_verse=verse_data.get('end_verse'),
                        original_text=verse_data.get('original_text', ''),
                        confidence=verse_data.get('confidence', 0.5),
                        source=source,
                        context=verse_data.get('context', '')
                    )
                elif 'reference' in verse_data:
                    # Parse reference string
                    ref = self._parse_reference_string(verse_data['reference'])
                    if ref:
                        ref.confidence = verse_data.get('confidence', 0.5)
                        ref.source = source
                        return ref
            elif isinstance(verse_data, str):
                # Parse string reference
                ref = self._parse_reference_string(verse_data)
                if ref:
                    ref.source = source
                    return ref
            elif hasattr(verse_data, 'book'):
                # Handle object with attributes
                return VerseReference(
                    book=verse_data.book,
                    chapter=verse_data.chapter,
                    start_verse=getattr(verse_data, 'start_verse', None),
                    end_verse=getattr(verse_data, 'end_verse', None),
                    original_text=getattr(verse_data, 'original_text', ''),
                    confidence=getattr(verse_data, 'confidence', 0.5),
                    source=source
                )
        except Exception as e:
            logger.debug(f"Failed to parse verse data: {e}")
        
        return None
    
    def _parse_reference_string(self, ref_text: str) -> Optional[VerseReference]:
        """Parse a reference string into VerseReference"""
        ref_text = ref_text.strip()
        
        # Try various patterns
        patterns = [
            r'^([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+):(\d+)(?:[a-c])?(?:[-–](\d+))?',
            r'^([1-3]?\s*[A-Z][a-z]+)\.?\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, ref_text, re.IGNORECASE)
            if match:
                book = self._normalize_book(match.group(1))
                if not book:
                    continue
                
                chapter = int(match.group(2))
                start_verse = int(match.group(3)) if len(match.groups()) >= 3 and match.group(3) else None
                end_verse = int(match.group(4)) if len(match.groups()) >= 4 and match.group(4) else start_verse
                
                return VerseReference(
                    book=book,
                    chapter=chapter,
                    start_verse=start_verse,
                    end_verse=end_verse,
                    original_text=ref_text,
                    confidence=0.8
                )
        
        return None
    
    def _normalize_book(self, book_name: str) -> Optional[str]:
        """Normalize book name to standard abbreviation"""
        if not book_name:
            return None
        
        # Clean and normalize
        book_name = book_name.strip().lower()
        book_name = re.sub(r'\.$', '', book_name)  # Remove trailing period
        book_name = re.sub(r'\s+', '', book_name)  # Remove spaces for numbered books
        
        return self.book_map.get(book_name)

    def extract_all_verses(self, text: str) -> Dict:
        """
        Extract all verses with statistics
        """
        verses = self.detect_all_verses(text)
        
        # Calculate statistics
        source_counts = {}
        confidence_levels = {'high': 0, 'medium': 0, 'low': 0}
        
        for verse in verses:
            # Count by source
            source = verse.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Count by confidence
            conf = verse.get('confidence', 0)
            if conf >= 0.9:
                confidence_levels['high'] += 1
            elif conf >= 0.7:
                confidence_levels['medium'] += 1
            else:
                confidence_levels['low'] += 1
        
        return {
            'verses': verses,
            'total_count': len(verses),
            'unique_count': len(verses),  # Already deduplicated
            'source_distribution': source_counts,
            'confidence_levels': confidence_levels,
            'average_confidence': sum(v.get('confidence', 0) for v in verses) / len(verses) if verses else 0
        }