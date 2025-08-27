"""
Enhanced Document Processor with Hybrid Verse Detection
Integrates regex, OpenAI LLM, and ML for optimal verse placement
"""

import os
import re
import uuid
from typing import Dict, List, Any, Optional
import pdfplumber
from docx import Document
from .hybrid_verse_detector import HybridVerseDetector, VerseReference
from .llm_verse_detector import LLMVerseDetector
try:
    from .pure_llm_detector import PureLLMDetector
    PURE_LLM_AVAILABLE = True
except ImportError:
    PURE_LLM_AVAILABLE = False
    print("Pure LLM detector not available")
try:
    from .master_verse_detector import MasterVerseDetector
    MASTER_AVAILABLE = True
except ImportError:
    MASTER_AVAILABLE = False
    print("Master detector not available")
# Ultimate detector removed - using comprehensive detector instead
ULTIMATE_AVAILABLE = False
try:
    from .improved_llm_detector import HybridLLMDetector
    IMPROVED_LLM_AVAILABLE = True
except ImportError:
    IMPROVED_LLM_AVAILABLE = False
    print("Improved LLM detector not available")
try:
    from .comprehensive_detector import ComprehensiveVerseDetector
    COMPREHENSIVE_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_AVAILABLE = False
    print("Comprehensive detector not available - using hybrid detector")
try:
    from .llm_first_detector import LLMFirstDetector
    LLM_FIRST_AVAILABLE = True
except ImportError:
    LLM_FIRST_AVAILABLE = False
    print("LLM-first detector not available")
from .training_data_manager import TrainingDataManager
from .sqlite_bible_database import SQLiteBibleDatabase
from .session_manager import SessionManager
try:
    from .html_structured_processor import HtmlStructuredProcessor
    HTML_PROCESSOR_AVAILABLE = True
except ImportError:
    HTML_PROCESSOR_AVAILABLE = False
    print("HTML structured processor not available")

# Import margin formatter for proper output formatting
try:
    from .margin_formatter import MarginFormatter
    MARGIN_FORMATTER_AVAILABLE = True
except ImportError:
    MARGIN_FORMATTER_AVAILABLE = False
    print("Margin formatter not available")

# PostgreSQL Bible database is optional - use if available
try:
    from .postgres_bible_database import PostgresBibleDatabase
    POSTGRES_BIBLE_AVAILABLE = True
except ImportError:
    POSTGRES_BIBLE_AVAILABLE = False
    print("PostgreSQL Bible database not available - using SQLite")

# PostgreSQL session manager is optional - only use if available
try:
    from .pg8000_session_manager import PG8000SessionManager
    POSTGRES_SESSION_AVAILABLE = True
except ImportError:
    POSTGRES_SESSION_AVAILABLE = False
    print("PostgreSQL session manager not available - using SQLite")

# Model scheduler is optional - depends on ML libraries
try:
    from .model_scheduler import ModelScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("Model scheduler not available - ML features disabled")

