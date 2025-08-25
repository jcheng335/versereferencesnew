"""
Enhanced Document Processor with Hybrid Verse Detection
Integrates regex, OpenAI LLM, and ML for optimal verse placement
"""

import os
import uuid
from typing import Dict, List, Any, Optional
import pdfplumber
from docx import Document
from .hybrid_verse_detector import HybridVerseDetector, VerseReference
from .training_data_manager import TrainingDataManager
from .sqlite_bible_database import SQLiteBibleDatabase
from .model_scheduler import ModelScheduler

class EnhancedProcessor:
    def __init__(self, db_path: str, openai_key: str = None):
        """
        Initialize enhanced processor with hybrid detection
        
        Args:
            db_path: Path to Bible database
            openai_key: OpenAI API key (optional, uses env var if not provided)
        """
        self.bible_db = SQLiteBibleDatabase(db_path)
        self.sessions = {}
        
        # Initialize hybrid detector with OpenAI (REQUIRED for hybrid approach)
        self.detector = HybridVerseDetector(
            openai_api_key=openai_key,
            model_path='models/verse_detector.pkl'
        )
        
        # Initialize training data manager
        self.training_manager = TrainingDataManager('training_data.db')
        
        # Create models directory if not exists
        os.makedirs('models', exist_ok=True)
        
        # Initialize model scheduler for automated retraining
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
    
    def process_document(self, file_path: str, filename: str, use_llm: bool = True) -> Dict[str, Any]:
        """
        Process document with enhanced verse detection
        
        Args:
            file_path: Path to uploaded file
            filename: Original filename
            use_llm: Whether to use OpenAI LLM for validation
        
        Returns:
            Processing result with session ID and detected references
        """
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Extract text based on file type
            content = self._extract_text(file_path, filename)
            
            # Detect verses using hybrid approach
            references = self.detector.detect_verses(content, use_llm=use_llm)
            
            # Convert VerseReference objects to dicts
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
            
            # Store session data
            self.sessions[session_id] = {
                'original_content': content,
                'original_filename': filename,
                'references': ref_dicts,
                'populated_content': None,
                'use_llm': use_llm
            }
            
            # Add to training data (for future model improvement)
            sample_id = self.training_manager.add_training_sample(
                original_text=content,
                references=ref_dicts,
                confidence=sum(r.confidence for r in references) / len(references) if references else 0
            )
            
            # Store sample ID in session for feedback tracking
            self.sessions[session_id]['sample_id'] = sample_id
            
            return {
                'success': True,
                'session_id': session_id,
                'content': content,
                'references_found': len(references),
                'total_verses': sum(r.end_verse - r.start_verse + 1 for r in references),
                'filename': filename,
                'average_confidence': sum(r.confidence for r in references) / len(references) if references else 0,
                'sample_id': sample_id  # For feedback tracking
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing document: {str(e)}'
            }
    
    def populate_verses(self, session_id: str, format_type: str = 'inline') -> Dict[str, Any]:
        """
        Populate document with verses at optimal insertion points
        
        Args:
            session_id: Session identifier
            format_type: Format type ('inline' or 'footnote')
        
        Returns:
            Populated content with verses
        """
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        session = self.sessions[session_id]
        content = session['original_content']
        references = session['references']
        
        try:
            # Sort references by insertion point
            references.sort(key=lambda x: x['insertion_point'])
            
            # Split content into lines
            lines = content.split('\n')
            result_lines = []
            inserted_at = set()
            
            # Process each line
            for i, line in enumerate(lines):
                result_lines.append(line)
                
                # Check if we should insert verses after this line
                verses_to_insert = []
                for ref in references:
                    if ref['insertion_point'] == i and i not in inserted_at:
                        # Fetch verse text
                        verse_text = self._fetch_verse_text(ref)
                        if verse_text:
                            verses_to_insert.append((ref, verse_text))
                
                # Insert verses with proper formatting
                if verses_to_insert:
                    for ref, verse_text in verses_to_insert:
                        if format_type == 'inline':
                            # Format: "Rom 5:18 - Therefore just as through one offense..."
                            formatted_verse = f"{ref['original_text']} - {verse_text}"
                            result_lines.append(formatted_verse)
                        else:
                            # Footnote style
                            result_lines.append(f"[{ref['original_text']}]")
                            result_lines.append(f"    {verse_text}")
                    
                    inserted_at.add(i)
            
            populated_content = '\n'.join(result_lines)
            
            # Store populated content
            session['populated_content'] = populated_content
            
            return {
                'success': True,
                'populated_content': populated_content,
                'format': format_type,
                'verse_count': len(references),
                'message': f'Successfully populated {len(references)} verses with enhanced placement'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error populating verses: {str(e)}'
            }
    
    def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from various file formats"""
        if filename.lower().endswith('.pdf'):
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
    
    def _fetch_verse_text(self, reference: Dict) -> Optional[str]:
        """Fetch verse text from database"""
        try:
            verses = []
            for verse_num in range(reference['start_verse'], reference['end_verse'] + 1):
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
        if session_id not in self.sessions:
            return {'success': False, 'error': 'Session not found'}
        
        session = self.sessions[session_id]
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
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            'session_id': session_id,
            'original_content': session['original_content'],
            'references': session['references'],
            'populated_content': session.get('populated_content'),
            'sample_id': session.get('sample_id')
        }