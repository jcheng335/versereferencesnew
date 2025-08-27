#!/usr/bin/env python3
"""
Test the improved LLM prompt with sample text
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('bible-outline-enhanced-backend/.env')

sys.path.append('bible-outline-enhanced-backend/src')
from utils.pure_llm_detector import PureLLMDetector

def test_llm_prompt():
    """Test LLM prompt with W24ECT02 sample text"""
    
    # Sample text from W24ECT02en.pdf
    sample_text = """Message Two 
Christ as the Emancipator 
and as the One Who Makes Us More Than Conquerors 
Scripture Reading: Rom. 8:2, 31-39 
I. We can experience, enjoy, and express Christ as our Emancipator by the law of 
the Spirit of life—Rom. 8:2: 
A. The enjoyment of the law of the Spirit of life in Romans 8 ushers us into the reality of 
the Body of Christ in Romans 12; this law operates within us as we live in the Body 
and for the Body—8:2, 28-29; 12:1-2, 11; Phil. 1:19."""
    
    # Initialize detector
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set")
        return
    
    detector = PureLLMDetector(api_key)
    
    print("=== Testing Pure LLM Detector ===")
    print("Sample text length:", len(sample_text))
    
    # Test detection
    try:
        result = detector.detect_verses(sample_text)
        
        if isinstance(result, dict):
            print("\n=== METADATA EXTRACTED ===")
            metadata = result.get('metadata', {})
            print(f"Message Number: {metadata.get('message_number', 'NOT FOUND')}")
            print(f"Title: {metadata.get('title', 'NOT FOUND')}")
            print(f"Subtitle: {metadata.get('subtitle', 'NOT FOUND')}")
            
            print("\n=== OUTLINE STRUCTURE ===")
            for item in result.get('outline_structure', []):
                print(f"- {item.get('type')}: {item.get('number', '')} {item.get('text', '')}")
            
            print("\n=== VERSES DETECTED ===")
            verses = result.get('verses', [])
            print(f"Total verses: {len(verses)}")
            
            # Check for Scripture Reading verses
            scripture_verses = []
            for v in verses:
                if hasattr(v, 'context'):
                    context = v.context
                elif isinstance(v, dict):
                    context = v.get('context', '')
                else:
                    continue
                    
                if 'Scripture Reading' in context:
                    if hasattr(v, 'book'):
                        scripture_verses.append(f"{v.book} {v.chapter}:{v.start_verse}")
                    elif isinstance(v, dict):
                        scripture_verses.append(f"{v.get('book', '')} {v.get('chapter', '')}:{v.get('start_verse', '')}")
            
            print(f"Scripture Reading verses ({len(scripture_verses)}): {scripture_verses}")
            
            # Check for Rom. 8:31-39 expansion
            rom_8_verses = []
            for v in verses:
                if hasattr(v, 'book'):
                    if v.book == 'Romans' and v.chapter == 8 and v.start_verse >= 31:
                        rom_8_verses.append(v.start_verse)
                elif isinstance(v, dict):
                    if v.get('book') == 'Romans' and v.get('chapter') == 8 and v.get('start_verse', 0) >= 31:
                        rom_8_verses.append(v.get('start_verse'))
            
            rom_8_verses.sort()
            print(f"Romans 8:31-39 expansion: {rom_8_verses}")
            
            # Check success criteria
            print("\n=== SUCCESS CRITERIA ===")
            checks = {
                'Message Two extracted': metadata.get('message_number') == 'Message Two',
                'Title extracted': 'Emancipator' in metadata.get('title', ''),
                'Subtitle extracted': 'Conquerors' in metadata.get('subtitle', ''),
                'Scripture Reading found': any('scripture_reading' in str(item.get('type', '')).lower() for item in result.get('outline_structure', [])),
                'Rom. 8:2 detected': any('8' in str(v.get('chapter', 0)) and '2' in str(v.get('start_verse', 0)) for v in verses if isinstance(v, dict) and v.get('book') == 'Romans'),
                'Rom. 8:31-39 expanded': len(rom_8_verses) >= 9,
                'All verses 31-39 present': rom_8_verses == [31, 32, 33, 34, 35, 36, 37, 38, 39]
            }
            
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"{status} {check}")
                
        else:
            print("ERROR: Result is not a dict, got:", type(result))
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_prompt()