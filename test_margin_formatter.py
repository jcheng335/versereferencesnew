#!/usr/bin/env python3
"""
Test the margin formatter with sample structured data
"""

import sys
sys.path.append('bible-outline-enhanced-backend/src')

from utils.margin_formatter import MarginFormatter

def test_margin_formatter():
    """Test margin formatter with sample data"""
    
    formatter = MarginFormatter()
    
    # Sample structured data mimicking pure_llm_detector output
    structured_data = {
        'metadata': {
            'message_number': 'Message Two',
            'title': 'Christ as the Emancipator',
            'subtitle': 'and as the One Who Makes Us More Than Conquerors',
            'hymns': '540, 784'
        },
        'outline_structure': [
            {'type': 'scripture_reading', 'text': 'Rom. 8:2, 31-39'},
            {'type': 'outline', 'number': 'I', 'text': 'We can experience Christ as the Emancipator', 'verses': []},
            {'type': 'outline', 'number': 'A', 'text': 'The enjoyment of Christ makes us more than conquerors', 'verses': []}
        ],
        'verses': [
            {'original_text': 'Rom. 8:2', 'book': 'Romans', 'chapter': 8, 'start_verse': 2},
            {'original_text': 'Rom. 8:31', 'book': 'Romans', 'chapter': 8, 'start_verse': 31},
            {'original_text': 'Rom. 8:32', 'book': 'Romans', 'chapter': 8, 'start_verse': 32}
        ]
    }
    
    # Format the HTML
    html_output = formatter.format_html(structured_data)
    
    # Save output for inspection
    with open('test_margin_formatter_output.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print("HTML output saved to test_margin_formatter_output.html")
    
    # Check for key elements
    checks = {
        'Message Two': 'Message Two' in html_output,
        'Christ as the Emancipator': 'Christ as the Emancipator' in html_output,
        'Scripture Reading': 'Scripture Reading' in html_output,
        'Rom. 8:2': 'Rom. 8:2' in html_output,
        'blue color': 'color: blue' in html_output,
        'Roman numeral I': 'I.' in html_output,
        '<body> has content': '<body>' in html_output and '</body>' in html_output and len(html_output) > 1000
    }
    
    print("\n=== CHECK RESULTS ===")
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}")
    
    # Show a snippet of the HTML
    print("\n=== HTML BODY SNIPPET ===")
    body_start = html_output.find('<body>') + 6
    body_end = html_output.find('</body>')
    body_content = html_output[body_start:body_end].strip()
    print(body_content[:500] if body_content else "[EMPTY BODY]")

if __name__ == "__main__":
    test_margin_formatter()