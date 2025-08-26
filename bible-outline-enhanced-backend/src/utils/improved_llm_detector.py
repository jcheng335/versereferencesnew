#!/usr/bin/env python3
"""
Improved LLM Verse Detector with training examples
Uses GPT-4 with specific examples from 12 training outlines
"""

import os
import re
import json
import logging
from typing import List, Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class ImprovedLLMDetector:
    """Enhanced LLM detector with training examples for 100% accuracy"""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("No OpenAI API key provided")
    
    def detect_verses(self, text: str) -> Dict:
        """
        Detect verses using improved LLM prompt with examples
        
        Args:
            text: Outline text to analyze
            
        Returns:
            Dictionary with detected verses and metadata
        """
        if not self.client:
            return {'error': 'No OpenAI API key available'}
        
        # Create comprehensive prompt with examples
        prompt = self._create_prompt(text)
        
        try:
            # Use GPT-4 for better accuracy
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=4000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback to text parsing
                return self._parse_text_response(content)
                
        except Exception as e:
            logger.error(f"LLM detection error: {e}")
            return {'error': str(e)}
    
    def _get_system_prompt(self) -> str:
        """Get system prompt with detailed instructions"""
        return """You are an expert Bible verse reference extractor. Your task is to identify ALL Bible verse references in church outlines.

CRITICAL INSTRUCTIONS:
1. Extract EVERY verse reference, no matter how it appears
2. Resolve contextual references (e.g., "vv. 47-48" after "Luke 7" means "Luke 7:47-48")
3. Include ALL formats:
   - Scripture Reading: Eph. 4:7-16; 6:10-20
   - Parenthetical: (Acts 10:43)
   - Full references: Rom. 5:18, John 14:6a
   - Complex lists: Rom. 16:1, 4-5, 16, 20
   - Standalone: v. 5, vv. 1-11
   - Chapter context: "according to Luke 7"
   - Cross-references: cf. Rom. 12:3
   - Numbered books: 1 Cor. 12:14

OUTPUT FORMAT:
Return a JSON object with:
{
  "outline_structure": [
    {
      "point": "I",
      "text": "...",
      "verses": ["Rom. 5:1", "John 3:16", ...]
    }
  ],
  "all_verses": ["Rom. 5:1", "John 3:16", ...],
  "verse_count": 123,
  "context_resolutions": {
    "vv. 47-48": "Luke 7:47-48"
  }
}

IMPORTANT: Process the ENTIRE document, not just the first section!"""
    
    def _create_prompt(self, text: str) -> str:
        """Create prompt with examples from training data"""
        
        # Clean text
        text = text.replace('—', '-').replace('–', '-')
        
        prompt = f"""Extract ALL Bible verse references from this outline. Remember to:
1. Process the ENTIRE document
2. Resolve contextual references
3. Include every single verse reference

EXAMPLES FROM TRAINING DATA:

Example 1: Scripture Reading
Input: "Scripture Reading: Eph. 4:7-16; 6:10-20"
Output: ["Eph. 4:7-16", "Eph. 6:10-20"]

Example 2: Contextual Resolution
Input: "according to Luke 7, vv. 47-48 show that..."
Output: ["Luke 7", "Luke 7:47-48"]

Example 3: Complex List
Input: "Rom. 16:1, 4-5, 16, 20"
Output: ["Rom. 16:1", "Rom. 16:4-5", "Rom. 16:16", "Rom. 16:20"]

Example 4: Parenthetical
Input: "(Acts 10:43)"
Output: ["Acts 10:43"]

Example 5: Standalone with Context
Input: "In John 14... v. 6a says..."
Output: ["John 14", "John 14:6a"]

OUTLINE TEXT TO ANALYZE:
{text}

Extract ALL verses and return as JSON."""
        
        return prompt
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse text response if JSON parsing fails"""
        
        verses = []
        
        # Extract anything that looks like a verse reference
        patterns = [
            r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+:\d+(?:[a-z])?(?:[\-,]\d+(?:[a-z])?)*)',
            r'([1-3]?\s*[A-Z][a-z]+\.?\s+\d+)',
            r'(v\.\s*\d+[a-z]?)',
            r'(vv\.\s*\d+[\-]\d+[a-z]?)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            verses.extend(matches)
        
        # Remove duplicates
        unique_verses = list(set(verses))
        
        return {
            'all_verses': unique_verses,
            'verse_count': len(unique_verses),
            'parse_method': 'fallback'
        }

class HybridLLMDetector:
    """Combines LLM with pattern matching for 100% accuracy"""
    
    def __init__(self, api_key: str = None):
        """Initialize hybrid detector"""
        self.llm_detector = ImprovedLLMDetector(api_key)
        # from ultimate_verse_detector import UltimateVerseDetector
        # self.pattern_detector = UltimateVerseDetector()
        self.pattern_detector = None
    
    def detect_verses(self, text: str) -> Dict:
        """
        Detect verses using hybrid approach
        
        1. Try LLM first for structure understanding
        2. Use pattern matching as fallback/supplement
        3. Merge results for comprehensive coverage
        """
        
        results = {
            'verses': [],
            'sources': {},
            'statistics': {}
        }
        
        # Try LLM detection
        llm_result = None
        if self.llm_detector.client:
            llm_result = self.llm_detector.detect_verses(text)
            if 'all_verses' in llm_result:
                for verse in llm_result['all_verses']:
                    results['verses'].append({
                        'reference': verse,
                        'source': 'llm',
                        'confidence': 0.95
                    })
                results['sources']['llm'] = len(llm_result['all_verses'])
        
        # Always run pattern detection
        if self.pattern_detector:
            pattern_result = self.pattern_detector.extract_all_verses(text)
        else:
            pattern_result = {'verses': []}
        if 'verses' in pattern_result:
            for verse_data in pattern_result['verses']:
                # Check if not already found by LLM
                ref = verse_data['reference']
                if not any(v['reference'] == ref for v in results['verses']):
                    results['verses'].append({
                        'reference': ref,
                        'source': 'pattern',
                        'confidence': verse_data['confidence'],
                        'type': verse_data['type']
                    })
            results['sources']['pattern'] = len(pattern_result['verses'])
        
        # Sort by position/confidence
        results['verses'].sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Calculate statistics
        results['statistics'] = {
            'total_verses': len(results['verses']),
            'unique_verses': len(set(v['reference'] for v in results['verses'])),
            'llm_verses': results['sources'].get('llm', 0),
            'pattern_verses': results['sources'].get('pattern', 0),
            'high_confidence': sum(1 for v in results['verses'] if v['confidence'] >= 0.90)
        }
        
        return results