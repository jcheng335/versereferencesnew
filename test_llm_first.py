"""
Test the new LLM-first verse detection approach
"""

import sys
import os
sys.path.append('bible-outline-enhanced-backend/src')

from utils.llm_verse_detector import LLMVerseDetector

# Test content from B25ANCC02en.pdf (snippet with Luke 7 references)
test_content = """
Message Two
The Result of Our Justification—
the Full Enjoyment of God in Christ as Our Life
Scripture Reading: Rom. 5:1-11

II. The result of our justification is the full enjoyment of God in Christ as our life—
vv. 1-11:

C. "We have obtained access by faith into this grace in which we stand" (Rom. 5:2); since 
we have been justified by faith and stand in the realm of grace, "we have peace toward 
God through our Lord Jesus Christ" (v. 1):

1. Having peace "toward" God means that our journey into God through our being 
justified out of faith has not yet been completed, and we are still on the way into 
God; according to Luke 7, the Lord Jesus told the sinful woman, who "loved much" 
because she had been forgiven much (vv. 47-48) in order to be saved, to "go into peace" 
(v. 50, lit.).

2. Once we have passed through the gate of justification, we need to walk on the way 
of peace (Rom. 3:17); when we set our mind on the spirit—by caring for our spirit, 
using our spirit, paying attention to our spirit, contacting God by our spirit in com-
munion with the Spirit of God, and walking and living in our spirit—our mind becomes 
peace to give us an inner feeling of rest, release, brightness, and comfort (8:6).
"""

def test_llm_detection():
    """Test LLM-first detection"""
    print("Testing LLM-first verse detection...")
    print("=" * 80)
    
    detector = LLMVerseDetector()
    
    # Process the document
    result = detector.process_document(test_content)
    
    if result['success']:
        print(f"[SUCCESS] Successfully processed document")
        print(f"  Total verses found: {result['total_verses']}")
        print(f"  Verses with text: {result['verses_found']}")
        print(f"  Success rate: {result['success_rate']:.1f}%")
        
        print("\n" + "=" * 80)
        print("OUTLINE STRUCTURE WITH VERSES:")
        print("=" * 80)
        
        for point in result['outline_points']:
            print(f"\n{point['outline_number']}. {point['outline_text'][:80]}...")
            
            if point['verses']:
                print(f"  Verses: {', '.join([v['reference'] for v in point['verses']])}")
                
                # Show first verse text as sample
                first_verse = point['verses'][0]
                if first_verse.get('text') and first_verse['text'] != '[Verse text not found in database]':
                    print(f"  Sample: {first_verse['reference']}: {first_verse['text'][:100]}...")
        
        # Test margin formatting
        print("\n" + "=" * 80)
        print("MARGIN FORMAT OUTPUT:")
        print("=" * 80)
        
        formatted = detector.format_for_margin_display(result['outline_points'])
        print(formatted)
        
        # Check if Luke 7:47-48 and Luke 7:50 are detected
        all_refs = []
        for point in result['outline_points']:
            for verse in point['verses']:
                all_refs.append(verse['reference'])
        
        print("\n" + "=" * 80)
        print("VERIFICATION:")
        print("=" * 80)
        
        expected = ["Rom. 5:1-11", "Rom. 5:2", "Rom. 5:1", "Luke 7:47-48", "Luke 7:50", "Rom. 3:17", "Rom. 8:6"]
        found = []
        missing = []
        
        for ref in expected:
            if any(ref in r for r in all_refs):
                found.append(ref)
                print(f"[OK] Found: {ref}")
            else:
                missing.append(ref)
                print(f"[X] Missing: {ref}")
        
        print(f"\nDetection rate: {len(found)}/{len(expected)} ({len(found)/len(expected)*100:.1f}%)")
        
        if missing:
            print(f"Missing references: {', '.join(missing)}")
        
    else:
        print(f"[FAILED] {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_llm_detection()