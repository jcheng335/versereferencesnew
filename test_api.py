"""
Test the enhanced API with hybrid verse detection
"""

import requests
import json

# API base URL
API_URL = "http://localhost:5004/api/enhanced"

# Test content from B25ANCC02en.pdf (full first section)
test_content = """
Message Two
The Result of Our Justification -
the Full Enjoyment of God in Christ as Our Life

Scripture Reading: Rom. 5:1-11

I. Justification is God's action in approving us according to His standard of righteousness; the believers' righteousness is not a condition that they possess in themselves but a person to whom they are joined, the living Christ Himself:

A. When we believe into Christ, we receive God's forgiveness (Acts 10:43), and God can justify us (Rom. 3:24, 26) by making Christ our righteousness and by clothing us with Christ as our robe of righteousness (Isa. 61:10; Luke 15:22; Jer. 23:6; Zech. 3:4).

B. Life is the goal of God's salvation; thus, justification is "of life"; through justification we have come up to the standard of God's righteousness and correspond with it so that now He can impart His life into us - Rom. 5:18.

II. The result of our justification is the full enjoyment of God in Christ as our life - vv. 1-11:

A. The result of our justification is embodied in six wonderful things - love (v. 5), grace (v. 2), peace (v. 1), hope (v. 2), life (v. 10), and glory (v. 2) - for our enjoyment; these verses also reveal the Triune God - the Holy Spirit (v. 5), Christ (v. 6), and God (v. 11) - for our enjoyment.

B. Through the redeeming death of Christ, God has justified us sinners and has reconciled us, His enemies, to Himself (vv. 1, 10-11); furthermore, "the love of God has been poured out in our hearts through the Holy Spirit, who has been given to us" (v. 5):

1. Although we may be afflicted, poor, and depressed, we cannot deny the presence of God's love within us; in order to stay on the line of life, which is Christ Himself (John 14:6a), we need to keep ourselves in the love of God (Jude 20-21), which is God Himself (1 John 4:8, 16).

2. We need to fan our God-given spirit of love into flame so that we can have a burning spirit of love to overcome the degradation of today's church; to fan our spirit into flame is to build up the habit of exercising our spirit continually so that we may stay in contact with the Lord as the Spirit in our spirit - 2 Tim. 1:6-7; 4:22.

C. "We have obtained access by faith into this grace in which we stand" (Rom. 5:2); since we have been justified by faith and stand in the realm of grace, "we have peace toward God through our Lord Jesus Christ" (v. 1):

1. Having peace "toward" God means that our journey into God through our being justified out of faith has not yet been completed, and we are still on the way into God; according to Luke 7, the Lord Jesus told the sinful woman, who "loved much" because she had been forgiven much (vv. 47-48) in order to be saved, to "go into peace" (v. 50, lit.).

2. Once we have passed through the gate of justification, we need to walk on the way of peace (Rom. 3:17); when we set our mind on the spirit - by caring for our spirit, using our spirit, paying attention to our spirit, contacting God by our spirit in communion with the Spirit of God, and walking and living in our spirit - our mind becomes peace to give us an inner feeling of rest, release, brightness, and comfort (8:6).

III. In the realm of grace, we have God as our boast and exultation for our enjoyment and rejoicing; to boast in God is also to "boast in our tribulations, knowing that tribulation produces endurance; and endurance, approvedness; and approvedness, hope" - 5:3-4, 11:

A. Tribulation is actually the incarnation of grace and the sweet visitation of grace; to reject tribulation is to reject grace, which is God as our portion for our enjoyment; grace mainly visits us in the form of tribulation by which God causes all things (all persons, all matters, all situations, all circumstances, and all environments) to work together for good, which is our gaining more of Christ to have Him wrought into our being, so that we may be transformed metabolically and conformed to Christ's image and so that we may be brought into the full sonship - 2 Cor. 12:7-9; Rom. 8:28-29.
"""

def test_upload_and_detect():
    """Test uploading content and detecting verses"""
    # Write test content to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Upload the file
        print("Uploading test content...")
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_outline.txt', f, 'text/plain')}
            data = {'use_llm': 'true'}  # Use LLM for hybrid approach
            
            response = requests.post(f"{API_URL}/upload", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] Upload successful!")
            print(f"Full response: {json.dumps(result, indent=2)}")
            print(f"Session ID: {result.get('session_id')}")
            print(f"References found: {result.get('references_found', 0)}")
            print(f"Total verses: {result.get('total_verses', 0)}")
            print(f"Average confidence: {result.get('average_confidence', 0):.2f}")
            
            # Test populate verses
            if result.get('session_id'):
                test_populate(result['session_id'])
            
            return result
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
        print(f"[SUCCESS] Populate successful!")
        print(f"Format: {result.get('format')}")
        print(f"Verse count: {result.get('verse_count')}")
        print(f"Message: {result.get('message')}")
        
        # Show a sample of the populated content
        content = result.get('populated_content', '')
        lines = content.split('\n')[:10]  # First 10 lines
        print("\nSample output (first 10 lines):")
        for line in lines:
            print(line)
    else:
        print(f"[FAILED] Populate failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_upload_and_detect()