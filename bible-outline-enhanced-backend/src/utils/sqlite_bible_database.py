import sqlite3
import os
from typing import List, Dict, Optional

class SQLiteBibleDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to the database in the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            db_path = os.path.join(project_root, 'bible_verses.db')
        
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
        except Exception as e:
            print(f"Error connecting to database: {e}")
    
    def get_verse(self, book_name: str, chapter: int, verse: int) -> Optional[str]:
        """Get a specific verse text"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # Try exact book name first
            cursor.execute('''
                SELECT v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE b.name = ? AND v.chapter = ? AND v.verse = ?
            ''', (book_name, chapter, verse))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # Try with abbreviations
            cursor.execute('''
                SELECT v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                JOIN book_abbreviations ba ON b.id = ba.book_id
                WHERE ba.abbreviation = ? AND v.chapter = ? AND v.verse = ?
            ''', (book_name, chapter, verse))
            
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting verse: {e}")
            return None
    
    def lookup_verse(self, book_name: str, chapter: int, verse: int) -> Optional[Dict]:
        """Look up a single verse with full information"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # Try exact book name first
            cursor.execute('''
                SELECT b.name, b.abbreviation, v.chapter, v.verse, v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE b.name = ? AND v.chapter = ? AND v.verse = ?
            ''', (book_name, chapter, verse))
            
            result = cursor.fetchone()
            if result:
                return {
                    'book_name': result[0],
                    'book_abbreviation': result[1],
                    'chapter': result[2],
                    'verse': result[3],
                    'text': result[4],
                    'reference': f"{result[1]} {result[2]}:{result[3]}"
                }
            
            # Try with abbreviations
            cursor.execute('''
                SELECT b.name, b.abbreviation, v.chapter, v.verse, v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                JOIN book_abbreviations ba ON b.id = ba.book_id
                WHERE ba.abbreviation = ? AND v.chapter = ? AND v.verse = ?
            ''', (book_name, chapter, verse))
            
            result = cursor.fetchone()
            if result:
                return {
                    'book_name': result[0],
                    'book_abbreviation': result[1],
                    'chapter': result[2],
                    'verse': result[3],
                    'text': result[4],
                    'reference': f"{result[1]} {result[2]}:{result[3]}"
                }
            
            return None
        except Exception as e:
            print(f"Error looking up verse: {e}")
            return None
    
    def lookup_verses_by_references(self, references: List[str]) -> List[Dict]:
        """Look up multiple verses from reference strings"""
        from src.utils.verse_parser import VerseParser
        
        results = []
        parser = VerseParser()
        
        for reference in references:
            try:
                parsed_refs = parser.parse_reference(reference)
                for ref in parsed_refs:
                    verse_data = self.lookup_verse(ref['book'], ref['chapter'], ref['verse'])
                    if verse_data:
                        verse_data['original_reference'] = reference
                        results.append(verse_data)
            except Exception as e:
                print(f"Error parsing reference '{reference}': {e}")
        
        return results
    
    def search_verses(self, query: str, limit: int = 50) -> List[Dict]:
        """Search verses by text content"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT b.name, b.abbreviation, v.chapter, v.verse, v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE v.text LIKE ? 
                ORDER BY b.book_order, v.chapter, v.verse
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'book_name': row[0],
                    'book_abbreviation': row[1],
                    'chapter': row[2],
                    'verse': row[3],
                    'text': row[4],
                    'reference': f"{row[1]} {row[2]}:{row[3]}"
                })
            
            return results
        except Exception as e:
            print(f"Error searching verses: {e}")
            return []
    
    def get_all_books(self) -> List[Dict]:
        """Get all books in the Bible"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT name, abbreviation, testament, book_order, total_chapters 
                FROM books 
                ORDER BY book_order
            ''')
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'name': row[0],
                    'abbreviation': row[1],
                    'testament': row[2],
                    'book_order': row[3],
                    'total_chapters': row[4]
                })
            
            return results
        except Exception as e:
            print(f"Error getting books: {e}")
            return []
    
    def get_book_by_name(self, name: str) -> Optional[Dict]:
        """Get book information by name or abbreviation"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # Try exact book name first
            cursor.execute('''
                SELECT name, abbreviation, testament, book_order, total_chapters 
                FROM books 
                WHERE name = ?
            ''', (name,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'name': result[0],
                    'abbreviation': result[1],
                    'testament': result[2],
                    'book_order': result[3],
                    'total_chapters': result[4]
                }
            
            # Try with abbreviations
            cursor.execute('''
                SELECT b.name, b.abbreviation, b.testament, b.book_order, b.total_chapters 
                FROM books b
                JOIN book_abbreviations ba ON b.id = ba.book_id
                WHERE ba.abbreviation = ?
            ''', (name,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'name': result[0],
                    'abbreviation': result[1],
                    'testament': result[2],
                    'book_order': result[3],
                    'total_chapters': result[4]
                }
            
            return None
        except Exception as e:
            print(f"Error getting book: {e}")
            return None
    
    def get_chapter_verses(self, book_name: str, chapter: int) -> List[Dict]:
        """Get all verses in a specific chapter"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT b.name, b.abbreviation, v.chapter, v.verse, v.text 
                FROM verses v 
                JOIN books b ON v.book_id = b.id 
                WHERE (b.name = ? OR b.id IN (
                    SELECT ba.book_id FROM book_abbreviations ba WHERE ba.abbreviation = ?
                )) AND v.chapter = ?
                ORDER BY v.verse
            ''', (book_name, book_name, chapter))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'book_name': row[0],
                    'book_abbreviation': row[1],
                    'chapter': row[2],
                    'verse': row[3],
                    'text': row[4],
                    'reference': f"{row[1]} {row[2]}:{row[3]}"
                })
            
            return results
        except Exception as e:
            print(f"Error getting chapter verses: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        if not self.conn:
            return {}
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM books')
            book_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM verses')
            verse_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM book_abbreviations')
            abbrev_count = cursor.fetchone()[0]
            
            return {
                'books': book_count,
                'verses': verse_count,
                'abbreviations': abbrev_count
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