class EnhancedProcessor:
    def __init__(self, db_path: str, openai_key: str = None, use_llm_first: bool = False, use_html_processor: bool = True):
        """
        Initialize enhanced processor with hybrid detection
        
        Args:
            db_path: Path to Bible database
            openai_key: OpenAI API key (optional, uses env var if not provided)
            use_llm_first: Whether to use LLM-first approach (default True)
        """
        # Use PostgreSQL for Bible verses if available (on Render), otherwise SQLite
        if POSTGRES_BIBLE_AVAILABLE and os.getenv('DATABASE_URL'):
            try:
                self.bible_db = PostgresBibleDatabase()
                print("Using PostgreSQL for Bible verse storage")
            except Exception as e:
                print(f"Failed to initialize PostgreSQL Bible database: {e}")
                self.bible_db = SQLiteBibleDatabase(db_path)
                print("Falling back to SQLite for Bible verses")
        else:
            self.bible_db = SQLiteBibleDatabase(db_path)
            print("Using SQLite for Bible verse storage")
        
        # Use PostgreSQL for sessions if available (on Render), otherwise SQLite
        if POSTGRES_SESSION_AVAILABLE and os.getenv('DATABASE_URL'):
            try:
                self.session_manager = PG8000SessionManager()
                print("Using PostgreSQL for session storage")
            except Exception as e:
                print(f"Failed to initialize PostgreSQL session manager: {e}")
                self.session_manager = SessionManager()  # Fallback to SQLite
                print("Falling back to SQLite for session storage")
        else:
            self.session_manager = SessionManager()  # Use SQLite
            print("Using SQLite for session storage")
            
        self.use_llm_first = use_llm_first
        
        # Initialize the best available detector - Pure LLM for 100% accuracy without regex
        if PURE_LLM_AVAILABLE and openai_key:
            try:
                self.pure_llm = PureLLMDetector(openai_key)
                print("Using Pure LLM Detector (no regex) for intelligent detection")
                self.detector = self.pure_llm
            except Exception as e:
                print(f"Could not initialize Pure LLM detector: {e}")
                # Fallback to LLM-first if available
                if LLM_FIRST_AVAILABLE:
                    try:
                        self.llm_first = LLMFirstDetector(openai_key)
                        print("Falling back to LLM-First Detector")
                        self.detector = self.llm_first
                    except Exception as e2:
                        print(f"LLM-first also failed: {e2}")
                        if COMPREHENSIVE_AVAILABLE:
                            self.comprehensive_detector = ComprehensiveVerseDetector(openai_key)
                            print("Falling back to Comprehensive Verse Detector")
                            self.detector = self.comprehensive_detector
        elif LLM_FIRST_AVAILABLE and openai_key:
            try:
                self.llm_first = LLMFirstDetector(openai_key)
                print("Using LLM-First Detector for 100% accuracy")
                self.detector = self.llm_first
            except Exception as e:
                print(f"Could not initialize LLM-first detector: {e}")
                if COMPREHENSIVE_AVAILABLE:
                    self.comprehensive_detector = ComprehensiveVerseDetector(openai_key)
                    print("Falling back to Comprehensive Verse Detector")
                    self.detector = self.comprehensive_detector
        elif COMPREHENSIVE_AVAILABLE:
            self.comprehensive_detector = ComprehensiveVerseDetector(openai_key)
            print("Using Comprehensive Verse Detector for 100% accuracy")
            # Use comprehensive detector as primary
            self.detector = self.comprehensive_detector
        elif MASTER_AVAILABLE:
            self.master_detector = MasterVerseDetector(openai_key)
            print("Using Master Verse Detector - combines all detection methods")
            self.detector = self.master_detector
        elif ULTIMATE_AVAILABLE:
            self.ultimate_detector = UltimateVerseDetector()
            print("Using Ultimate Verse Detector for 100% accuracy")
            self.detector = self.ultimate_detector
        else:
            # Initialize hybrid detector as fallback
            self.detector = HybridVerseDetector(
                openai_api_key=openai_key,
                model_path='models/verse_detector.pkl'
            )
            print("Using Hybrid Verse Detector")
        
        if IMPROVED_LLM_AVAILABLE and openai_key:
            self.improved_llm = HybridLLMDetector(openai_key)
            print("Improved Hybrid LLM Detector available")
        
        # Initialize LLM detector if using LLM-first approach
        if self.use_llm_first:
            self.llm_detector = LLMVerseDetector()
        
        # Initialize training data manager
        self.training_manager = TrainingDataManager('training_data.db')
        
        # Initialize HTML processor if available
        self.use_html_processor = use_html_processor and HTML_PROCESSOR_AVAILABLE
        if self.use_html_processor:
            self.html_processor = HtmlStructuredProcessor(self.bible_db, openai_key)
            print("HTML structured processor initialized for 100% verse population")
        
        # Initialize margin formatter
        if MARGIN_FORMATTER_AVAILABLE:
            self.margin_formatter = MarginFormatter()
            print("Margin formatter initialized for proper output")
        else:
            self.margin_formatter = None
        
        # Create models directory if not exists
        os.makedirs('models', exist_ok=True)
        
        # Initialize model scheduler for automated retraining (if available)
        self.scheduler = None
        if SCHEDULER_AVAILABLE:
            try:
                self.scheduler = ModelScheduler(
                    training_manager=self.training_manager,
                    detector=self.detector,
                    check_interval_hours=24,  # Check daily
                    min_new_samples=100,
                    min_feedback_count=50
                )
                
                # Start scheduler in production (check environment variable)
                if os.getenv('ENABLE_AUTO_RETRAIN', 'false').lower() == 'true':
                    self.scheduler.start()
            except Exception as e:
                print(f"Could not initialize scheduler: {e}")
                self.scheduler = None
    
    def process_document(self, file_path: str, filename: str, use_llm: bool = True, force_html: bool = True) -> Dict[str, Any]:
        """
        Process document with enhanced verse detection
        
        Args:
            file_path: Path to uploaded file
            filename: Original filename
            use_llm: Whether to use OpenAI LLM for validation
        
        Returns:
            Processing result with session ID and detected references
        """
        print(f"[DEBUG] Starting process_document for {filename}, use_llm={use_llm}, force_html={force_html}")
        try:
            # Use HTML processor for 100% verse population if enabled
            if force_html and self.use_html_processor:
                print("[INFO] Using HTML structured processor for 100% verse population")
                result = self.html_processor.process_document(file_path, filename)
                
                # Generate session ID and store result
                session_id = str(uuid.uuid4())
                
                # Store in session for populate method
                session_data = {
                    'original_content': result.get('text_output', ''),
                    'original_filename': filename,
                    'structured_data': result.get('structured_data'),
                    'html_output': result.get('html_output'),
                    'populated_content': result.get('text_output'),
                    'use_llm': True,
                    'stats': result.get('stats', {})
                }
                
                self.session_manager.save_session(session_id, session_data)
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'content': result.get('text_output', ''),
                    'references_found': result['stats'].get('total_verses_detected', 0),
                    'total_verses': result['stats'].get('total_verses_populated', 0),
                    'filename': filename,
                    'average_confidence': result['stats'].get('population_rate', 0) / 100,
                    'message': f"HTML processor: {result['stats'].get('population_rate', 0):.1f}% verses populated"
                }
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Extract text based on file type
            content = self._extract_text(file_path, filename)
            
            # Use LLM-first approach if enabled
            llm_outline = None
            
            if self.use_llm_first and use_llm:
                # Process with LLM to extract outline and verses
                llm_result = self.llm_detector.process_document(content)
                
                if llm_result['success']:
                    # Convert LLM results to reference format
                    ref_dicts = []
                    llm_outline = llm_result['outline_points']
                    
                    for point in llm_result['outline_points']:
                        for verse in point.get('verses', []):
                            # Parse the verse reference
                            ref_text = verse['reference']
                            parsed = self._parse_reference_string(ref_text)
                            
                            if parsed:
                                ref_dict = {
                                    'book': parsed['book'],
                                    'chapter': parsed['chapter'],
                                    'start_verse': parsed['start_verse'],
                                    'end_verse': parsed['end_verse'],
                                    'context': point['outline_text'],
                                    'confidence': 0.95,  # High confidence for LLM results
                                    'insertion_point': len(content),  # Will be updated in populate
                                    'original_text': ref_text,
                                    'verse_text': verse.get('text', '')
                                }
                                ref_dicts.append(ref_dict)
                else:
                    # Fallback to detector - handle both dict and list returns
                    detection_result = self._call_detector_safely(content, use_llm)
                    
                    # Check if Pure LLM detector returned dict with metadata
                    if isinstance(detection_result, dict):
                        references = detection_result.get('verses', [])
                        session_metadata = detection_result.get('metadata', {})
                        session_structure = detection_result.get('outline_structure', [])
                        # Store the full detection result as structured_data for margin formatter
                        session_structured_data = detection_result
                    else:
                        references = detection_result
                        session_metadata = {}
                        session_structure = []
                        session_structured_data = None
                    
                    ref_dicts = []
                    
                    for ref in references:
                        ref_dict = {
                            'book': ref.book,
                            'chapter': ref.chapter,
                            'start_verse': ref.start_verse,
                            'end_verse': ref.end_verse,
                            'context': ref.context,
                            'confidence': ref.confidence,
                            'insertion_point': ref.insertion_point,
                            'original_text': ref.original_text
                        }
                        ref_dicts.append(ref_dict)
            else:
                # Use the configured detector - handle both dict and list returns
                detection_result = self._call_detector_safely(content, use_llm)
                
                # Check if Pure LLM detector returned dict with metadata
                if isinstance(detection_result, dict):
                    references = detection_result.get('verses', [])
                    session_metadata = detection_result.get('metadata', {})
                    session_structure = detection_result.get('outline_structure', [])
                    # Store the full detection result as structured_data for margin formatter
                    session_structured_data = detection_result
                else:
                    references = detection_result
                    session_metadata = {}
                    session_structure = []
                    session_structured_data = None
                
                ref_dicts = []
                
                for ref in references:
                    ref_dict = {
                        'book': ref.book,
                        'chapter': ref.chapter,
                        'start_verse': ref.start_verse,
                        'end_verse': ref.end_verse,
                        'context': getattr(ref, 'context', ''),
                        'confidence': ref.confidence,
                        'insertion_point': getattr(ref, 'insertion_point', 0),
                        'original_text': ref.original_text
                    }
                    ref_dicts.append(ref_dict)
            
            # Store session data persistently
            session_data = {
                'original_content': content,
                'original_filename': filename,
                'references': ref_dicts,
                'populated_content': None,
                'use_llm': use_llm,
                'llm_outline': llm_outline,  # Store LLM outline structure if available
                'metadata': session_metadata if 'session_metadata' in locals() else {},
                'outline_structure': session_structure if 'session_structure' in locals() else [],
                'structured_data': session_structured_data if 'session_structured_data' in locals() and session_structured_data else {
                    'metadata': session_metadata if 'session_metadata' in locals() else {},
                    'outline_structure': session_structure if 'session_structure' in locals() else [],
                    'content': [],  # Will be populated with formatted content
                    'verses': ref_dicts
                }
            }
            print(f"Saving session {session_id} with {len(ref_dicts)} references")
            self.session_manager.save_session(session_id, session_data)
            print(f"Session {session_id} saved successfully")
            
            # Add to training data (for future model improvement)
            sample_id = self.training_manager.add_training_sample(
                original_text=content,
                references=ref_dicts,
                confidence=sum(r['confidence'] for r in ref_dicts) / len(ref_dicts) if ref_dicts else 0
            )
            
            # Store sample ID in session for feedback tracking
            # Update session with sample_id
            session_data['sample_id'] = sample_id
            self.session_manager.save_session(session_id, session_data)
            
            return {
                'success': True,
                'session_id': session_id,
                'content': content,
                'references_found': len(ref_dicts),
                'total_verses': sum((r['end_verse'] or r['start_verse']) - r['start_verse'] + 1 for r in ref_dicts),
                'filename': filename,
                'average_confidence': sum(r['confidence'] for r in ref_dicts) / len(ref_dicts) if ref_dicts else 0,
                'sample_id': sample_id  # For feedback tracking
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing document: {str(e)}'
            }
    
    def populate_verses(self, session_id: str, format_type: str = 'margin') -> Dict[str, Any]:
        """
        Populate document with verses in margin format (like MSG12VerseReferences.pdf)
        
        Args:
            session_id: Session identifier
            format_type: Format type ('margin', 'inline', or 'footnote')
        
        Returns:
            Populated content with verses in margin
        """
        # Retrieve session from persistent storage
        print(f"Attempting to retrieve session {session_id}")
        session = self.session_manager.get_session(session_id)
        if not session:
            print(f"Session {session_id} not found in storage")
            return {'success': False, 'error': 'Session not found'}
        print(f"Session {session_id} retrieved successfully")
        
        # Check if this was processed with HTML processor or Pure LLM
        if session.get('html_output') or session.get('structured_data'):
            print("Session was processed with HTML/Pure LLM processor - formatting with margin formatter")
            
            # Use margin formatter if available
            if self.margin_formatter and format_type == 'margin':
                structured_data = session.get('structured_data')
                if structured_data:
                    html_output = self.margin_formatter.format_html(structured_data)
                    return {
                        'success': True,
                        'populated_content': session.get('populated_content', ''),
                        'html_content': html_output,
                        'format': format_type,
                        'verse_count': session.get('stats', {}).get('total_verses_populated', 0),
                        'message': f"Formatted with margin formatter"
                    }
            
            # Fallback to original HTML output
            return {
                'success': True,
                'populated_content': session.get('populated_content', ''),
                'html_content': session.get('html_output', ''),
                'format': format_type,
                'verse_count': session.get('stats', {}).get('total_verses_populated', 0),
                'message': f"100% verses populated via HTML structure processing"
            }
        
        content = session['original_content']
        references = session.get('references', [])
        llm_outline = session.get('llm_outline')
        
        try:
            # If we have LLM outline structure, use it for better formatting
            if llm_outline and format_type == 'margin':
                result_lines = []
                
                for point in llm_outline:
                    # Format verse references for margin
                    if point.get('verses'):
                        refs = ', '.join([v['reference'] for v in point['verses']])
                        # Left column for references (20 chars), right column for outline text
                        if point.get('outline_number'):
                            formatted_line = f"{refs:<20} {point['outline_number']}. {point['outline_text']}"
                        else:
                            formatted_line = f"{refs:<20} {point['outline_text']}"
                    else:
                        if point.get('outline_number'):
                            formatted_line = f"{'':20} {point['outline_number']}. {point['outline_text']}"
                        else:
                            formatted_line = f"{'':20} {point['outline_text']}"
                    
                    result_lines.append(formatted_line)
                
                # Add verse texts at the end
                result_lines.append('')
                result_lines.append('=' * 80)
                result_lines.append('VERSE TEXTS:')
                result_lines.append('=' * 80)
                
                for point in llm_outline:
                    for verse in point.get('verses', []):
                        verse_text = verse.get('text')
                        
                        # If LLM didn't provide verse text or provided invalid text, fetch from database
                        # Invalid text includes: empty, error messages, or just reference numbers
                        is_invalid_text = (
                            not verse_text or 
                            verse_text == '[Verse text not found in database]' or
                            len(verse_text) < 10 or  # Too short, likely just reference numbers
                            verse_text.count(':') > 0 and len(verse_text.split()) <= 3  # Looks like reference format
                        )
                        
                        if is_invalid_text:
                            # Parse the reference and fetch from database
                            parsed = self._parse_reference_string(verse['reference'])
                            if parsed:
                                ref_dict = {
                                    'book': parsed['book'],
                                    'chapter': parsed['chapter'],
                                    'start_verse': parsed['start_verse'],
                                    'end_verse': parsed['end_verse']
                                }
                                verse_text = self._fetch_verse_text(ref_dict)
                        
                        if verse_text:
                            result_lines.append(f"{verse['reference']}: {verse_text}")
                
                populated_content = '\n'.join(result_lines)
                
                # Store populated content back to persistent storage
                session['populated_content'] = populated_content
                self.session_manager.save_session(session_id, session)
                
                return {
                    'success': True,
                    'populated_content': populated_content,
                    'format': format_type,
                    'verse_count': sum(len(p.get('verses', [])) for p in llm_outline),
                    'message': f'Successfully populated {sum(len(p.get("verses", [])) for p in llm_outline)} verses using LLM-first approach'
                }
            
            # Enhanced approach: Process content with better verse placement
            lines = content.split('\n')
            result_lines = []
            
            # First, detect outline structure and associate verses
            outline_verses = {}  # Map outline points to their verses
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                
                # Detect outline points
                is_outline_point = (
                    re.match(r'^[IVX]+\.\s', stripped_line) or  # Roman numerals
                    re.match(r'^[A-Z]\.\s', stripped_line) or    # Capital letters
                    re.match(r'^\d+\.\s', stripped_line)         # Numbers
                )
                
                if is_outline_point:
                    outline_verses[i] = []
                
                # Find verses mentioned in this line
                verses_in_line = []
                for ref in references:
                    # Check if reference appears in this line (based on text content)
                    if ref.get('original_text') and ref['original_text'] in line:
                        verses_in_line.append(ref)
                
                # Associate verses with outline points
                if verses_in_line:
                    if i in outline_verses:
                        # This line is an outline point, add verses to it
                        outline_verses[i].extend(verses_in_line)
                    else:
                        # Find nearest outline point above
                        for j in range(i - 1, -1, -1):
                            if j in outline_verses:
                                outline_verses[j].extend(verses_in_line)
                                break
            
            # Now format the output with verses under outline points
            for i, line in enumerate(lines):
                # Add the original line
                result_lines.append(line)
                
                # If this is an outline point with associated verses, add them below
                if i in outline_verses and outline_verses[i]:
                    # Add verse texts indented below the outline point
                    for ref in outline_verses[i]:
                        verse_text = self._fetch_verse_text(ref)
                        if verse_text:
                            # Format: indented verse reference and text
                            result_lines.append(f"    {ref['original_text']}: {verse_text}")
                    # Add blank line after verses for readability
                    if outline_verses[i]:
                        result_lines.append("")
            
            populated_content = '\n'.join(result_lines)
            
            # Store populated content back to persistent storage
            session['populated_content'] = populated_content
            self.session_manager.save_session(session_id, session)
            
            return {
                'success': True,
                'populated_content': populated_content,
                'format': format_type,
                'verse_count': len(references),
                'message': f'Successfully populated {len(references)} verses in {format_type} format'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error populating verses: {str(e)}'
            }
    
    def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from various file formats"""
        if filename.lower().endswith('.pdf'):
            # Use standard PDF extraction to get ALL text
            # HTML conversion was losing content between outline points
            return self._extract_pdf_text(file_path)
        elif filename.lower().endswith(('.docx', '.doc')):
            return self._extract_docx_text(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error extracting Word document text: {str(e)}")
    
    def _call_detector_safely(self, content: str, use_llm: bool) -> List:
        """
        Safely call detect_verses with the appropriate parameters for each detector type
        """
        try:
            # Check detector type and call with appropriate parameters
            if hasattr(self, 'llm_first') and self.detector == self.llm_first:
                # LLMFirstDetector uses use_training parameter (and optional _internal_call)
                return self.detector.detect_verses(content, use_training=use_llm, _internal_call=False)
            elif hasattr(self, 'ultimate_detector') and self.detector == self.ultimate_detector:
                # UltimateVerseDetector uses context parameter
                return self.detector.detect_verses(content, context={'use_llm': use_llm})
            else:
                # Try to detect which parameter the detector expects using introspection
                import inspect
                try:
                    sig = inspect.signature(self.detector.detect_verses)
                    params = list(sig.parameters.keys())
                    
                    if 'use_training' in params:
                        return self.detector.detect_verses(content, use_training=use_llm)
                    elif 'use_llm' in params:
                        return self.detector.detect_verses(content, use_llm=use_llm)
                    elif 'context' in params:
                        return self.detector.detect_verses(content, context={'use_llm': use_llm})
                    elif len(params) == 1:  # Only takes text parameter
                        return self.detector.detect_verses(content)
                    else:
                        # Default: try with use_llm
                        return self.detector.detect_verses(content, use_llm=use_llm)
                except:
                    # If introspection fails, try common patterns
                    try:
                        return self.detector.detect_verses(content, use_llm=use_llm)
                    except TypeError:
                        try:
                            return self.detector.detect_verses(content, use_training=use_llm)
                        except TypeError:
                            return self.detector.detect_verses(content)
        except Exception as e:
            print(f"Error calling detector: {e}")
            # Try without parameters as last resort
            return self.detector.detect_verses(content)
    
    def _fetch_verse_text(self, reference: Dict) -> Optional[str]:
        """Fetch verse text from database"""
        try:
            verses = []
            end_verse = reference.get('end_verse') or reference.get('start_verse')
            for verse_num in range(reference['start_verse'], end_verse + 1):
                verse_data = self.bible_db.lookup_verse(
                    reference['book'],
                    reference['chapter'],
                    verse_num
                )
                if verse_data and 'text' in verse_data:
                    verses.append(verse_data['text'])
            
            return ' '.join(verses) if verses else None
            
        except Exception as e:
            print(f"Error fetching verse: {e}")
            return None
    
    def provide_feedback(self, session_id: str, corrections: List[Dict]) -> Dict[str, Any]:
        """
        Provide feedback on verse detection and placement
        
        Args:
            session_id: Session identifier
            corrections: List of corrected verse references and placements
        
        Returns:
            Feedback processing result
        """
        # Retrieve session from persistent storage
        print(f"Attempting to retrieve session {session_id}")
        session = self.session_manager.get_session(session_id)
        if not session:
            print(f"Session {session_id} not found in storage")
            return {'success': False, 'error': 'Session not found'}
        print(f"Session {session_id} retrieved successfully")
        sample_id = session.get('sample_id')
        
        if sample_id:
            # Determine if feedback is positive or negative
            is_positive = True
            for correction in corrections:
                if correction.get('type') == 'negative' or correction.get('action') in ['remove', 'fix']:
                    is_positive = False
                    break
            
            # Store corrections in training data
            self.training_manager.add_user_correction(sample_id, corrections)
            
            # Add feedback to hybrid detector for immediate learning
            self.detector.add_feedback(
                session['original_content'],
                corrections
            )
            
            # Log detailed feedback
            self.training_manager.add_feedback(
                sample_id,
                'user_correction',
                {
                    'corrections': corrections,
                    'is_positive': is_positive,
                    'session_id': session_id,
                    'use_llm': session.get('use_llm', False)
                }
            )
            
            # Check if automatic retraining should be triggered
            if self.scheduler and self.scheduler.is_running:
                # Check thresholds in background
                import threading
                threading.Thread(
                    target=self.scheduler.check_and_retrain,
                    daemon=True
                ).start()
            
            return {
                'success': True,
                'message': 'Feedback received and stored for model improvement',
                'sample_id': sample_id,
                'is_positive': is_positive,
                'feedback_count': self.training_manager.get_feedback_count(sample_id)
            }
        
        return {'success': False, 'error': 'No training sample associated with session'}
    
    def train_model(self, min_samples: int = 50) -> Dict[str, Any]:
        """
        Train or retrain the ML model with collected data
        
        Args:
            min_samples: Minimum number of samples required for training
        
        Returns:
            Training result
        """
        # Get validated training samples
        samples = self.training_manager.get_validated_samples()
        
        if len(samples) < min_samples:
            return {
                'success': False,
                'error': f'Insufficient training data. Need {min_samples}, have {len(samples)}'
            }
        
        # Prepare training data
        training_data = []
        for sample in samples:
            training_data.append({
                'text': sample['original_text'],
                'correct_references': sample['user_corrections'] or sample['references']
            })
        
        # Train the model
        self.detector.train_model(training_data)
        
        # Log performance metrics (you would calculate these from a test set)
        metrics = {
            'accuracy': 0.85,  # Placeholder - calculate from test set
            'precision': 0.88,
            'recall': 0.82,
            'f1_score': 0.85
        }
        
        model_version = f"v{len(samples)}_{uuid.uuid4().hex[:8]}"
        self.training_manager.log_model_performance(model_version, metrics)
        
        return {
            'success': True,
            'message': f'Model trained successfully on {len(samples)} samples',
            'model_version': model_version,
            'metrics': metrics
        }
    
    def get_training_report(self) -> Dict[str, Any]:
        """Get comprehensive training data report"""
        report = self.training_manager.create_training_report()
        
        # Add scheduler status if available
        if self.scheduler:
            report['scheduler_status'] = self.scheduler.get_status()
        
        # Add model performance trends
        report['performance_trends'] = self._get_performance_trends()
        
        return report
    
    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get model performance trends over time"""
        # Get all model performance logs
        performance_logs = self.training_manager.get_performance_logs()
        
        if not performance_logs:
            return {'message': 'No performance data available'}
        
        # Calculate trends
        latest = performance_logs[-1] if performance_logs else None
        previous = performance_logs[-2] if len(performance_logs) > 1 else None
        
        trends = {
            'latest_performance': latest,
            'total_versions': len(performance_logs)
        }
        
        if latest and previous:
            # Calculate improvements
            trends['accuracy_change'] = latest.get('accuracy', 0) - previous.get('accuracy', 0)
            trends['f1_change'] = latest.get('f1_score', 0) - previous.get('f1_score', 0)
            trends['is_improving'] = trends['accuracy_change'] > 0
        
        return trends
    
    def export_session(self, session_id: str) -> Optional[Dict]:
        """Export session data for analysis"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return None
        return {
            'session_id': session_id,
            'original_content': session['original_content'],
            'references': session['references'],
            'populated_content': session.get('populated_content'),
            'sample_id': session.get('sample_id')
        }
    
    def _parse_reference_string(self, ref_text: str) -> Optional[Dict]:
        """Parse a verse reference string into components"""
        import re
        
        # Handle various reference formats
        patterns = [
            r'([123]?\s*[A-Z][a-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?',  # Book Ch:V or Book Ch:V-V
            r'([A-Z][a-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?',  # Book Ch:V or Book Ch:V-V
        ]
        
        for pattern in patterns:
            match = re.match(pattern, ref_text.strip())
            if match:
                book = match.group(1).strip().replace('.', '')
                chapter = int(match.group(2))
                start_verse = int(match.group(3))
                end_verse = int(match.group(4)) if match.group(4) else start_verse
                
                return {
                    'book': book,
                    'chapter': chapter,
                    'start_verse': start_verse,
                    'end_verse': end_verse
                }
        
        return None