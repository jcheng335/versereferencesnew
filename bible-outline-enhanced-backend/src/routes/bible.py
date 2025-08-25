from flask import Blueprint, request, jsonify
from src.utils.sqlite_bible_database import SQLiteBibleDatabase
from src.utils.verse_parser import VerseParser
import uuid

bible_bp = Blueprint('bible', __name__)

# Initialize database and parser
bible_db = SQLiteBibleDatabase()
parser = VerseParser()

@bible_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        stats = bible_db.get_stats()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bible_bp.route('/verses/lookup', methods=['GET'])
def lookup_verses():
    """Look up verses by reference string"""
    reference = request.args.get('reference')
    if not reference:
        return jsonify({'error': 'Reference parameter is required'}), 400
    
    try:
        # Parse the reference
        parsed_refs = parser.parse_reference(reference)
        if not parsed_refs:
            return jsonify({'error': 'Invalid reference format'}), 400
        
        verses = []
        for ref in parsed_refs:
            verse_data = bible_db.lookup_verse(ref['book'], ref['chapter'], ref['verse'])
            if verse_data:
                verse_data['original_reference'] = reference
                verses.append(verse_data)
        
        return jsonify({
            'success': True,
            'reference': reference,
            'verses': verses,
            'count': len(verses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/verses/batch-lookup', methods=['POST'])
def batch_lookup_verses():
    """Look up multiple verses by reference strings"""
    data = request.get_json()
    if not data or 'references' not in data:
        return jsonify({'error': 'References array is required'}), 400
    
    references = data['references']
    if not isinstance(references, list):
        return jsonify({'error': 'References must be an array'}), 400
    
    try:
        all_verses = bible_db.lookup_verses_by_references(references)
        
        return jsonify({
            'success': True,
            'references': references,
            'verses': all_verses,
            'count': len(all_verses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/verses/search', methods=['GET'])
def search_verses():
    """Search verses by text content"""
    query = request.args.get('query') or request.args.get('q')
    limit = request.args.get('limit', 50, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        verses = bible_db.search_verses(query, limit)
        return jsonify({
            'success': True,
            'query': query,
            'verses': verses,
            'count': len(verses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/books', methods=['GET'])
def get_books():
    """Get all books in the Bible"""
    try:
        books = bible_db.get_all_books()
        return jsonify({
            'success': True,
            'books': books,
            'count': len(books)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/books/<book_name>', methods=['GET'])
def get_book(book_name):
    """Get book information by name"""
    try:
        book = bible_db.get_book_by_name(book_name)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        return jsonify({
            'success': True,
            'book': book
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/books/<book_name>/<int:chapter>', methods=['GET'])
def get_chapter_verses(book_name, chapter):
    """Get all verses in a specific chapter"""
    try:
        verses = bible_db.get_chapter_verses(book_name, chapter)
        return jsonify({
            'success': True,
            'book': book_name,
            'chapter': chapter,
            'verses': verses,
            'count': len(verses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/parse-references', methods=['POST'])
def parse_references():
    """Parse verse references from text"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text parameter is required'}), 400
    
    text = data['text']
    
    try:
        # Extract references from text
        references = parser.extract_references_from_text(text)
        
        # Parse each reference
        parsed_references = []
        for ref in references:
            parsed = parser.parse_reference(ref)
            parsed_references.append({
                'original': ref,
                'parsed': parsed,
                'normalized': parser.normalize_reference(ref)
            })
        
        return jsonify({
            'success': True,
            'text': text,
            'references': parsed_references,
            'count': len(parsed_references)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/populate-text', methods=['POST'])
def populate_text_with_verses():
    """Populate text with verse content"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Text parameter is required'}), 400
    
    text = data['text']
    format_type = data.get('format', 'inline')  # 'inline' or 'footnotes'
    
    try:
        # Extract references from text
        references = parser.extract_references_from_text(text)
        
        # Look up all verses
        all_verses = bible_db.lookup_verses_by_references(references)
        
        # Create a mapping of references to verses
        verse_map = {}
        for verse in all_verses:
            ref = verse.get('original_reference', verse['reference'])
            if ref not in verse_map:
                verse_map[ref] = []
            verse_map[ref].append(verse)
        
        # Populate the text based on format
        populated_text = text
        if format_type == 'inline':
            for ref in references:
                if ref in verse_map:
                    verses_text = []
                    for verse in verse_map[ref]:
                        verses_text.append(f"({verse['reference']}: {verse['text']})")
                    replacement = f"{ref} {' '.join(verses_text)}"
                    populated_text = populated_text.replace(ref, replacement)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'populated_text': populated_text,
            'references_found': references,
            'verses': all_verses,
            'format': format_type
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bible_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = bible_db.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

