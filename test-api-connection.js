// Node.js script to test the API connection like the frontend would
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://bible-outline-backend.onrender.com/api';

// Test 1: Health Check
async function testHealth() {
    console.log('\n1. Testing Backend Health Endpoint...');
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('✅ Health Check Success:', {
            status: response.status,
            data: data
        });
        return true;
    } catch (error) {
        console.log('❌ Health Check Failed:', error.message);
        return false;
    }
}

// Test 2: File Upload (with our test file)
async function testFileUpload() {
    console.log('\n2. Testing File Upload...');
    
    const testFile = path.join(__dirname, 'test-bible-verses.txt');
    
    if (!fs.existsSync(testFile)) {
        console.log('❌ Test file not found:', testFile);
        return false;
    }
    
    try {
        // Read file and create FormData equivalent
        const fileContent = fs.readFileSync(testFile);
        const formData = new FormData();
        
        // Create a blob from the file content
        const blob = new Blob([fileContent], { type: 'text/plain' });
        formData.append('file', blob, 'test-bible-verses.txt');
        
        const response = await fetch(`${API_BASE}/enhanced/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log('✅ File Upload Success:', {
                status: response.status,
                session_id: result.session_id,
                references_found: result.references_found,
                total_verses: result.total_verses
            });
            return result.session_id;
        } else {
            console.log('❌ File Upload Failed:', {
                status: response.status,
                error: result.error || result
            });
            return false;
        }
    } catch (error) {
        console.log('❌ File Upload Error:', error.message);
        return false;
    }
}

// Test 3: Populate Verses
async function testPopulateVerses(sessionId) {
    if (!sessionId) {
        console.log('\n3. Skipping Populate Verses (no session ID)');
        return false;
    }
    
    console.log('\n3. Testing Populate Verses...');
    try {
        const response = await fetch(`${API_BASE}/enhanced/populate/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                format: 'margin'
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log('✅ Populate Verses Success:', {
                status: response.status,
                verse_count: result.verse_count,
                content_preview: result.populated_content ? result.populated_content.substring(0, 200) + '...' : 'No content'
            });
            return true;
        } else {
            console.log('❌ Populate Verses Failed:', {
                status: response.status,
                error: result.error || result
            });
            return false;
        }
    } catch (error) {
        console.log('❌ Populate Verses Error:', error.message);
        return false;
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 Starting Frontend-Backend Connection Tests...');
    console.log('Backend URL:', API_BASE);
    
    const healthOk = await testHealth();
    const sessionId = await testFileUpload();
    const populateOk = await testPopulateVerses(sessionId);
    
    console.log('\n📊 Test Results Summary:');
    console.log('Health Check:', healthOk ? '✅ PASS' : '❌ FAIL');
    console.log('File Upload:', sessionId ? '✅ PASS' : '❌ FAIL');
    console.log('Populate Verses:', populateOk ? '✅ PASS' : '❌ FAIL');
    
    if (healthOk && sessionId && populateOk) {
        console.log('\n🎉 All tests passed! Frontend-backend connection should work properly.');
    } else {
        console.log('\n⚠️ Some tests failed. Check the errors above.');
    }
}

// Check if fetch is available (Node.js 18+)
if (typeof fetch === 'undefined') {
    console.log('❌ This test requires Node.js 18+ with built-in fetch support');
    console.log('Alternative: Run this code in a browser console or use node-fetch');
    process.exit(1);
}

runAllTests().catch(console.error);