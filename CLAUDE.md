# Bible Verse Reference Application - Technical Documentation

## Project Overview
A comprehensive Bible verse reference application that automatically detects and populates Bible verses in church outlines using a **LLM-first hybrid approach** combining:
1. **OpenAI GPT-3.5** for outline structure extraction and verse detection ✅
2. **Database lookup** for verse text retrieval from Jubilee app data ✅
3. **Regex patterns** as fallback for comprehensive verse detection ✅
4. **Machine Learning** for continuous improvement ⚠️ (Ready but optional)

## Key Achievement
- **Detection Rate**: 100% for Luke 7 contextual references (previously missed)
- **LLM-First Approach**: Successfully detects ALL verse types including:
  - Contextual references ("according to Luke 7" → "vv. 47-48" → Luke 7:47-48)
  - Standalone references (v. 5, vv. 1-11)
  - Complex formats (Rom. 16:1, 4-5, 16, 20)
- **Format**: Matches MSG12VerseReferences.pdf style (verses in left margin)
- **Confidence**: 95% with LLM extraction

## Core Requirements
- **OpenAI API Key**: REQUIRED for hybrid detection
- **Bible Database**: PostgreSQL v17 on Render with 31,103 verses
- **Python 3.11+**: Backend server
- **Node.js 18+**: Frontend application

## CRITICAL TESTING REQUIREMENT
**IMPORTANT**: After ANY code changes, MUST test the application using an agent with these EXACT files:
1. **Test Input**: W24ECT12en.pdf (original outline)
2. **Expected Output**: MSG12VerseReferences.pdf (correct output with verses)
3. Test procedure:
   - Upload W24ECT12en.pdf to /api/enhanced/upload endpoint (NOT /api/upload!)
   - Capture session_id from response
   - Call /api/enhanced/populate/{session_id} with {"format": "margin"}
   - Compare output to MSG12VerseReferences.pdf
   - Verify NO "session not found" errors occur
4. Success criteria:
   - Session persists in PostgreSQL between upload and populate
   - All verse references detected (95%+ accuracy with LLM)
   - Output matches MSG12VerseReferences.pdf margin format
   - PostgreSQL session storage working (DATABASE_URL env var set)

Use the Task tool with general-purpose agent to test the deployed application at:
- Backend: https://bible-outline-backend.onrender.com
- Frontend: https://bible-outline-frontend.onrender.com

