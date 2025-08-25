"""
Automated Model Retraining Scheduler
Monitors training data and triggers retraining when thresholds are met
"""

import os
import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .training_data_manager import TrainingDataManager
from .hybrid_verse_detector import HybridVerseDetector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelScheduler:
    def __init__(
        self,
        training_manager: TrainingDataManager,
        detector: HybridVerseDetector,
        check_interval_hours: int = 24,
        min_new_samples: int = 100,
        min_feedback_count: int = 50,
        performance_threshold: float = 0.85
    ):
        """
        Initialize the model scheduler
        
        Args:
            training_manager: Training data manager instance
            detector: Hybrid verse detector instance
            check_interval_hours: Hours between retraining checks
            min_new_samples: Minimum new samples before retraining
            min_feedback_count: Minimum feedback items before retraining
            performance_threshold: Performance threshold to trigger retraining
        """
        self.training_manager = training_manager
        self.detector = detector
        self.check_interval_hours = check_interval_hours
        self.min_new_samples = min_new_samples
        self.min_feedback_count = min_feedback_count
        self.performance_threshold = performance_threshold
        
        self.last_training_time = datetime.now()
        self.last_sample_count = 0
        self.model_versions = []
        self.is_running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the automated scheduler"""
        if self.is_running:
            logger.info("Scheduler already running")
            return
            
        self.is_running = True
        
        # Schedule periodic checks
        schedule.every(self.check_interval_hours).hours.do(self.check_and_retrain)
        
        # Run scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"Model scheduler started, checking every {self.check_interval_hours} hours")
        
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Model scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    def check_and_retrain(self) -> Dict[str, Any]:
        """
        Check if retraining is needed and trigger if necessary
        
        Returns:
            Retraining result
        """
        logger.info("Checking if model retraining is needed...")
        
        # Get current statistics
        report = self.training_manager.create_training_report()
        
        should_retrain = False
        reasons = []
        
        # Check new samples threshold
        current_samples = report['total_samples']
        new_samples = current_samples - self.last_sample_count
        if new_samples >= self.min_new_samples:
            should_retrain = True
            reasons.append(f"New samples: {new_samples} >= {self.min_new_samples}")
            
        # Check feedback count
        feedback_count = report.get('total_feedback', 0)
        if feedback_count >= self.min_feedback_count:
            should_retrain = True
            reasons.append(f"Feedback count: {feedback_count} >= {self.min_feedback_count}")
            
        # Check performance degradation
        recent_performance = self._calculate_recent_performance()
        if recent_performance and recent_performance < self.performance_threshold:
            should_retrain = True
            reasons.append(f"Performance: {recent_performance:.2f} < {self.performance_threshold}")
            
        # Check time since last training
        time_since_training = datetime.now() - self.last_training_time
        if time_since_training > timedelta(days=7):
            should_retrain = True
            reasons.append(f"Time since last training: {time_since_training.days} days")
            
        if should_retrain:
            logger.info(f"Triggering retraining. Reasons: {', '.join(reasons)}")
            result = self._perform_retraining()
            
            if result['success']:
                self.last_training_time = datetime.now()
                self.last_sample_count = current_samples
                
                # Store model version
                self.model_versions.append({
                    'version': result['model_version'],
                    'timestamp': datetime.now(),
                    'metrics': result.get('metrics', {}),
                    'sample_count': current_samples
                })
                
            return result
        else:
            logger.info("No retraining needed at this time")
            return {
                'success': False,
                'message': 'No retraining needed',
                'checked_at': datetime.now().isoformat()
            }
            
    def _calculate_recent_performance(self) -> Optional[float]:
        """
        Calculate performance based on recent feedback
        
        Returns:
            Performance score or None if insufficient data
        """
        # Get recent feedback
        recent_feedback = self.training_manager.get_recent_feedback(days=7)
        
        if not recent_feedback:
            return None
            
        # Calculate accuracy based on positive vs negative feedback
        positive = sum(1 for f in recent_feedback if f.get('is_positive', False))
        total = len(recent_feedback)
        
        if total == 0:
            return None
            
        return positive / total
        
    def _perform_retraining(self) -> Dict[str, Any]:
        """
        Perform model retraining
        
        Returns:
            Training result
        """
        try:
            # Get validated training samples
            samples = self.training_manager.get_validated_samples()
            
            if len(samples) < 50:  # Minimum threshold
                return {
                    'success': False,
                    'error': f'Insufficient samples: {len(samples)} < 50'
                }
                
            # Prepare training data
            training_data = []
            for sample in samples:
                training_data.append({
                    'text': sample['original_text'],
                    'correct_references': sample.get('user_corrections') or sample['references']
                })
                
            # Train the model
            self.detector.train_model(training_data)
            
            # Calculate metrics (would be from validation set in production)
            metrics = self._evaluate_model(samples[-20:])  # Use last 20 as validation
            
            # Generate version ID
            version_id = f"auto_v{len(self.model_versions)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Log performance
            self.training_manager.log_model_performance(version_id, metrics)
            
            return {
                'success': True,
                'model_version': version_id,
                'metrics': metrics,
                'sample_count': len(samples),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Retraining failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _evaluate_model(self, validation_samples: list) -> Dict[str, float]:
        """
        Evaluate model performance on validation set
        
        Args:
            validation_samples: Samples to evaluate on
            
        Returns:
            Performance metrics
        """
        if not validation_samples:
            return {
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0
            }
            
        correct_predictions = 0
        total_predictions = 0
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for sample in validation_samples:
            text = sample['original_text']
            expected_refs = sample.get('user_corrections') or sample['references']
            
            # Get model predictions
            predicted_refs = self.detector.detect_verses(text, use_llm=False)  # Test without LLM
            
            # Convert to comparable format
            expected_set = {
                (r['book'], r['chapter'], r['start_verse'], r['end_verse'])
                for r in expected_refs
            }
            
            predicted_set = {
                (r.book, r.chapter, r.start_verse, r.end_verse)
                for r in predicted_refs
            }
            
            # Calculate metrics
            true_positives += len(expected_set & predicted_set)
            false_positives += len(predicted_set - expected_set)
            false_negatives += len(expected_set - predicted_set)
            
            if expected_set == predicted_set:
                correct_predictions += 1
            total_predictions += 1
            
        # Calculate final metrics
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
        
    def rollback_model(self, version_index: int = -2) -> bool:
        """
        Rollback to a previous model version
        
        Args:
            version_index: Index of version to rollback to (default: previous version)
            
        Returns:
            Success status
        """
        if len(self.model_versions) < 2:
            logger.warning("Not enough model versions for rollback")
            return False
            
        try:
            # Get target version
            target_version = self.model_versions[version_index]
            
            # Load the model (assuming models are saved with version names)
            model_path = f"models/verse_detector_{target_version['version']}.pkl"
            
            if os.path.exists(model_path):
                self.detector.load_model(model_path)
                logger.info(f"Rolled back to model version: {target_version['version']}")
                return True
            else:
                logger.error(f"Model file not found: {model_path}")
                return False
                
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        return {
            'is_running': self.is_running,
            'last_training_time': self.last_training_time.isoformat(),
            'last_sample_count': self.last_sample_count,
            'check_interval_hours': self.check_interval_hours,
            'model_versions': len(self.model_versions),
            'current_version': self.model_versions[-1] if self.model_versions else None
        }