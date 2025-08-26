"""
Enhanced Document Processing Routes with ML/LLM Support
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from src.utils.enhanced_processor import EnhancedProcessor
from openai import OpenAI

enhanced_bp = Blueprint('enhanced', __name__)

# Global variable for enhanced processor (lazy initialization)
enhanced_processor = None

def get_enhanced_processor():
    """Get or create the enhanced processor instance (lazy loading)"""
    global enhanced_processor
    if enhanced_processor is None:
        try:
            bible_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bible_verses.db')
            # Get OpenAI key from environment
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                print(f"OpenAI API key found (length: {len(openai_key)}), enabling LLM detection")
            else:
                print("Warning: No OpenAI API key found, LLM detection disabled")
            enhanced_processor = EnhancedProcessor(bible_db_path, openai_key=openai_key)
            print("Enhanced processor initialized successfully with hybrid detection")
        except Exception as e:
            import traceback
            print(f"ERROR: Could not initialize EnhancedProcessor: {e}")
            print("Full traceback:")
            traceback.print_exc()
            print("Make sure OPENAI_API_KEY is set in .env file or environment variables")
            raise e
    return enhanced_processor

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@enhanced_bp.route('/upload', methods=['POST'])
def enhanced_upload():
    """Upload and process document with hybrid detection"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Check if LLM should be used (from request or default to True)
    use_llm = request.form.get('use_llm', 'true').lower() == 'true'
    
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process with enhanced detector
        result = processor.process_document(file_path, filename, use_llm=use_llm)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/populate/<session_id>', methods=['POST'])
def enhanced_populate(session_id):
    """Populate verses with optimal placement"""
    data = request.get_json() or {}
    format_type = data.get('format', 'margin')  # Default to margin format like MSG12VerseReferences.pdf
    
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        result = processor.populate_verses(session_id, format_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/feedback/<session_id>', methods=['POST'])
def provide_feedback(session_id):
    """Provide feedback on verse detection and placement"""
    data = request.get_json()
    
    if not data or 'corrections' not in data:
        return jsonify({'error': 'Corrections data required'}), 400
    
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        result = processor.provide_feedback(session_id, data['corrections'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/train', methods=['POST'])
def train_model():
    """Trigger model training with collected data"""
    data = request.get_json() or {}
    min_samples = data.get('min_samples', 50)
    
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        result = processor.train_model(min_samples)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/training-report', methods=['GET'])
def training_report():
    """Get training data statistics and recommendations"""
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        report = processor.get_training_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/export/<session_id>', methods=['GET'])
def export_session(session_id):
    """Export session data for analysis"""
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        session_data = processor.export_session(session_id)
        if session_data:
            return jsonify(session_data)
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/settings', methods=['GET', 'POST'])
def api_settings():
    """Get or update API settings (OpenAI key, etc.)"""
    if request.method == 'GET':
        # Return current settings (without sensitive data)
        return jsonify({
            'use_llm_default': True,
            'has_openai_key': bool(os.getenv('OPENAI_API_KEY')),
            'model_path': 'models/verse_detector.pkl',
            'model_exists': os.path.exists('models/verse_detector.pkl')
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Update OpenAI key if provided
        if 'openai_key' in data:
            os.environ['OPENAI_API_KEY'] = data['openai_key']
            # Update will be applied on next processor initialization
            # The lazy loading will pick up the new environment variable
            
        return jsonify({'success': True, 'message': 'Settings updated'})

@enhanced_bp.route('/test-llm', methods=['POST'])
def test_llm():
    """Test LLM connection and verse detection"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Test text required'}), 400
    
    try:
        processor = get_enhanced_processor()
    except Exception as e:
        return jsonify({'error': 'Enhanced processing not available. Check logs for details.'}), 503
    
    try:
        # Test with a small sample
        references = processor.detector.detect_verses(
            data['text'], 
            use_llm=True
        )
        
        # Convert to JSON-serializable format
        ref_list = []
        for ref in references:
            ref_list.append({
                'book': ref.book,
                'chapter': ref.chapter,
                'start_verse': ref.start_verse,
                'end_verse': ref.end_verse,
                'confidence': ref.confidence,
                'original_text': ref.original_text
            })
        
        return jsonify({
            'success': True,
            'references_found': len(references),
            'references': ref_list,
            'llm_available': bool(processor.detector.openai_api_key)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'llm_available': bool(processor.detector.openai_api_key)
        })