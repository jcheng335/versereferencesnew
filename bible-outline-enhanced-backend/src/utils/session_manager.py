"""
Session Manager for persistent session storage
Stores session data in SQLite database to survive server restarts
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SessionManager:
    def __init__(self, db_path: str = None):
        """
        Initialize session manager with SQLite database
        
        Args:
            db_path: Path to session database (creates if not exists)
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sessions.db')
        
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the session database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sessions_updated 
            ON sessions(updated_at)
        ''')
        
        conn.commit()
        conn.close()
        
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """
        Save session data to database
        
        Args:
            session_id: Unique session identifier
            data: Session data to store
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert data to JSON, handling special types
        json_data = json.dumps(data, default=str)
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_id, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, json_data))
        
        conn.commit()
        conn.close()
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from database
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
        
    def delete_session(self, session_id: str):
        """
        Delete a session from database
        
        Args:
            session_id: Session identifier
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
    def cleanup_old_sessions(self, hours: int = 24):
        """
        Remove sessions older than specified hours
        
        Args:
            hours: Number of hours to keep sessions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            DELETE FROM sessions 
            WHERE updated_at < ?
        ''', (cutoff_time,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
        
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 1 FROM sessions WHERE session_id = ? LIMIT 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None