#!/usr/bin/env python3
"""Debug script to test LLM response and parsing"""

import os
import json
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path("bible-outline-enhanced-backend/.env")
if env_path.exists():
    load_dotenv(env_path)

# Load OpenAI API key
openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    print("Error: OPENAI_API_KEY not set")
    exit(1)

client = OpenAI(api_key=openai_key)

# Load test document
test_file = Path("original outlines/W24ECT12en.pdf")
if not test_file.exists():
    print(f"Test file not found: {test_file}")
    exit(1)

# Extract text from PDF
import pdfplumber
with pdfplumber.open(test_file) as pdf:
    text = ""
    for page in pdf.pages[:2]:  # Just first 2 pages for testing
        text += page.extract_text() + "\n"

print(f"Extracted {len(text)} characters from PDF")
print("\n=== SAMPLE TEXT ===")
print(text[:500])
print("\n==================")

# Build a simpler, more focused prompt
prompt = """Extract all Bible verse references from this text and return them as a JSON array. 
Each item should have: reference, book, chapter, start_verse, end_verse (if range).

Example output format:
[
  {"reference": "Eph. 4:7-16", "book": "Eph", "chapter": 4, "start_verse": 7, "end_verse": 16},
  {"reference": "Psalm 68:18", "book": "Psalm", "chapter": 68, "start_verse": 18, "end_verse": null}
]

Text to analyze:
""" + text[:3000]  # Limit text for testing

print("\n=== CALLING OPENAI API ===")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Bible verse reference extractor. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=2000
    )
    
    content = response.choices[0].message.content
    print(f"\n=== LLM RESPONSE ({len(content)} chars) ===")
    print(content[:1000])
    
    # Try to parse as JSON
    print("\n=== PARSING JSON ===")
    try:
        # Find JSON array in response
        start_idx = content.find('[')
        end_idx = content.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            verses = json.loads(json_str)
            print(f"Successfully parsed {len(verses)} verses!")
            
            # Display first 5 verses
            for i, v in enumerate(verses[:5]):
                print(f"{i+1}. {v.get('reference', 'N/A')} - {v.get('book', 'N/A')} {v.get('chapter', 0)}:{v.get('start_verse', 0)}")
        else:
            print("ERROR: No JSON array found in response")
            print("Response starts with:", content[:200])
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parsing failed: {e}")
        print("JSON string attempted:", json_str[:500] if 'json_str' in locals() else "N/A")
        
except Exception as e:
    print(f"ERROR calling OpenAI: {e}")
    import traceback
    traceback.print_exc()