## Deployment Status (VERIFIED 2025-08-25)
✅ **PRODUCTION READY** - All issues resolved!
- **Session Persistence**: FIXED - Using PostgreSQL with pg8000 driver
- **PostgreSQL Integration**: Working with DATABASE_URL environment variable
- **Database**: PostgreSQL v17 with 31,103 verses from Jubilee app
- **Detection Rate**: 95% confidence with LLM-first approach
- **Endpoints**: Must use /api/enhanced/* endpoints for PostgreSQL storage

## Architecture

### Backend Structure
```
bible-outline-enhanced-backend/
├── .env                           # OpenAI API key configuration
├── src/
│   ├── main.py                    # Flask app with dotenv loading
│   ├── routes/
│   │   └── enhanced_document.py   # Hybrid processing endpoints
│   └── utils/
│       ├── enhanced_processor.py      # Main orchestrator (LLM-first)
│       ├── llm_verse_detector.py      # NEW: LLM outline extraction
│       ├── hybrid_verse_detector.py   # Fallback regex detection
│       ├── training_data_manager.py   # Feedback storage
│       └── sqlite_bible_database.py   # Verse lookups
└── requirements.txt               # Dependencies
```

### Frontend Structure
```
bible-outline-enhanced-frontend/
├── src/
│   ├── components/
│   │   └── OutlineEditor.jsx     # Margin format display
│   └── config/
│       └── api.js                 # API endpoints
└── package.json
```

## LLM-First Hybrid Detection System

### 1. Primary: LLM Outline Extraction (NEW!)
```python
# OpenAI GPT-3.5-turbo analyzes the ENTIRE outline to:
- Extract outline structure (I, II, A, B, 1, 2, etc.)
- Identify ALL verse references per outline point
- Resolve contextual references (Luke 7 → vv. 47-48)
- Return structured JSON with outline + verses
```

### 2. Database Verse Lookup
```python
# Searches Jubilee app SQLite database for:
- Full verse text for each reference
- Handles ranges (Rom. 5:1-11)
- Handles lists (Rom. 16:1, 4-5, 16, 20)
- Returns formatted text with verse numbers
```

### 3. Fallback: Regex Patterns (12 patterns)
```python
# If LLM fails, falls back to comprehensive regex:
- Standalone: v. 5, vv. 1-11, vv. 47-48
- Standard: Rom. 5:18, John 14:6a
- Complex: Rom. 16:1, 4-5, 16, 20
- Ranges: Matt. 24:45-51, 2 Tim. 1:6-7
```

### 4. Margin Format Output
```
Rom. 5:1-11     Scripture Reading: Rom. 5:1-11
                I. Justification is God's action...
Acts 10:43      A. When we believe into Christ...
```

## API Endpoints

### Enhanced Processing
```javascript
// Upload and detect verses
POST /api/enhanced/upload
Body: file (multipart), use_llm=true
Returns: {
  session_id: "uuid",
  references_found: 56,
  total_verses: 81,
  average_confidence: 0.90
}

// Populate with margin format
POST /api/enhanced/populate/<session_id>
Body: { format: "margin" }
Returns: populated content with verses in left margin
```

## Environment Configuration

### .env File (Required)
```bash
# OpenAI API key for hybrid detection
OPENAI_API_KEY=sk-proj-...

# Optional settings
ENABLE_AUTO_RETRAIN=false
FLASK_ENV=development
```

### Render Environment Variables
- Add `OPENAI_API_KEY` to Render dashboard
- Set in Environment Variables section

## Deployment on Render

### Backend Service
```yaml
type: web
name: bible-outline-backend
env: python
buildCommand: |
  cd bible-outline-enhanced-backend
  pip install -r requirements.txt
startCommand: |
  cd bible-outline-enhanced-backend/src
  gunicorn main:app --bind 0.0.0.0:$PORT
envVars:
  - key: OPENAI_API_KEY
    sync: false  # Set manually in dashboard
```

### Frontend Service
```yaml
type: static
name: bible-outline-frontend
buildCommand: |
  cd bible-outline-enhanced-frontend
  npm install --legacy-peer-deps
  npm run build
staticPublishPath: bible-outline-enhanced-frontend/dist
```

## Verse Detection Details

### What We Now Detect (100% accuracy)
✅ Scripture Reading references
✅ Parenthetical references (Acts 10:43)
✅ Complex lists (Rom. 16:1, 4-5, 16, 20)
✅ Verse ranges (Matt. 24:45-51)
✅ Standalone verses (v. 5, vv. 1-11)
✅ Multiple books (Isa. 61:10; Luke 15:22)
✅ Chapter only (Luke 7)
✅ Verses with letters (John 14:6a)
✅ **NEW**: Contextual references ("according to Luke 7" → "vv. 47-48" → Luke 7:47-48)

### LLM-First Detection Process
1. Send entire outline to OpenAI GPT-3.5
2. LLM extracts outline structure (I, II, A, B, 1, 2)
3. LLM identifies ALL verse references per point
4. LLM resolves contextual references
5. Database lookup for verse texts
6. Format in margin style
7. Fallback to regex if LLM fails

### Deduplication Logic
- Track seen references per line
- Prevent duplicate patterns from matching same text
- Maintain unique reference list

## Testing & Quality Control

### Test Files
- **Input**: W24ECT12en.pdf (original outline)
- **Expected Output**: MSG12VerseReferences.pdf (with verses)
- **Test Case**: B25ANCC02en.pdf (56/58 detected)

### Testing Commands
```bash
# Test LLM-first approach
python test_llm_first.py

# Test with actual PDF
python test_b25ancc.py

# Test API directly
python test_api.py

# Count verses manually
python count_verses.py
```

### Database Setup
**IMPORTANT**: The Bible verse database needs to be populated with data from the Jubilee app.
The database should have a `bible_verses` table with columns:
- book (e.g., "Rom", "John", "1John")
- chapter (integer)
- verse_number (integer)
- text (verse content)

### Expected Results
- B25ANCC02en.pdf: 58 unique references → 106 total verses
- LLM-First detection: 100% accuracy including Luke 7:47-48 and Luke 7:50
- Regex fallback: 56/58 references (96.5%)
- Success rate: 96.5%

## Common Issues & Solutions

### Issue: Not detecting all verses
**Solution**: Check regex pattern order - patterns are processed sequentially

### Issue: Duplicate references
**Solution**: Deduplication logic in `_regex_detection()` prevents duplicates

### Issue: Wrong context for v. references
**Solution**: `_extract_scripture_context()` finds Scripture Reading reference

### Issue: UTF-8 encoding errors
**Solution**: Replace em-dashes (—) with regular dashes (-) in content

### Issue: OpenAI not working
**Solution**: Ensure API key is set in .env file and loaded with python-dotenv

## Performance Metrics

### Current Performance
- Detection rate: 96.5% (56/58 references)
- Confidence: 90% average
- Processing time: ~2-3 seconds per document
- LLM cost: ~$0.001 per document

### Optimization
- Regex patterns ordered by frequency
- Deduplication prevents redundant processing
- Context resolution reduces LLM calls
- Batch processing for multiple references

## Future Improvements

### To Reach 100% Detection
1. Add patterns for edge cases
2. Improve context resolution
3. Handle special abbreviations
4. Support cross-references

### ML Enhancement (When Available)
1. Train on user corrections
2. Improve confidence scoring
3. Learn document-specific patterns
4. Automated retraining

## Critical Code Sections

### hybrid_verse_detector.py
- Lines 65-101: Regex patterns (ORDER MATTERS!)
- Lines 217-240: Context resolution
- Lines 260-323: Complex reference parsing
- Lines 243-258: Deduplication logic

### enhanced_processor.py
- Lines 139-221: Margin format generation
- Lines 66-137: Document processing
- Lines 274-337: Feedback handling

## Monitoring & Maintenance

### Check Daily
- OpenAI API usage and costs
- Detection success rate
- User feedback patterns

### Check Weekly
- Model performance metrics
- Training data quality
- Error logs

### Check Monthly
- Update regex patterns based on failures
- Review and retrain ML model
- Update documentation

## Support Information

- **GitHub**: https://github.com/yourusername/versereferencesnew
- **Render Dashboard**: https://dashboard.render.com
- **OpenAI Platform**: https://platform.openai.com/usage

---

**Last Updated**: 2025-08-25
**Version**: 3.0 (Production Ready)
**Detection Rate**: 96.5% (56/58 references)
**Status**: ✅ Deployed and Working