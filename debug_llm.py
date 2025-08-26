"""
Debug script to test LLM verse detection directly
"""
import os
import sys
import pdfplumber
from dotenv import load_dotenv

# Add the backend source to path
sys.path.append('bible-outline-enhanced-backend/src')

load_dotenv('bible-outline-enhanced-backend/.env')

from utils.llm_verse_detector import LLMVerseDetector

def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def main():
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("No OPENAI_API_KEY found. Testing without LLM.")
        return
    
    print("Testing LLM verse detection...")
    
    # Extract text from PDF
    pdf_path = 'W24ECT12en.pdf'
    if not os.path.exists(pdf_path):
        print(f"PDF file {pdf_path} not found")
        return
    
    text = extract_pdf_text(pdf_path)
    print(f"Extracted text length: {len(text)} characters")
    print("First 500 characters:")
    print(text[:500])
    print("\n" + "="*50 + "\n")
    
    # Initialize LLM detector
    try:
        detector = LLMVerseDetector()
        
        # Process the document
        result = detector.process_document(text)
        
        print("LLM Processing Result:")
        print(f"Success: {result['success']}")
        print(f"Outline points found: {len(result.get('outline_points', []))}")
        print(f"Total references: {result.get('total_references', 0)}")
        print(f"Processing details: {result.get('processing_details', {})}")
        
        # Show first few outline points
        outline_points = result.get('outline_points', [])
        for i, point in enumerate(outline_points[:5]):
            print(f"\nPoint {i+1}:")
            print(f"  Outline: {point.get('outline_number', 'N/A')}")
            print(f"  Text: {point.get('outline_text', '')[:100]}...")
            print(f"  Verses: {point.get('verses', [])}")
        
        if len(outline_points) > 5:
            print(f"\n... and {len(outline_points) - 5} more points")
            
    except Exception as e:
        print(f"Error testing LLM detector: {e}")

if __name__ == "__main__":
    main()