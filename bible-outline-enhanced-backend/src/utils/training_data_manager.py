"""
Training Data Manager for ML Model
Collects, stores, and manages training data for continuous improvement
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sqlite3
from pathlib import Path

class TrainingDataManager:
    def __init__(self, db_path: str = 'training_data.db'):
        """
        Initialize training data manager
        
        Args:
            db_path: Path to SQLite database for training data
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for training data"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                processed_text TEXT,
                references TEXT,
                user_corrections TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_validated BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id INTEGER,
                feedback_type TEXT,
                feedback_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sample_id) REFERENCES training_samples (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                metrics TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_training_sample(self, original_text: str, references: List[Dict], 
                           processed_text: str = None, confidence: float = None) -> int:
        """
        Add a new training sample
        
        Returns:
            Sample ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_samples (original_text, processed_text, references, confidence_score)
            VALUES (?, ?, ?, ?)
        ''', (
            original_text,
            processed_text,
            json.dumps(references),
            confidence
        ))
        
        sample_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return sample_id
    
    def add_user_correction(self, sample_id: int, corrected_references: List[Dict]):
        """Add user corrections to a training sample"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE training_samples 
            SET user_corrections = ?, is_validated = 1
            WHERE id = ?
        ''', (json.dumps(corrected_references), sample_id))
        
        conn.commit()
        conn.close()
    
    def add_feedback(self, sample_id: int, feedback_type: str, feedback_data: Dict):
        """Add feedback for a training sample"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (sample_id, feedback_type, feedback_data)
            VALUES (?, ?, ?)
        ''', (sample_id, feedback_type, json.dumps(feedback_data)))
        
        conn.commit()
        conn.close()
    
    def get_validated_samples(self, limit: int = None) -> List[Dict]:
        """Get validated training samples"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, original_text, processed_text, references, user_corrections, confidence_score
            FROM training_samples
            WHERE is_validated = 1
            ORDER BY created_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        samples = []
        for row in rows:
            samples.append({
                'id': row[0],
                'original_text': row[1],
                'processed_text': row[2],
                'references': json.loads(row[3]) if row[3] else [],
                'user_corrections': json.loads(row[4]) if row[4] else [],
                'confidence_score': row[5]
            })
        
        return samples
    
    def export_for_training(self, output_path: str = 'training_data.json'):
        """Export validated samples for model training"""
        samples = self.get_validated_samples()
        
        training_data = {
            'version': datetime.now().isoformat(),
            'total_samples': len(samples),
            'samples': samples
        }
        
        with open(output_path, 'w') as f:
            json.dump(training_data, f, indent=2)
        
        print(f"Exported {len(samples)} training samples to {output_path}")
        return output_path
    
    def log_model_performance(self, model_version: str, metrics: Dict):
        """Log model performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_performance (model_version, metrics)
            VALUES (?, ?)
        ''', (
            model_version,
            json.dumps(metrics)
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_history(self) -> List[Dict]:
        """Get model performance history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT model_version, accuracy, precision, recall, f1_score, test_date
            FROM model_performance
            ORDER BY test_date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'model_version': row[0],
                'accuracy': row[1],
                'precision': row[2],
                'recall': row[3],
                'f1_score': row[4],
                'test_date': row[5]
            })
        
        return history
    
    def create_training_report(self) -> Dict:
        """Create a comprehensive training data report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM training_samples')
        total_samples = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM training_samples WHERE is_validated = 1')
        validated_samples = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(confidence_score) FROM training_samples WHERE confidence_score IS NOT NULL')
        avg_confidence = cursor.fetchone()[0]
        
        conn.close()
        
        # Get performance history
        performance = self.get_performance_history()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_samples': total_samples,
                'validated_samples': validated_samples,
                'total_feedback': total_feedback,
                'average_confidence': avg_confidence,
                'validation_rate': validated_samples / total_samples if total_samples > 0 else 0
            },
            'recent_performance': performance[:5] if performance else [],
            'recommendations': self._generate_recommendations(total_samples, validated_samples)
        }
        
        return report
    
    def _generate_recommendations(self, total_samples: int, validated_samples: int) -> List[str]:
        """Generate recommendations based on training data"""
        recommendations = []
        
        if validated_samples < 100:
            recommendations.append(f"Need more validated samples. Current: {validated_samples}, Recommended: 100+")
        
        if total_samples > 0:
            validation_rate = validated_samples / total_samples
            if validation_rate < 0.8:
                recommendations.append(f"Low validation rate ({validation_rate:.1%}). Review and validate more samples.")
        
        if total_samples < 500:
            recommendations.append("Collect more diverse training samples for better model performance.")
        
        return recommendations
    
    def get_feedback_count(self, sample_id: int) -> int:
        """Get feedback count for a specific sample"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM feedback WHERE sample_id = ?",
            (sample_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_recent_feedback(self, days: int = 7) -> List[Dict]:
        """Get recent feedback entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute(
            """
            SELECT f.*, s.original_text 
            FROM feedback f
            JOIN training_samples s ON f.sample_id = s.id
            WHERE f.timestamp >= ?
            ORDER BY f.timestamp DESC
            """,
            (cutoff_date.isoformat(),)
        )
        
        feedback_list = []
        for row in cursor.fetchall():
            feedback_data = json.loads(row[3]) if row[3] else {}
            feedback_list.append({
                'id': row[0],
                'sample_id': row[1],
                'feedback_type': row[2],
                'is_positive': feedback_data.get('is_positive', False),
                'corrections': feedback_data.get('corrections', []),
                'timestamp': row[4]
            })
        
        conn.close()
        return feedback_list
    
    def get_performance_logs(self) -> List[Dict]:
        """Get all model performance logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM model_performance
            ORDER BY timestamp ASC
            """
        )
        
        logs = []
        for row in cursor.fetchall():
            metrics = json.loads(row[2]) if row[2] else {}
            logs.append({
                'model_version': row[1],
                'accuracy': metrics.get('accuracy', 0),
                'precision': metrics.get('precision', 0),
                'recall': metrics.get('recall', 0),
                'f1_score': metrics.get('f1_score', 0),
                'timestamp': row[3]
            })
        
        conn.close()
        return logs