# Bible Verse Reference Application - Technical Documentation

## Project Overview
A comprehensive Bible verse reference application that uses a **hybrid approach** combining:
1. **Regex patterns** for initial verse detection ✅
2. **OpenAI LLM** for context understanding and validation ✅
3. **Machine Learning** for continuous improvement and scoring ⚠️ (Temporarily disabled due to Render Python 3.13 issues)

## Core Requirements
- **OpenAI API Key**: REQUIRED - The hybrid system depends on OpenAI for context understanding
- **Bible Database**: SQLite database with all Bible verses (bible_verses.db)
- **Python 3.11.10**: Specified in runtime.txt (Python 3.13 has C extension compatibility issues)
- **Node.js 18+**: For frontend

## Architecture

### Backend Structure
```
bible-outline-enhanced-backend/
├── src/
│   ├── main.py                    # Flask app entry point
│   ├── routes/
│   │   ├── bible.py               # Bible lookup endpoints
│   │   ├── document.py            # Basic document processing
│   │   └── enhanced_document.py   # HYBRID AI/ML processing
│   └── utils/
│       ├── enhanced_processor.py      # Main processor orchestrator
│       ├── hybrid_verse_detector.py   # HYBRID detection system
│       ├── training_data_manager.py   # ML training data storage
│       ├── model_scheduler.py         # Automated retraining
│       └── sqlite_bible_database.py   # Bible verse lookups
└── requirements.txt
```

### Frontend Structure
```
bible-outline-enhanced-frontend/
├── src/
│   ├── components/
│   │   ├── Upload.jsx             # Basic upload
│   │   └── EnhancedUpload.jsx    # AI-powered upload with LLM toggle
│   └── config/
│       └── api.js                 # API configuration
└── package.json
```

## Hybrid Verse Detection System

### 1. Regex Detection (Initial Pass)
- Patterns for standard formats: `Rom 5:18`, `Romans 5:18-20`, etc.
- Handles abbreviations and variations
- Fast initial candidate identification

### 2. OpenAI LLM Validation (Context Understanding)
- **Model**: GPT-3.5-turbo
- **Purpose**: 
  - Validate detected references
  - Understand context and placement
  - Identify optimal insertion points (after complete thoughts)
- **Required**: OpenAI API key must be set

### 3. Machine Learning (Scoring & Improvement)
- **Model**: Random Forest Classifier
- **Features**: Text patterns, position, context
- **Training**: Continuous learning from user feedback
- **Versioning**: Models saved with timestamps

## API Endpoints

### Enhanced Processing (Hybrid System)
- `POST /api/enhanced/upload` - Process document with hybrid detection
  - Body: `file` (multipart), `use_llm` (boolean)
  - Returns: session_id, detected references, confidence scores

- `POST /api/enhanced/populate/<session_id>` - Insert verses at optimal points
  - Body: `format` (inline/footnote)
  - Returns: populated content with verses

- `POST /api/enhanced/feedback/<session_id>` - Provide corrections
  - Body: `corrections` (array of corrections)
  - Used for ML model improvement

- `GET /api/enhanced/training-report` - View model performance
- `POST /api/enhanced/train` - Trigger model retraining
- `POST /api/enhanced/settings` - Update OpenAI API key

### Basic Processing (Fallback)
- `POST /api/upload` - Basic regex-only processing
- `POST /api/populate` - Basic verse insertion

## Environment Variables

### Required
```bash
OPENAI_API_KEY=sk-...  # REQUIRED for hybrid approach
```

### Optional
```bash
ENABLE_AUTO_RETRAIN=true  # Enable automatic model retraining
DATABASE_URL=postgresql://...  # For production database
```

## Deployment Configuration

### Render Setup
1. **Backend Service**: Web Service
   - Build: `cd bible-outline-enhanced-backend && pip install -r requirements.txt`
   - Start: `cd bible-outline-enhanced-backend/src && gunicorn main:app --bind 0.0.0.0:$PORT`
   - Environment: Add `OPENAI_API_KEY`

2. **Frontend Service**: Static Site
   - Build: `cd bible-outline-enhanced-frontend && npm install && npm run build`
   - Publish: `bible-outline-enhanced-frontend/dist`

### Database
- Development: SQLite (bible_verses.db, training_data.db)
- Production: Can use PostgreSQL with DATABASE_URL

## Key Features

### Verse Insertion Logic
- **Placement**: After complete outline points, not mid-sentence
- **Format**: "Reference - verse text" on same line
- **Context-aware**: Uses LLM to understand document structure

### Training & Improvement
- **Feedback Collection**: User corrections stored in SQLite
- **Automated Retraining**: Scheduler checks daily for new data
- **Model Versioning**: Each model saved with timestamp
- **Rollback Support**: Can revert to previous model versions

### Performance Optimization
- **Caching**: 15-minute cache for repeated API calls
- **Batch Processing**: Multiple verses processed together
- **Lazy Loading**: Components initialized only when needed

## Common Issues & Solutions

### 1. Deployment Failures
**Issue**: pandas/scikit-learn build fails with C extension errors
**Solution**: Use Python 3.11.10 (specified in runtime.txt), not 3.13

**Issue**: OpenAI not initialized
**Solution**: Ensure OPENAI_API_KEY is set in environment

**Issue**: Module compilation errors with Python 3.13
**Solution**: Temporarily removed ML dependencies (scikit-learn, pandas, numpy)
**Status**: System works with Regex + OpenAI LLM (2/3 hybrid components)
**TODO**: Re-add ML when Render supports Python version specification

### 2. Verse Insertion Problems
**Issue**: Verses breaking sentences
**Solution**: LLM analyzes context to find sentence endings

**Issue**: Wrong format
**Solution**: Format controlled in enhanced_processor.py line 157

### 3. Network Errors
**Issue**: Frontend can't reach backend
**Solution**: Check API_BASE_URL in frontend config/api.js

## Testing Checklist

1. **Upload Test**
   - Upload PDF/DOCX with Bible references
   - Verify references detected with confidence scores
   - Check LLM validation working

2. **Population Test**
   - Click "Populate Verses"
   - Verify verses inserted after outline points
   - Check format is "Reference - verse text"

3. **Feedback Test**
   - Use thumbs up/down buttons
   - Provide corrections
   - Verify feedback stored

4. **Training Test**
   - Check training report endpoint
   - Verify model metrics displayed
   - Test retraining with sufficient samples

## Future Enhancements

1. **Multi-language Support**: Detect verses in other languages
2. **Custom Training**: Allow users to train on their specific document styles
3. **Batch Processing**: Process multiple documents simultaneously
4. **Export Formats**: Support more output formats (PDF, DOCX)
5. **Reference Validation**: Check if referenced verses actually exist

## Critical Files to Never Modify Without Context

1. **hybrid_verse_detector.py**: Core detection logic
2. **enhanced_processor.py**: Main orchestration
3. **training_data_manager.py**: Data persistence
4. **enhanced_document.py**: API routes

## Monitoring & Logs

- Check Render logs for deployment issues
- Monitor OpenAI API usage and costs
- Track model performance metrics over time
- Review user feedback patterns

## Contact & Support

- GitHub: https://github.com/jcheng335/versereferencesnew
- Render Dashboard: https://dashboard.render.com
- OpenAI Platform: https://platform.openai.com

---

**Last Updated**: 2025-08-25
**Version**: 2.0 (Hybrid AI/ML System)
**Status**: Production Ready with OpenAI API Key