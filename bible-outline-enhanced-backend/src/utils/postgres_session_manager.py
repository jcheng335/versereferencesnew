"""
PostgreSQL Session Manager for persistent session storage on Render
Uses PostgreSQL database for production-ready session persistence
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("psycopg2 not available - PostgreSQL session manager disabled")

logger = logging.getLogger(__name__)

class PostgresSessionManager:
    def __init__(self, connection_string: str = None):
        """
        Initialize session manager with PostgreSQL database
        
        Args:
            connection_string: PostgreSQL connection string (uses DATABASE_URL env var if not provided)
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is not available - cannot use PostgreSQL session manager")
            
        if connection_string is None:
            # Get from environment variable (Render provides this)
            connection_string = os.getenv('DATABASE_URL')
            
            # If no DATABASE_URL, fall back to internal connection string
            if not connection_string:
                # Internal connection string for Render PostgreSQL
                connection_string = os.getenv('POSTGRES_INTERNAL_URL', '')
        
        self.connection_string = connection_string
        
        # Only initialize if we have a connection string
        if self.connection_string:
            self._init_database()
        else:
            logger.warning("No PostgreSQL connection available, sessions will not persist")
            
    def _get_connection(self):
        """Get a new database connection"""
        if not self.connection_string:
            return None
        return psycopg2.connect(self.connection_string)
        
    def _init_database(self):
        """Initialize the session table in PostgreSQL"""
        try:
            conn = self._get_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Create sessions table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    data JSONB NOT NULL,
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
            cursor.close()
            conn.close()
            logger.info("PostgreSQL session table initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL session table: {e}")
            
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """
        Save session data to PostgreSQL
        
        Args:
            session_id: Unique session identifier
            data: Session data to store
        """
        conn = self._get_connection()
        if not conn:
            logger.warning("No database connection, session not saved")
            return
            
        try:
            cursor = conn.cursor()
            
            # Use JSONB for efficient storage and querying
            cursor.execute('''
                INSERT INTO sessions (session_id, data, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (session_id) 
                DO UPDATE SET 
                    data = EXCLUDED.data,
                    updated_at = CURRENT_TIMESTAMP
            ''', (session_id, json.dumps(data)))
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.debug(f"Session {session_id} saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            if conn:
                conn.rollback()
                conn.close()
                
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from PostgreSQL
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        conn = self._get_connection()
        if not conn:
            logger.warning("No database connection, returning None")
            return None
            
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute('''
                SELECT data FROM sessions WHERE session_id = %s
            ''', (session_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return result['data']
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            if conn:
                conn.close()
            return None
            
    def delete_session(self, session_id: str):
        """
        Delete a session from PostgreSQL
        
        Args:
            session_id: Session identifier
        """
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM sessions WHERE session_id = %s
            ''', (session_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.debug(f"Session {session_id} deleted")
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            if conn:
                conn.rollback()
                conn.close()
                
    def cleanup_old_sessions(self, hours: int = 24):
        """
        Remove sessions older than specified hours
        
        Args:
            hours: Number of hours to keep sessions
            
        Returns:
            Number of sessions deleted
        """
        conn = self._get_connection()
        if not conn:
            return 0
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM sessions 
                WHERE updated_at < NOW() - INTERVAL '%s hours'
            ''', (hours,))
            
            deleted = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old sessions")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return 0
            
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        conn = self._get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 1 FROM sessions WHERE session_id = %s LIMIT 1
            ''', (session_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Failed to check session existence {session_id}: {e}")
            if conn:
                conn.close()
            return False