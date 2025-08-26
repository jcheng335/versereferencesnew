"""
PostgreSQL Bible Database Interface
Uses pg8000 driver which is pure Python and compatible with Python 3.13
"""

import os
import logging
from typing import List, Dict, Optional, Tuple

# Use pg8000 which is pure Python and works with Python 3.13
try:
    import pg8000
    PG8000_AVAILABLE = True
except ImportError:
    PG8000_AVAILABLE = False
    print("pg8000 not available - PostgreSQL Bible database disabled")

logger = logging.getLogger(__name__)

class PostgresBibleDatabase:
    def __init__(self, connection_string: str = None):
        """
        Initialize PostgreSQL Bible database connection
        
        Args:
            connection_string: PostgreSQL connection string
        """
        if not PG8000_AVAILABLE:
            raise ImportError("pg8000 is required for PostgreSQL Bible database")
            
        if connection_string is None:
            # Get from environment variable
            connection_string = os.getenv('DATABASE_URL')
            
        if not connection_string:
            raise ValueError("No PostgreSQL connection string provided")
            
        # Parse connection string
        self.connection_params = self._parse_connection_string(connection_string)
        
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
    
    def get_verse(self, book_name: str, chapter: int, verse_num: int) -> Optional[str]:
        """
        Get a single verse from the database
        
        Args:
            book: Book abbreviation (e.g., 'Rom', 'John')
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Verse text or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Try exact book name match first
            cursor.execute('''
                SELECT v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE b.name = %s AND v.chapter = %s AND v.verse = %s
            ''', (book_name, chapter, verse_num))
            
            result = cursor.fetchone()
            if result:
                cursor.close()
                conn.close()
                return result[0]
            
            # Try abbreviation match
            cursor.execute('''
                SELECT v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE b.abbreviation = %s AND v.chapter = %s AND v.verse = %s
            ''', (book_name, chapter, verse_num))
            
            result = cursor.fetchone()
            if result:
                cursor.close()
                conn.close()
                return result[0]
            
            # Try book_abbreviations table
            cursor.execute('''
                SELECT v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                JOIN book_abbreviations ba ON b.id = ba.book_id
                WHERE ba.abbreviation = %s AND v.chapter = %s AND v.verse = %s
                LIMIT 1
            ''', (book_name, chapter, verse_num))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting verse {book_name} {chapter}:{verse_num}: {e}")
            return None
            
    def lookup_verse(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """
        Alias for get_verse to maintain compatibility with SQLiteBibleDatabase
        
        Args:
            book: Book abbreviation (e.g., 'Rom', 'John')
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Verse text or None if not found
        """
        return self.get_verse(book, chapter, verse)
    
    def get_verses_range(self, book: str, chapter: int, start_verse: int, end_verse: int) -> List[Tuple[int, str]]:
        """
        Get a range of verses from the database
        
        Args:
            book: Book abbreviation
            chapter: Chapter number
            start_verse: Starting verse number
            end_verse: Ending verse number
            
        Returns:
            List of (verse_number, text) tuples
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT verse_number, text 
                FROM bible_verses 
                WHERE book = %s AND chapter = %s 
                AND verse_number >= %s AND verse_number <= %s
                ORDER BY verse_number
                """,
                (book, chapter, start_verse, end_verse)
            )
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting verse range {book} {chapter}:{start_verse}-{end_verse}: {e}")
            return []
    
    def get_chapter(self, book: str, chapter: int) -> List[Tuple[int, str]]:
        """
        Get all verses in a chapter
        
        Args:
            book: Book abbreviation
            chapter: Chapter number
            
        Returns:
            List of (verse_number, text) tuples
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT verse_number, text 
                FROM bible_verses 
                WHERE book = %s AND chapter = %s
                ORDER BY verse_number
                """,
                (book, chapter)
            )
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting chapter {book} {chapter}: {e}")
            return []
    
    def search_verses(self, search_text: str, limit: int = 10) -> List[Dict]:
        """
        Search for verses containing specific text
        
        Args:
            search_text: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of verse dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT book, chapter, verse_number, text 
                FROM bible_verses 
                WHERE text ILIKE %s
                LIMIT %s
                """,
                (f'%{search_text}%', limit)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'book': row[0],
                    'chapter': row[1],
                    'verse': row[2],
                    'text': row[3]
                })
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching verses for '{search_text}': {e}")
            return []
    
    def get_books(self) -> List[str]:
        """
        Get list of all books in the database
        
        Returns:
            List of book abbreviations
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT DISTINCT book FROM bible_verses ORDER BY book"
            )
            
            books = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return books
            
        except Exception as e:
            logger.error(f"Error getting books: {e}")
            return []
    
    def verse_exists(self, book: str, chapter: int, verse: int) -> bool:
        """
        Check if a verse exists in the database
        
        Args:
            book: Book abbreviation
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            True if verse exists, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 1 FROM bible_verses 
                WHERE book = %s AND chapter = %s AND verse_number = %s
                LIMIT 1
                """,
                (book, chapter, verse)
            )
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking verse existence {book} {chapter}:{verse}: {e}")
            return False