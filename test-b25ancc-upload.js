const fs = require('fs');
const path = require('path');

const API_BASE = 'https://bible-outline-backend.onrender.com/api';

async function testFileUpload() {
    console.log('\nTesting B25ANCC02en.pdf upload...');
    
    const testFile = path.join(__dirname, 'B25ANCC02en.pdf');
    
    if (!fs.existsSync(testFile)) {
        console.log('❌ Test file not found:', testFile);
        return false;
    }
    
    try {
        const fileContent = fs.readFileSync(testFile);
        const formData = new FormData();
        
        const blob = new Blob([fileContent], { type: 'application/pdf' });
        formData.append('file', blob, 'B25ANCC02en.pdf');
        
        console.log('📤 Uploading file (this may take up to 5 minutes)...');
        const startTime = Date.now();
        
        const response = await fetch(`${API_BASE}/enhanced/upload`, {
            method: 'POST',
            body: formData
        });
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(1);
        const result = await response.json();
        
        if (response.ok) {
            console.log(`✅ Upload successful in ${elapsedTime} seconds!`, {
                status: response.status,
                session_id: result.session_id,
                references_found: result.references_found,
                total_verses: result.total_verses
            });
            return result.session_id;
        } else {
            console.log(`❌ Upload failed after ${elapsedTime} seconds:`, {
                status: response.status,
                error: result.error || result
            });
            return false;
        }
    } catch (error) {
        console.log('❌ Upload request error:', error.message);
        return false;
    }
}

async function testPopulateVerses(sessionId) {
    if (!sessionId) {
        console.log('\nSkipping populate test (no session ID)');
        return false;
    }
    
    console.log(`\nTesting verse population for session: ${sessionId}`);
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
            console.log('✅ Populate successful!', {
                status: response.status,
                verse_count: result.verse_count,
                content_length: result.populated_content ? result.populated_content.length : 0
            });
            
            // Save the output to a file for inspection
            if (result.populated_content) {
                fs.writeFileSync('B25ANCC02en_output.txt', result.populated_content);
                console.log('📝 Output saved to B25ANCC02en_output.txt');
            }
            return true;
        } else {
            console.log('❌ Populate failed:', {
                status: response.status,
                error: result.error || result
            });
            return false;
        }
    } catch (error) {
        console.log('❌ Populate request error:', error.message);
        return false;
    }
}

// Run the test
async function runTest() {
    console.log('🚀 Testing B25ANCC02en.pdf processing...');
    console.log('Backend URL:', API_BASE);
    
    const sessionId = await testFileUpload();
    if (sessionId) {
        await testPopulateVerses(sessionId);
    }
}

if (typeof fetch === 'undefined') {
    console.log('❌ This test requires Node.js 18+ with built-in fetch support');
    process.exit(1);
}

runTest().catch(console.error);