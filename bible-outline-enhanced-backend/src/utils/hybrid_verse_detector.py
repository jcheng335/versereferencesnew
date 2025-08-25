"""
Hybrid Verse Detection System
Combines regex patterns, OpenAI LLM, and ML models for accurate verse detection and placement
"""

import os
import re
import json
import pickle
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from openai import OpenAI

# ML components are optional - system works with just regex + LLM
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    import pandas as pd
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML libraries not available - using regex + LLM only")
from datetime import datetime

@dataclass
class VerseReference:
    """Data class for verse references"""
    book: str
    chapter: int
    start_verse: int
    end_verse: int
    context: str
    confidence: float
    insertion_point: int
    original_text: str

class HybridVerseDetector:
    def __init__(self, openai_api_key: str = None, model_path: str = None):
        """
        Initialize the hybrid verse detector
        
        Args:
            openai_api_key: OpenAI API key for LLM validation
            model_path: Path to trained ML model
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for hybrid verse detection. Set OPENAI_API_KEY environment variable.")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        self.model_path = model_path
        self.ml_model = None
        self.vectorizer = None
        
        # Load ML model if exists
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        # Enhanced regex patterns for verse detection
        self.verse_patterns = [
            # Standard format: Book Chapter:Verse
            r'([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?',
            # With "cf." prefix
            r'cf\.\s+([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)(?:-(\d+))?',
            # Verse only references
            r'v{1,2}\.\s*(\d+)(?:-(\d+))?',
            # Multiple verses with commas
            r'([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+(?:,\s*\d+)+)',
            # Chapter and verse ranges
            r'([123]?\s*[A-Za-z]+\.?)\s+(\d+):(\d+)-(\d+):(\d+)',
        ]
        
        # Book name variations
        self.book_variations = self._load_book_variations()
        
        # Training data storage
        self.training_data = []
        self.feedback_data = []
    
    def _load_book_variations(self) -> Dict[str, str]:
        """Load comprehensive book name variations"""
        return {
            # Old Testament
            'Gen': 'Genesis', 'Genesis': 'Genesis', 'Ge': 'Genesis',
            'Exo': 'Exodus', 'Exodus': 'Exodus', 'Ex': 'Exodus',
            'Lev': 'Leviticus', 'Leviticus': 'Leviticus', 'Le': 'Leviticus',
            'Num': 'Numbers', 'Numbers': 'Numbers', 'Nu': 'Numbers',
            'Deut': 'Deuteronomy', 'Deuteronomy': 'Deuteronomy', 'De': 'Deuteronomy', 'Dt': 'Deuteronomy',
            
            # Gospels
            'Matt': 'Matthew', 'Matthew': 'Matthew', 'Mt': 'Matthew', 'Mat': 'Matthew',
            'Mark': 'Mark', 'Mk': 'Mark', 'Mr': 'Mark',
            'Luke': 'Luke', 'Lk': 'Luke', 'Lu': 'Luke',
            'John': 'John', 'Jn': 'John', 'Joh': 'John',
            
            # Paul's Letters
            'Rom': 'Romans', 'Romans': 'Romans', 'Ro': 'Romans',
            'Cor': 'Corinthians', '1Cor': '1 Corinthians', '2Cor': '2 Corinthians',
            '1 Cor': '1 Corinthians', '2 Cor': '2 Corinthians',
            'Gal': 'Galatians', 'Galatians': 'Galatians', 'Ga': 'Galatians',
            'Eph': 'Ephesians', 'Ephesians': 'Ephesians', 'Ephes': 'Ephesians',
            'Phil': 'Philippians', 'Philippians': 'Philippians', 'Php': 'Philippians',
            'Col': 'Colossians', 'Colossians': 'Colossians',
            
            # Add more as needed...
        }
    
    def detect_verses(self, text: str, use_llm: bool = True) -> List[VerseReference]:
        """
        Detect verse references using hybrid approach
        
        Args:
            text: Input text to analyze
            use_llm: Whether to use LLM for validation
        
        Returns:
            List of detected verse references
        """
        # Step 1: Regex-based initial detection
        candidates = self._regex_detection(text)
        
        # Step 2: ML model scoring (if available)
        if ML_AVAILABLE and self.ml_model:
            candidates = self._ml_scoring(candidates, text)
        
        # Step 3: LLM validation and context understanding
        if use_llm and self.openai_client:
            candidates = self._llm_validation(candidates, text)
        
        # Step 4: Determine optimal insertion points
        references = self._determine_insertion_points(candidates, text)
        
        return references
    
    def _regex_detection(self, text: str) -> List[Dict]:
        """Initial regex-based verse detection"""
        candidates = []
        lines = text.split('\n')
        
        for line_idx, line in enumerate(lines):
            for pattern in self.verse_patterns:
                for match in re.finditer(pattern, line):
                    candidate = {
                        'match': match,
                        'line_idx': line_idx,
                        'line': line,
                        'pattern': pattern,
                        'confidence': 0.5  # Base confidence
                    }
                    candidates.append(candidate)
        
        return candidates
    
    def _ml_scoring(self, candidates: List[Dict], text: str) -> List[Dict]:
        """Score candidates using ML model"""
        if not ML_AVAILABLE or not self.ml_model or not candidates:
            return candidates
        
        # Extract features for each candidate
        features = []
        for candidate in candidates:
            feature_vec = self._extract_features(candidate, text)
            features.append(feature_vec)
        
        # Predict confidence scores
        if features:
            X = self.vectorizer.transform(features)
            scores = self.ml_model.predict_proba(X)[:, 1]  # Probability of being valid
            
            for i, candidate in enumerate(candidates):
                candidate['confidence'] = scores[i]
        
        return candidates
    
    def _llm_validation(self, candidates: List[Dict], text: str) -> List[Dict]:
        """Validate and enhance candidates using OpenAI LLM"""
        if not candidates:
            return candidates
        
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(candidates, text)
            
            # Call OpenAI API
            if not self.openai_client:
                print("OpenAI client not initialized")
                return candidates
                
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Bible verse reference expert. Analyze the given text and:
                        1. Validate if the detected references are correct
                        2. Identify the best insertion point for each verse (after complete sentences/thoughts)
                        3. Detect any missed references
                        4. Return JSON with validated references and insertion instructions"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Parse LLM response
            llm_result = json.loads(response.choices[0].message.content)
            
            # Update candidates based on LLM feedback
            validated_candidates = self._process_llm_response(candidates, llm_result)
            
            return validated_candidates
            
        except Exception as e:
            print(f"LLM validation error: {e}")
            return candidates
    
    def _prepare_llm_context(self, candidates: List[Dict], text: str) -> str:
        """Prepare context for LLM analysis"""
        context = {
            "full_text": text,
            "detected_references": [
                {
                    "text": c['match'].group(0),
                    "line": c['line'],
                    "line_number": c['line_idx']
                }
                for c in candidates
            ],
            "instructions": "Validate these references and determine optimal insertion points"
        }
        return json.dumps(context)
    
    def _process_llm_response(self, candidates: List[Dict], llm_result: Dict) -> List[Dict]:
        """Process LLM response and update candidates"""
        validated = []
        
        for candidate in candidates:
            # Check if LLM validated this reference
            match_text = candidate['match'].group(0)
            
            for llm_ref in llm_result.get('validated_references', []):
                if llm_ref.get('original_text') == match_text:
                    candidate['confidence'] = llm_ref.get('confidence', 0.9)
                    candidate['insertion_line'] = llm_ref.get('insertion_line', candidate['line_idx'])
                    candidate['llm_validated'] = True
                    validated.append(candidate)
                    break
        
        return validated
    
    def _determine_insertion_points(self, candidates: List[Dict], text: str) -> List[VerseReference]:
        """Determine optimal insertion points for verses"""
        references = []
        lines = text.split('\n')
        
        for candidate in candidates:
            if candidate.get('confidence', 0) < 0.3:  # Skip low confidence
                continue
            
            match = candidate['match']
            line_idx = candidate.get('insertion_line', candidate['line_idx'])
            
            # Find end of complete thought/sentence
            insertion_point = self._find_sentence_end(lines, line_idx)
            
            # Extract book, chapter, verse information
            groups = match.groups()
            book = self._normalize_book_name(groups[0]) if groups[0] else None
            
            if book:
                ref = VerseReference(
                    book=book,
                    chapter=int(groups[1]) if len(groups) > 1 and groups[1] else 0,
                    start_verse=int(groups[2]) if len(groups) > 2 and groups[2] else 0,
                    end_verse=int(groups[3]) if len(groups) > 3 and groups[3] else int(groups[2]) if len(groups) > 2 and groups[2] else 0,
                    context=candidate['line'],
                    confidence=candidate.get('confidence', 0.5),
                    insertion_point=insertion_point,
                    original_text=match.group(0)
                )
                references.append(ref)
        
        return references
    
    def _find_sentence_end(self, lines: List[str], start_idx: int) -> int:
        """Find the end of a complete sentence or thought"""
        # Look for sentence ending punctuation
        current_idx = start_idx
        
        while current_idx < len(lines):
            line = lines[current_idx].strip()
            
            # Check if line ends with sentence-ending punctuation
            if line and line[-1] in '.!?:;':
                return current_idx
            
            # Check if next line starts with outline marker
            if current_idx + 1 < len(lines):
                next_line = lines[current_idx + 1].strip()
                if re.match(r'^[A-Z]\.|^[IVX]+\.|^\d+\.|^[a-z]\.', next_line):
                    return current_idx
            
            current_idx += 1
        
        return start_idx
    
    def _normalize_book_name(self, book_text: str) -> Optional[str]:
        """Normalize book name to standard form"""
        if not book_text:
            return None
        
        book_text = book_text.strip().replace('.', '')
        return self.book_variations.get(book_text, book_text)
    
    def _extract_features(self, candidate: Dict, full_text: str) -> str:
        """Extract features for ML model"""
        # Simple feature extraction - can be enhanced
        features = {
            'line_text': candidate['line'],
            'has_colon': ':' in candidate['line'],
            'has_dash': '-' in candidate['line'],
            'line_length': len(candidate['line']),
            'position_in_text': candidate['line_idx'] / len(full_text.split('\n')),
            'starts_with_outline': bool(re.match(r'^[A-Z]\.|^[IVX]+\.|^\d+\.', candidate['line'].strip()))
        }
        return ' '.join([f"{k}:{v}" for k, v in features.items()])
    
    def train_model(self, training_data: List[Dict]):
        """
        Train ML model on labeled data
        
        Args:
            training_data: List of dictionaries with 'text', 'references', and 'correct_placements'
        """
        if not ML_AVAILABLE:
            print("ML libraries not available - cannot train model")
            return
            
        if not training_data:
            print("No training data provided")
            return
        
        # Prepare training dataset
        X = []
        y = []
        
        for sample in training_data:
            text = sample['text']
            correct_refs = sample['correct_references']
            
            # Extract features from correct references
            for ref in correct_refs:
                features = self._extract_features({'line': ref['context'], 'line_idx': ref['line_idx']}, text)
                X.append(features)
                y.append(1)  # Correct reference
            
            # Add negative samples (incorrect references)
            if 'incorrect_references' in sample:
                for ref in sample['incorrect_references']:
                    features = self._extract_features({'line': ref['context'], 'line_idx': ref['line_idx']}, text)
                    X.append(features)
                    y.append(0)  # Incorrect reference
        
        # Vectorize features
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=100)
            X_vec = self.vectorizer.fit_transform(X)
            
            # Train Random Forest model
            self.ml_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.ml_model.fit(X_vec, y)
        else:
            print("ML libraries not available - cannot train model")
        
        # Save model
        self.save_model()
        
        print(f"Model trained on {len(training_data)} samples")
    
    def save_model(self, path: str = None):
        """Save trained model and vectorizer"""
        if not self.ml_model:
            print("No model to save")
            return
        
        save_path = path or self.model_path or 'verse_detector_model.pkl'
        
        model_data = {
            'model': self.ml_model,
            'vectorizer': self.vectorizer,
            'book_variations': self.book_variations,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {save_path}")
    
    def load_model(self, path: str):
        """Load trained model and vectorizer"""
        if not os.path.exists(path):
            print(f"Model file not found: {path}")
            return
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.ml_model = model_data.get('model')
        self.vectorizer = model_data.get('vectorizer')
        self.book_variations.update(model_data.get('book_variations', {}))
        
        print(f"Model loaded from {path}")
    
    def add_feedback(self, original_text: str, corrected_references: List[Dict]):
        """
        Add user feedback for continuous improvement
        
        Args:
            original_text: Original input text
            corrected_references: User-corrected reference placements
        """
        feedback = {
            'text': original_text,
            'timestamp': datetime.now().isoformat(),
            'corrected_references': corrected_references
        }
        
        self.feedback_data.append(feedback)
        
        # Auto-retrain if enough feedback collected
        if len(self.feedback_data) >= 10:
            self.retrain_with_feedback()
    
    def retrain_with_feedback(self):
        """Retrain model with accumulated feedback"""
        if not self.feedback_data:
            return
        
        # Convert feedback to training data format
        training_data = []
        for feedback in self.feedback_data:
            training_sample = {
                'text': feedback['text'],
                'correct_references': feedback['corrected_references']
            }
            training_data.append(training_sample)
        
        # Retrain model
        self.train_model(training_data)
        
        # Clear processed feedback
        self.feedback_data = []
        
        print(f"Model retrained with {len(training_data)} feedback samples")
    
    def export_training_data(self, path: str = 'training_data.json'):
        """Export training data for analysis or backup"""
        data = {
            'training_samples': self.training_data,
            'feedback_samples': self.feedback_data,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Training data exported to {path}")