"""
PostgreSQL Session Manager using pg8000 (Python 3.13 compatible)
Uses pg8000 driver which is pure Python and works with all Python versions
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

try:
    import pg8000
    PG8000_AVAILABLE = True
except ImportError:
    PG8000_AVAILABLE = False
    print("pg8000 not available - PostgreSQL session manager disabled")

logger = logging.getLogger(__name__)

class PG8000SessionManager:
    def __init__(self, connection_string: str = None):
        """
        Initialize session manager with PostgreSQL database using pg8000
        
        Args:
            connection_string: PostgreSQL connection string
        """
        if not PG8000_AVAILABLE:
            raise ImportError("pg8000 is not available - cannot use PostgreSQL session manager")
            
        if connection_string is None:
            # Get from environment variable
            connection_string = os.getenv('DATABASE_URL')
            
        if not connection_string:
            raise ValueError("No PostgreSQL connection string provided")
            
        # Parse connection string
        self.connection_params = self._parse_connection_string(connection_string)
        self._init_database()
    
    def _parse_connection_string(self, url: str) -> dict:
        """Parse PostgreSQL connection string"""
        # Format: postgresql://user:password@host/database
        url = url.replace('postgresql://', '')
        
        # Split user:password@host/database
        auth_host = url.split('@')
        user_pass = auth_host[0].split(':')
        host_db = auth_host[1].split('/')
        
        # Handle host:port
        host_parts = host_db[0].split(':')
        host = host_parts[0]
        port = int(host_parts[1]) if len(host_parts) > 1 else 5432
        
        return {
            'user': user_pass[0],
            'password': user_pass[1],
            'host': host,
            'port': port,
            'database': host_db[1]
        }
    
    def _get_connection(self):
        """Get a new database connection"""
        return pg8000.connect(
            user=self.connection_params['user'],
            password=self.connection_params['password'],
            host=self.connection_params['host'],
            port=self.connection_params['port'],
            database=self.connection_params['database']
        )
        
    def _init_database(self):
        """Initialize the session table in PostgreSQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create sessions table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
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
            cursor.close()
            conn.close()
            logger.info("PostgreSQL session table initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL session table: {e}")
            raise
            
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """
        Save session data to PostgreSQL
        
        Args:
            session_id: Unique session identifier
            data: Session data to store
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert data to JSON string, handling special types
            json_data = json.dumps(data, default=str)
            
            logger.info(f"Saving session {session_id} to PostgreSQL")
            
            # Use UPSERT pattern
            cursor.execute('''
                INSERT INTO sessions (session_id, data, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (session_id) 
                DO UPDATE SET 
                    data = EXCLUDED.data,
                    updated_at = CURRENT_TIMESTAMP
            ''', (session_id, json_data))
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.debug(f"Session {session_id} saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            raise
                
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from PostgreSQL
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        try:
            logger.info(f"Retrieving session {session_id} from PostgreSQL")
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data FROM sessions WHERE session_id = %s
            ''', (session_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                logger.info(f"Session {session_id} found in PostgreSQL")
                return json.loads(result[0])
            else:
                logger.warning(f"Session {session_id} not found in PostgreSQL")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
            
    def delete_session(self, session_id: str):
        """
        Delete a session from PostgreSQL
        
        Args:
            session_id: Session identifier
        """
        try:
            conn = self._get_connection()
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
                
    def cleanup_old_sessions(self, hours: int = 24):
        """
        Remove sessions older than specified hours
        
        Args:
            hours: Number of hours to keep sessions
            
        Returns:
            Number of sessions deleted
        """
        try:
            conn = self._get_connection()
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
            return 0
            
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        try:
            conn = self._get_connection()
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
            return False