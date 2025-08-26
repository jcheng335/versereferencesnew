"""
Debug script to see raw LLM response
"""
import os
import sys
import pdfplumber
from dotenv import load_dotenv
import json

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
    
    print("Testing raw LLM response...")
    
    # Extract text from PDF
    pdf_path = 'W24ECT12en.pdf'
    if not os.path.exists(pdf_path):
        print(f"PDF file {pdf_path} not found")
        return
    
    text = extract_pdf_text(pdf_path)
    
    # Initialize LLM detector and call the raw extraction method
    try:
        detector = LLMVerseDetector()
        
        # Call the raw outline extraction to see what LLM returns
        outline_points = detector.extract_outline_with_verses(text)
        
        print(f"Raw LLM returned {len(outline_points)} outline points:")
        print(json.dumps(outline_points, indent=2))
        
    except Exception as e:
        print(f"Error testing LLM detector: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()