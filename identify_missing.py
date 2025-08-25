"""
Identify which verses are missing from detection
"""

# All 58 unique references from manual count
all_expected = [
    "Rom. 5:1-11",  # Scripture Reading
    
    # Section I.A
    "Acts 10:43",
    "Rom. 3:24", "Rom. 3:26",
    "Isa. 61:10", "Luke 15:22", "Jer. 23:6", "Zech. 3:4",
    
    # Section I.B
    "Rom. 5:18",
    
    # Section II references (v. and vv. should resolve to Rom. 5)
    "Rom. 5:1-11",  # vv. 1-11
    "Rom. 5:5", "Rom. 5:2", "Rom. 5:1", "Rom. 5:10",  # six wonderful things
    "Rom. 5:6", "Rom. 5:11",  # Triune God
    
    # Section II.B
    "Rom. 5:1, 10-11", "Rom. 5:5",
    
    # Section II.B.1
    "John 14:6a", "Jude 20-21", "1 John 4:8, 16",
    
    # Section II.B.2
    "2 Tim. 1:6-7", "2 Tim. 4:22",
    
    # Section II.C
    "Rom. 5:2", "Rom. 5:1",
    
    # Section II.C.1
    "Luke 7:47-48", "Luke 7:50",  # Luke 7 with vv. 47-48 and v. 50
    
    # Section II.C.2
    "Rom. 3:17", "Rom. 8:6",
    
    # Section III heading
    "Rom. 5:3-4, 11",
    
    # Page 2
    # Section III.A
    "2 Cor. 12:7-9", "Rom. 8:28-29",
    
    # Section III.B
    "Phil. 2:19-22", "1 Thes. 2:4",
    
    # Section III.B.1
    "1 Pet. 1:7", "Mal. 3:3",
    
    # Section III.B.2
    "Rev. 3:18", "Rev. 1:20", "Rev. 21:18, 23", "2 Pet. 1:4",
    
    # Section III.B.4
    "Matt. 24:45-51",
    
    # Section III.C
    "Rom. 5:4", "Rom. 5:2",
    
    # Section III.C.1
    "2 Cor. 4:17",
    
    # Section III.C.2
    "1 Pet. 5:10", "1 Thes. 2:12", "Col. 1:27", "Phil. 3:21",
    
    # Section III.C.3
    "Heb. 2:10-11", "2 Cor. 3:16-18", "2 Cor. 4:6b",
    
    # Section III.D
    "Rom. 5:10", "Rom. 12:5", "Rom. 16:1, 4-5, 16, 20"
]

# Remove duplicates and normalize
unique_expected = []
seen = set()
for ref in all_expected:
    # Normalize format
    normalized = ref.strip()
    if normalized not in seen:
        unique_expected.append(normalized)
        seen.add(normalized)

print(f"Total unique expected references: {len(unique_expected)}")
print("\nAll expected references:")
for i, ref in enumerate(unique_expected, 1):
    print(f"{i:3}. {ref}")

# Load the test results from our last run
detected_refs = [
    "Rom. 5:1-11",
    "Acts 10:43",
    "Rom. 3:24",
    "Rom. 3:26",
    "Isa. 61:10",
    "Luke 15:22",
    "Jer. 23:6",
    "Zech. 3:4",
    "Rom. 5:18",
    "Rom. 5:1-11",  # vv. 1-11
    "Rom. 5:5",
    "Rom. 5:2",
    "Rom. 5:1",
    "Rom. 5:10",
    "Rom. 5:6",
    "Rom. 5:11",
    "Rom. 5:1, 10-11",
    "John 14:6a",
    "Jude 20-21",
    "1 John 4:8, 16",
    "2 Tim. 1:6-7",
    "2 Tim. 4:22",
    "Rom. 5:2",  # duplicate ok
    "Rom. 5:1",  # duplicate ok
    # Missing: Luke 7 references
    "Rom. 3:17",
    "Rom. 8:6",
    "Rom. 5:3-4, 11",
    "2 Cor. 12:7-9",
    "Rom. 8:28-29",
    "Phil. 2:19-22",
    "1 Thes. 2:4",
    "1 Pet. 1:7",
    "Mal. 3:3",
    "Rev. 3:18",
    "Rev. 1:20",
    "Rev. 21:18, 23",
    "2 Pet. 1:4",
    "Matt. 24:45-51",
    "Rom. 5:4",
    "2 Cor. 4:17",
    "1 Pet. 5:10",
    "1 Thes. 2:12",
    "Col. 1:27",
    "Phil. 3:21",
    "Heb. 2:10-11",
    "2 Cor. 3:16-18",
    "2 Cor. 4:6b",
    "Rom. 5:10",  # duplicate ok
    "Rom. 12:5",
    "Rom. 16:1, 4-5, 16, 20"
]

# Find missing references
missing = []
for ref in unique_expected:
    if ref not in detected_refs:
        missing.append(ref)

print(f"\n\nMISSING REFERENCES ({len(missing)}):")
for ref in missing:
    print(f"  - {ref}")

# Analyze the pattern
print("\n\nANALYSIS:")
print("The missing references appear to be:")
print("1. Luke 7:47-48 (from 'vv. 47-48' after 'according to Luke 7')")
print("2. Luke 7:50 (from 'v. 50' after the Luke 7 context)")
print("\nThese are contextual references that need the 'Luke 7' mentioned earlier to resolve properly.")