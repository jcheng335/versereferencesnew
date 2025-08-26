#!/usr/bin/env python3
"""Test the improved detection system locally"""

import sys
import os
sys.path.insert(0, 'bible-outline-enhanced-backend/src')

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path("bible-outline-enhanced-backend/.env")
if env_path.exists():
    load_dotenv(env_path)

from utils.llm_first_detector import LLMFirstDetector

# Test the detector
detector = LLMFirstDetector()

# Load test text
test_text = """
Message Twelve
The Giver of Gifts and the Constituents of God's Armor
Scripture Reading: Eph. 4:7-16; 6:10-20

I. Ephesians 4:7-16 presents to us Christ as the Giver of gifts for the intrinsic building
up of the organic Body of Christ; this building up is by the giving, the dispensing,
of the divine grace according to the measure of the gift of Christ:

A. Every member of the Body of Christ is an indispensable gift to the Body—v. 7; 1 Cor.
12:14-22; Rom. 12:4-5:
1. The gift of Christ is a person constituted of Christ (2 Cor. 1:15).
2. Each one of us is a measure of Christ, and we need all the measures to have
the immeasurable Christ—Eph. 4:16; cf. Rom. 12:3.

B. Christ ascended to the heavens like a victorious general leading a train of vanquished
foes, and He received gifts, which He has given to the churches—Eph. 4:8;
Psalm 68:18; cf. Num. 10:35.

C. The gifts in verse 11 are persons—the apostles, the prophets, the evangelists, and
the shepherds and teachers—given to the Body by the Head for the building up of
the Body, which is the organism of the Triune God.
"""

print("Testing improved LLM detector...")
print("=" * 60)

verses = detector.detect_verses(test_text)

print(f"Detected {len(verses)} verses:")
print("-" * 60)

for i, verse in enumerate(verses, 1):
    print(f"{i:2}. {verse.original_text:20} -> {verse.book} {verse.chapter}:{verse.start_verse}", end="")
    if verse.end_verse:
        print(f"-{verse.end_verse}", end="")
    print(f" (confidence: {verse.confidence:.2f})")

print("\n" + "=" * 60)
print("Test complete!")