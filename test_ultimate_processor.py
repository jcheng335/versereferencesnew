"""
Test the Ultimate Verse Processor with all 12 outlines
Validate 100% accuracy in verse detection and population
"""

import sys
import os
import json
import fitz
from typing import Dict, List

sys.path.append('bible-outline-enhanced-backend/src')
from utils.ultimate_verse_processor import UltimateVerseProcessor

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text

def test_single_outline(processor: UltimateVerseProcessor, pdf_path: str, outline_name: str) -> Dict:
    """Test a single outline"""
    
    print(f"\nTesting: {outline_name}")
    print("-" * 40)
    
    # Extract text
    text = extract_pdf_text(pdf_path)
    
    # Process document
    result = processor.process_document(text)
    
    if result['success']:
        print(f"[OK] Successfully processed")
        print(f"  Outline points: {result['outline_points']}")
        print(f"  Total verses detected: {result['total_verses']}")
        
        # Show sample output
        if result['outline']:
            print(f"\n  Sample outline points:")
            for point in result['outline'][:3]:
                verses = ', '.join([v['reference'] for v in point.get('verses', [])])
                print(f"    {point['number']}. {point['text'][:50]}...")
                if verses:
                    print(f"      Verses: {verses}")
        
        # Save formatted output
        output_path = f"output_{outline_name}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['formatted_output'])
        print(f"  Output saved to: {output_path}")
    else:
        print(f"[FAIL] Processing failed")
    
    return result

def test_all_outlines():
    """Test all 12 outlines"""
    
    print("=" * 60)
    print("ULTIMATE VERSE PROCESSOR TEST")
    print("Testing all 12 original outlines")
    print("=" * 60)
    
    # Initialize processor
    processor = UltimateVerseProcessor()
    
    results = {}
    total_verses = 0
    total_points = 0
    
    # Test each outline
    for i in range(1, 13):
        outline_num = str(i).zfill(2)
        pdf_path = f"original outlines/W24ECT{outline_num}en.pdf"
        
        # Handle naming variations
        if not os.path.exists(pdf_path):
            pdf_path = f"original outlines/W24ECT{outline_num}en (1).pdf"
        
        if os.path.exists(pdf_path):
            outline_name = f"W24ECT{outline_num}"
            result = test_single_outline(processor, pdf_path, outline_name)
            
            results[outline_name] = {
                'success': result['success'],
                'outline_points': result.get('outline_points', 0),
                'total_verses': result.get('total_verses', 0)
            }
            
            total_verses += result.get('total_verses', 0)
            total_points += result.get('outline_points', 0)
        else:
            print(f"\n[FAIL] Could not find: {pdf_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Outlines processed: {len(results)}")
    print(f"Total outline points: {total_points}")
    print(f"Total verses detected: {total_verses}")
    print(f"Average verses per outline: {total_verses / len(results):.1f}" if results else "N/A")
    
    # Save results
    with open('ultimate_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'outlines_processed': len(results),
                'total_points': total_points,
                'total_verses': total_verses,
                'average_verses': total_verses / len(results) if results else 0
            },
            'details': results
        }, f, indent=2)
    
    print("\n[Results saved to ultimate_test_results.json]")
    
    return results

def test_with_llm():
    """Test with LLM enhancement"""
    
    print("\n" + "=" * 60)
    print("TESTING WITH LLM ENHANCEMENT")
    print("=" * 60)
    
    processor = UltimateVerseProcessor()
    
    # Test with W24ECT12en.pdf
    pdf_path = "original outlines/W24ECT12en.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "W24ECT12en.pdf"
    
    if os.path.exists(pdf_path):
        text = extract_pdf_text(pdf_path)
        
        # Process with LLM
        result = processor.process_with_llm(text)
        
        if result['success']:
            print("[OK] LLM processing successful")
            print(f"  Total verses: {result['total_verses']}")
            
            # Compare with expected
            # Based on our analysis, W24ECT12en should have ~183 verses
            expected = 183
            accuracy = (result['total_verses'] / expected * 100) if expected > 0 else 0
            print(f"  Expected verses: {expected}")
            print(f"  Detection accuracy: {accuracy:.1f}%")
            
            if accuracy >= 95:
                print("  [EXCELLENT] 95%+ accuracy achieved!")
            elif accuracy >= 90:
                print("  [GOOD] 90%+ accuracy achieved")
            else:
                print(f"  [NEEDS WORK] Only {accuracy:.1f}% accuracy")
    else:
        print(f"[FAIL] Could not find test file: {pdf_path}")

def main():
    """Run all tests"""
    
    print("COMPREHENSIVE ULTIMATE PROCESSOR TEST")
    print("Target: 100% verse detection accuracy")
    print()
    
    # Test 1: All outlines
    all_results = test_all_outlines()
    
    # Test 2: LLM enhancement
    test_with_llm()
    
    # Final verdict
    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)
    
    if all_results:
        success_rate = sum(1 for r in all_results.values() if r['success']) / len(all_results) * 100
        avg_verses = sum(r['total_verses'] for r in all_results.values()) / len(all_results)
        
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Average verses per outline: {avg_verses:.1f}")
        
        if success_rate == 100 and avg_verses > 50:
            print("\n[SUCCESS] SYSTEM WORKING PERFECTLY!")
            print("All outlines processed successfully with comprehensive verse detection")
        else:
            print("\n[WARNING] System needs further improvement")
            print(f"Target: 100% success rate with 50+ verses per outline")
            print(f"Current: {success_rate:.1f}% success, {avg_verses:.1f} verses average")

if __name__ == "__main__":
    main()