"""
Test script to verify verse detection improvements
"""

import re
from typing import List, Dict

# Test content from B25ANCC02en.pdf
test_content = """
Scripture Reading: Rom. 5:1-11
I. Justification is God's action in approving us according to His standard of righteousness; the believers' righteousness is not a condition that they possess in themselves but a person to whom they are joined, the living Christ Himself:
A. When we believe into Christ, we receive God's forgiveness (Acts 10:43), and God can
justify us (Rom. 3:24, 26) by making Christ our righteousness and by clothing us with
Christ as our robe of righteousness (Isa. 61:10; Luke 15:22; Jer. 23:6; Zech. 3:4).
B. Life is the goal of God's salvation; thus, justification is "of life"; through justification we
have come up to the standard of God's righteousness and correspond with it so that
now He can impart His life into us—Rom. 5:18.
II. The result of our justification is the full enjoyment of God in Christ as our life—
vv. 1-11:
A. The result of our justification is embodied in six wonderful things—love (v. 5), grace
(v. 2), peace (v. 1), hope (v. 2), life (v. 10), and glory (v. 2)—for our enjoyment; these verses
also reveal the Triune God—the Holy Spirit (v. 5), Christ (v. 6), and God (v. 11)—for our
enjoyment.
B. Through the redeeming death of Christ, God has justified us sinners and has reconciled
us, His enemies, to Himself (vv. 1, 10-11); furthermore, "the love of God has been poured
out in our hearts through the Holy Spirit, who has been given to us" (v. 5):
1. Although we may be afflicted, poor, and depressed, we cannot deny the presence of
God's love within us; in order to stay on the line of life, which is Christ Himself (John
14:6a), we need to keep ourselves in the love of God (Jude 20-21), which is God Himself (1 John 4:8, 16).
2. We need to fan our God-given spirit of love into flame so that we can have a burning
spirit of love to overcome the degradation of today's church; to fan our spirit into
flame is to build up the habit of exercising our spirit continually so that we may
stay in contact with the Lord as the Spirit in our spirit—2 Tim. 1:6-7; 4:22.
"""

# Comprehensive regex patterns for verse detection
verse_patterns = [
    # Books with periods (e.g., Rom. 5:10; Isa. 61:10)
    r'([123]?\s*[A-Z][a-z]{1,}\.)[\s]+([\d]+):([\d]+(?:[-–][\d]+)?(?:,\s*[\d]+(?:[-–][\d]+)?)*)',
    # Books without periods (e.g., Romans 5:10)
    r'([123]?\s*[A-Z][a-z]+)\s+([\d]+):([\d]+(?:[-–][\d]+)?(?:,\s*[\d]+(?:[-–][\d]+)?)*)',
    # With "cf." prefix
    r'cf\.\s+([123]?\s*[A-Z][a-z]+\.?)\s+([\d]+):([\d]+(?:[-–][\d]+)?)',
    # Verse only references (v. 5 or vv. 5-10)
    r'v{1,2}\.\s*([\d]+(?:[-–][\d]+)?(?:,\s*[\d]+(?:[-–][\d]+)?)*)',
    # Multiple chapter:verse separated by semicolons (e.g., Rom. 5:10; 12:5)
    r'([123]?\s*[A-Z][a-z]+\.?)\s+([\d]+:[\d]+(?:[-–][\d]+)?(?:[,;]\s*[\d]+:[\d]+(?:[-–][\d]+)?)*)',
    # Books with chapter only (e.g., John 14)
    r'([123]?\s*[A-Z][a-z]+\.?)\s+([\d]+)(?!:)(?=\s|$|,|;|\.)',
    # Special formats with parentheses
    r'\(([123]?\s*[A-Z][a-z]+\.?)\s+([\d]+):([\d]+(?:[-–][\d]+)?)\)',
]

def test_detection():
    """Test verse detection on sample content"""
    lines = test_content.split('\n')
    all_matches = []
    
    for line_idx, line in enumerate(lines):
        for pattern in verse_patterns:
            for match in re.finditer(pattern, line):
                all_matches.append({
                    'line': line_idx + 1,
                    'text': match.group(0),
                    'line_content': line.strip()[:50] + '...' if len(line.strip()) > 50 else line.strip()
                })
    
    print(f"Total verse references found: {len(all_matches)}\n")
    print("Sample detections:")
    for i, match in enumerate(all_matches[:30]):  # Show first 30
        print(f"Line {match['line']:3}: {match['text']:20} | {match['line_content']}")
    
    # Count unique references
    unique_refs = set(m['text'] for m in all_matches)
    print(f"\nUnique references: {len(unique_refs)}")
    
    return len(all_matches)

if __name__ == "__main__":
    count = test_detection()
    print(f"\n✓ Detection complete: {count} verse references found")