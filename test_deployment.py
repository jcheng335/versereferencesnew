#!/usr/bin/env python3

import requests
import json
import time
import sys
import os

# Fix console encoding for Windows
if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

def test_bible_verse_detection():
    """Test the Bible verse detection application deployment"""
    
    base_url = "https://bible-outline-backend.onrender.com"
    test_file = r"C:\Users\jchen\versereferencesnew\original outlines\W24ECT12en.pdf"
    
    print("=== Bible Verse Detection App Test ===")
    print(f"Testing backend at: {base_url}")
    print(f"Test file: {test_file}")
    print()
    
    # 1. Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   📊 Database: {health_data.get('database', 'unknown')}")
            print(f"   📚 Verses: {health_data.get('stats', {}).get('verses', 'unknown')}")
            print(f"   📖 Books: {health_data.get('stats', {}).get('books', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    print()
    
    # 2. Test file upload
    print("2. Testing file upload...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/upload", files=files)
            
        if response.status_code == 200:
            upload_data = response.json()
            print(f"   ✅ Upload successful")
            print(f"   🎯 References found: {upload_data.get('references_found', 'unknown')}")
            print(f"   📝 Total verses: {upload_data.get('total_verses', 'unknown')}")
            print(f"   🔑 Session ID: {upload_data.get('session_id', 'unknown')}")
            
            session_id = upload_data.get('session_id')
            if not session_id:
                print(f"   ❌ No session ID returned")
                return False
                
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return False
    
    print()
    
    # 3. Test enhanced endpoints (if available)
    print("3. Testing enhanced endpoints...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'use_llm': 'true'}
            response = requests.post(f"{base_url}/api/enhanced/upload", files=files, data=data)
            
        if response.status_code == 200:
            enhanced_data = response.json()
            print(f"   ✅ Enhanced upload successful")
            print(f"   🎯 References found: {enhanced_data.get('references_found', 'unknown')}")
            print(f"   🤖 Used LLM: {enhanced_data.get('used_llm', 'unknown')}")
            print(f"   🔑 Session ID: {enhanced_data.get('session_id', 'unknown')}")
        elif response.status_code == 502:
            print(f"   ⚠️  Enhanced endpoints experiencing 502 errors (timeout/overload)")
        else:
            print(f"   ❌ Enhanced upload failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️  Enhanced endpoints error: {e}")
    
    print()
    
    # 4. Compare with expected results
    print("4. Analyzing detection results...")
    expected_verses = 308  # From MSG12VerseReferences.pdf analysis
    found_verses = upload_data.get('total_verses', 0)
    detection_rate = (found_verses / expected_verses) * 100 if expected_verses > 0 else 0
    
    print(f"   📊 Expected verses: {expected_verses}")
    print(f"   🎯 Detected verses: {found_verses}")
    print(f"   📈 Detection rate: {detection_rate:.1f}%")
    
    if detection_rate >= 90:
        print(f"   ✅ Excellent detection rate!")
    elif detection_rate >= 70:
        print(f"   ⚠️  Good detection rate, room for improvement")
    elif detection_rate >= 50:
        print(f"   ⚠️  Moderate detection rate, needs work")
    else:
        print(f"   ❌ Poor detection rate, significant issues")
    
    print()
    
    # 5. Test frontend connectivity
    print("5. Testing frontend connectivity...")
    try:
        frontend_response = requests.get("https://bible-outline-frontend.onrender.com", timeout=10)
        if frontend_response.status_code == 200:
            print(f"   ✅ Frontend is accessible")
            if "Bible Outline" in frontend_response.text:
                print(f"   ✅ Frontend content looks correct")
            else:
                print(f"   ⚠️  Frontend content may be incorrect")
        else:
            print(f"   ❌ Frontend not accessible: {frontend_response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
    
    print()
    
    # Summary
    print("=== Test Summary ===")
    if detection_rate >= 70:
        print("🎉 DEPLOYMENT TEST PASSED")
        print(f"✅ Backend API working")
        print(f"✅ File processing functional") 
        print(f"✅ Detection rate: {detection_rate:.1f}% (Good)")
        print(f"✅ Database connected with {health_data.get('stats', {}).get('verses', 'unknown')} verses")
        
        if detection_rate < 90:
            print(f"⚠️  Areas for improvement:")
            print(f"   - Detection rate could be higher (target: 95%+)")
            print(f"   - Consider LLM-first approach improvements")
        
        return True
    else:
        print("❌ DEPLOYMENT TEST FAILED")
        print(f"❌ Detection rate too low: {detection_rate:.1f}%")
        print(f"❌ Application not meeting quality requirements")
        return False

if __name__ == "__main__":
    success = test_bible_verse_detection()
    sys.exit(0 if success else 1)