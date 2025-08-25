from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from src.utils.accurate_inline_processor import AccurateInlineProcessor
from src.utils.ocr_service import OCRService

document_bp = Blueprint('document', __name__)

# Initialize the accurate inline processor
# Try different possible paths for the database file
possible_paths = [
    # Path when running from src directory (production on Render)
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'bible_verses.db'),
    # Path when running from project root
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bible_verses.db'),
    # Absolute path on Render
    '/opt/render/project/src/bible-outline-enhanced-backend/bible_verses.db',
    # Legacy path
    '/home/ubuntu/recovery_version_bible_final.db'
]

bible_db_path = None
for path in possible_paths:
    if os.path.exists(path):
        bible_db_path = path
        print(f"Found database at: {path}")
        break

if not bible_db_path:
    print(f"Warning: Could not find bible database. Searched paths: {possible_paths}")
    bible_db_path = possible_paths[0]  # Use first path as fallback

doc_processor = AccurateInlineProcessor(bible_db_path)
ocr_service = OCRService()

@document_bp.route('/test', methods=['GET'])
def test_route():
    """Test route to verify document blueprint is working"""
    return jsonify({'message': 'Document blueprint is working!', 'success': True})

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Upload and process PDF/Word document"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process the file
        result = doc_processor.process_file(file_path, filename)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """Upload and process image with OCR"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process with OCR
        result = ocr_service.process_image(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if result['success']:
            # Process the extracted text as a document
            # Create a temporary file with the OCR text
            temp_text_file = os.path.join(UPLOAD_FOLDER, f"ocr_{filename}.txt")
            with open(temp_text_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            doc_result = doc_processor.process_file(temp_text_file, f"ocr_{filename}.txt")
            
            # Clean up temp file
            os.remove(temp_text_file)
            
            return jsonify({
                'success': True,
                'ocr_result': result,
                'document_result': doc_result
            })
        else:
            return jsonify(result), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/process-document', methods=['POST'])
def process_document():
    """Process document and extract verse references"""
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({'error': 'Session ID is required'}), 400
    
    session_id = data['session_id']
    format_type = data.get('format', 'inline')
    
    try:
        result = doc_processor.populate_verses(session_id, format_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/export/<session_id>', methods=['GET'])
def export_document(session_id):
    """Export processed document as Word file"""
    try:
        file_path = doc_processor.export_to_word(session_id)
        if not file_path:
            return jsonify({'error': 'Export failed or session not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'church_outline_{session_id}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/export-clean/<session_id>', methods=['GET'])
def export_clean_text(session_id):
    """Export clean text without HTML tags for OneNote"""
    try:
        clean_text = doc_processor.export_clean_text(session_id)
        if not clean_text:
            return jsonify({'error': 'Clean text export failed or session not found'}), 404
        
        return jsonify({
            'success': True,
            'clean_text': clean_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/session/<session_id>', methods=['PUT'])
def update_session(session_id):
    """Update session content"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    try:
        # Update the session with new content
        if session_id in doc_processor.sessions:
            doc_processor.sessions[session_id]['original_content'] = data['content']
            # Re-find references in the updated content
            references = doc_processor._find_inline_references(data['content'])
            doc_processor.sessions[session_id]['references'] = references
            return jsonify({'success': True, 'message': 'Content updated successfully'})
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/ocr/process', methods=['POST'])
def process_ocr():
    """Process image with OCR only"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process with OCR
        result = ocr_service.process_image(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_bp.route('/ocr/to-document', methods=['POST'])
def ocr_to_document():
    """Convert OCR result to document format"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        # Create a temporary file with the OCR text
        temp_text_file = os.path.join(UPLOAD_FOLDER, "ocr_document.txt")
        with open(temp_text_file, 'w', encoding='utf-8') as f:
            f.write(data['text'])
        
        result = doc_processor.process_file(temp_text_file, "ocr_document.txt")
        
        # Clean up temp file
        os.remove(temp_text_file)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

