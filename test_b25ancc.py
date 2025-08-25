"""
Test the enhanced API with B25ANCC02en.pdf content
"""

import requests
import json
import pdfplumber

# API base URL
API_URL = "http://localhost:5004/api/enhanced"

def test_actual_pdf():
    """Test with actual B25ANCC02en.pdf file"""
    pdf_path = "B25ANCC02en.pdf"
    
    # Extract text from PDF
    print(f"Extracting text from {pdf_path}...")
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return
    
    print(f"Extracted {len(text)} characters from PDF")
    
    # Write to temp file for upload
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        temp_file = f.name
    
    try:
        # Upload the file
        print("\nUploading to API...")
        with open(temp_file, 'rb') as f:
            files = {'file': ('b25ancc02en.txt', f, 'text/plain')}
            data = {'use_llm': 'true'}
            
            response = requests.post(f"{API_URL}/upload", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"\n[SUCCESS] Upload successful!")
                print(f"Session ID: {result.get('session_id')}")
                print(f"References found: {result.get('references_found', 0)}")
                print(f"Total verses: {result.get('total_verses', 0)}")
                print(f"Average confidence: {result.get('average_confidence', 0):.2f}")
                
                # Expected: 58 unique references, 106 total verses
                print(f"\nExpected: 58 unique references, 106 total verses")
                print(f"Actual: {result.get('references_found', 0)} references, {result.get('total_verses', 0)} verses")
                
                if result.get('references_found', 0) < 58:
                    print(f"\n[WARNING] Missing {58 - result.get('references_found', 0)} references!")
                
                # Test populate verses
                if result.get('session_id'):
                    test_populate(result['session_id'])
                
                return result
            else:
                print(f"[ERROR] {result.get('error', 'Unknown error')}")
        else:
            print(f"[FAILED] Upload failed: {response.status_code}")
            print(response.text)
            
    finally:
        # Clean up temp file
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_populate(session_id):
    """Test populating verses"""
    print(f"\nPopulating verses for session {session_id}...")
    
    response = requests.post(
        f"{API_URL}/populate/{session_id}",
        json={'format': 'margin'}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"[SUCCESS] Populate successful!")
            print(f"Format: {result.get('format')}")
            print(f"Verse count: {result.get('verse_count')}")
            print(f"Message: {result.get('message')}")
            
            # Show a sample of the populated content
            content = result.get('populated_content', '')
            lines = content.split('\n')[:20]  # First 20 lines
            print("\nSample output (first 20 lines):")
            for line in lines:
                if line.strip():
                    print(line[:100] + '...' if len(line) > 100 else line)
        else:
            print(f"[ERROR] {result.get('error', 'Unknown error')}")
    else:
        print(f"[FAILED] Populate failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_actual_pdf()