import re

text = "Test document with John 3:16 and Genesis 1:1"
full_ref_pattern = r'(?:cf\.\s+)?([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?'

matches = list(re.finditer(full_ref_pattern, text))
print(f"Text: {text}")
print(f"Pattern: {full_ref_pattern}")
print(f"Matches found: {len(matches)}")

for match in matches:
    print(f"Match: {match.group()}")
    print(f"Groups: {match.groups()}")