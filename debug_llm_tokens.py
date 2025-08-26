"""
Debug script to check token length and analyze why LLM is missing content
"""
import os
import sys
import pdfplumber
from dotenv import load_dotenv
import json
import tiktoken

# Add the backend source to path
sys.path.append('bible-outline-enhanced-backend/src')

load_dotenv('bible-outline-enhanced-backend/.env')

def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def count_tokens(text):
    """Count tokens for GPT-3.5"""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def main():
    # Extract text from PDF
    pdf_path = 'W24ECT12en.pdf'
    if not os.path.exists(pdf_path):
        print(f"PDF file {pdf_path} not found")
        return
    
    text = extract_pdf_text(pdf_path)
    
    print(f"Full text length: {len(text)} characters")
    print(f"Token count: {count_tokens(text)} tokens")
    print("GPT-3.5-turbo context limit: 16,385 tokens")
    
    # Show the full text to see what might be missing
    print("\n=== FULL TEXT ===")
    print(text)
    print("\n=== END FULL TEXT ===")
    
    # Look for all major outline points
    import re
    major_points = re.findall(r'^[IVX]+\.', text, re.MULTILINE)
    print(f"\nMajor outline points found: {major_points}")
    
    # Look for sub-points
    sub_points = re.findall(r'^\s*[A-Z]\.', text, re.MULTILINE)
    print(f"Sub-points found: {sub_points}")
    
    # Look for numbered points
    numbered = re.findall(r'^\s*\d+\.', text, re.MULTILINE)
    print(f"Numbered points found: {numbered[:10]}...")  # Show first 10
    
    # Check if there's a "II." section
    if "II." in text:
        print("\n'II.' found in text - should be detected!")
        ii_index = text.find("II.")
        print(f"II. appears at character {ii_index}")
        print(f"Context around II.:\n{text[ii_index-100:ii_index+200]}")
    else:
        print("\n'II.' not found in text")

if __name__ == "__main__":
    main()