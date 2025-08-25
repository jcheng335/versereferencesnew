"""
Enhanced Document Processing Routes with ML/LLM Support
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from src.utils.enhanced_processor import EnhancedProcessor

enhanced_bp = Blueprint('enhanced', __name__)

# Global variable for enhanced processor (lazy initialization)
enhanced_processor = None

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def get_enhanced_processor():
    """Get or create the enhanced processor instance"""
    global enhanced_processor
    if enhanced_processor is None:
        try:
            bible_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bible_verses.db')
            enhanced_processor = EnhancedProcessor(bible_db_path)
        except Exception as e:
            print(f"Warning: Could not initialize EnhancedProcessor: {e}")
            # Return a basic processor that will return errors
            return None
    return enhanced_processor

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
        # Get processor
        processor = get_enhanced_processor()
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
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
    format_type = data.get('format', 'inline')
    
    try:
        processor = get_enhanced_processor()
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
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
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
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
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
        result = processor.train_model(min_samples)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/training-report', methods=['GET'])
def training_report():
    """Get training data statistics and recommendations"""
    try:
        processor = get_enhanced_processor()
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
        report = processor.get_training_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enhanced_bp.route('/export/<session_id>', methods=['GET'])
def export_session(session_id):
    """Export session data for analysis"""
    try:
        processor = get_enhanced_processor()
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
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
            processor = get_enhanced_processor()
            if processor:
                processor.detector.openai_api_key = data['openai_key']
            
        return jsonify({'success': True, 'message': 'Settings updated'})

@enhanced_bp.route('/test-llm', methods=['POST'])
def test_llm():
    """Test LLM connection and verse detection"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Test text required'}), 400
    
    try:
        # Get processor
        processor = get_enhanced_processor()
        if not processor:
            return jsonify({'error': 'Enhanced processing not available'}), 503
        
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
            'llm_available': bool(processor.detector.openai_api_key) if processor else False
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'llm_available': bool(processor.detector.openai_api_key) if processor else False
        })