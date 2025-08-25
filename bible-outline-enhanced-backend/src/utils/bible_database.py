from typing import List, Dict, Optional
from src.models.bible import Book, Verse, BookAbbreviation, db
from src.utils.verse_parser import VerseParser

class BibleDatabase:
    def __init__(self):
        self.parser = VerseParser()
    
    def lookup_verse(self, book_name: str, chapter: int, verse: int) -> Optional[Dict]:
        """Look up a single verse"""
        book_id = self.parser._get_book_id(book_name)
        if not book_id:
            return None
        
        verse_obj = Verse.query.filter_by(
            book_id=book_id,
            chapter=chapter,
            verse=verse
        ).first()
        
        return verse_obj.to_dict() if verse_obj else None
    
    def lookup_verses(self, references: List[str]) -> List[Dict]:
        """Look up multiple verses from reference strings"""
        results = []
        
        for reference in references:
            parsed_refs = self.parser.parse_reference(reference)
            for ref in parsed_refs:
                verse_obj = Verse.query.filter_by(
                    book_id=ref['book_id'],
                    chapter=ref['chapter'],
                    verse=ref['verse']
                ).first()
                
                if verse_obj:
                    verse_dict = verse_obj.to_dict()
                    verse_dict['original_reference'] = reference
                    results.append(verse_dict)
        
        return results
    
    def lookup_verses_by_parsed_refs(self, parsed_refs: List[Dict]) -> List[Dict]:
        """Look up verses from already parsed reference data"""
        results = []
        
        for ref in parsed_refs:
            verse_obj = Verse.query.filter_by(
                book_id=ref['book_id'],
                chapter=ref['chapter'],
                verse=ref['verse']
            ).first()
            
            if verse_obj:
                results.append(verse_obj.to_dict())
        
        return results
    
    def search_verses(self, query: str, limit: int = 50) -> List[Dict]:
        """Search verses by text content"""
        verses = Verse.query.filter(
            Verse.text.contains(query)
        ).limit(limit).all()
        
        return [verse.to_dict() for verse in verses]
    
    def get_all_books(self) -> List[Dict]:
        """Get all books in the Bible"""
        books = Book.query.order_by(Book.book_order).all()
        return [book.to_dict() for book in books]
    
    def get_book_by_name(self, name: str) -> Optional[Dict]:
        """Get book information by name or abbreviation"""
        book_id = self.parser._get_book_id(name)
        if not book_id:
            return None
        
        book = Book.query.get(book_id)
        return book.to_dict() if book else None
    
    def get_chapter_verses(self, book_name: str, chapter: int) -> List[Dict]:
        """Get all verses in a specific chapter"""
        book_id = self.parser._get_book_id(book_name)
        if not book_id:
            return []
        
        verses = Verse.query.filter_by(
            book_id=book_id,
            chapter=chapter
        ).order_by(Verse.verse).all()
        
        return [verse.to_dict() for verse in verses]
    
    def populate_sample_data(self):
        """Populate database with sample Bible data for testing"""
        # Check if data already exists
        if Book.query.first():
            return
        
        # Sample books
        books_data = [
            {'name': 'Genesis', 'abbreviation': 'Gen', 'testament': 'OT', 'book_order': 1, 'total_chapters': 50},
            {'name': 'Exodus', 'abbreviation': 'Exo', 'testament': 'OT', 'book_order': 2, 'total_chapters': 40},
            {'name': 'Matthew', 'abbreviation': 'Matt', 'testament': 'NT', 'book_order': 40, 'total_chapters': 28},
            {'name': 'John', 'abbreviation': 'John', 'testament': 'NT', 'book_order': 43, 'total_chapters': 21},
            {'name': 'Ephesians', 'abbreviation': 'Eph', 'testament': 'NT', 'book_order': 49, 'total_chapters': 6},
            {'name': '1 John', 'abbreviation': '1 John', 'testament': 'NT', 'book_order': 62, 'total_chapters': 5},
            {'name': '2 Peter', 'abbreviation': '2 Pet', 'testament': 'NT', 'book_order': 61, 'total_chapters': 3},
            {'name': 'Romans', 'abbreviation': 'Rom', 'testament': 'NT', 'book_order': 45, 'total_chapters': 16},
            {'name': '1 Corinthians', 'abbreviation': '1 Cor', 'testament': 'NT', 'book_order': 46, 'total_chapters': 16},
        ]
        
        for book_data in books_data:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.commit()
        
        # Add abbreviations
        abbreviations_data = [
            {'book_name': 'Matthew', 'abbreviations': ['Mt', 'Mat']},
            {'book_name': 'John', 'abbreviations': ['Jn', 'Joh']},
            {'book_name': 'Ephesians', 'abbreviations': ['Ephes', 'Ep']},
            {'book_name': '1 John', 'abbreviations': ['1Jn', '1 Jn']},
            {'book_name': '2 Peter', 'abbreviations': ['2Pet', '2 Pe', '2Pe']},
            {'book_name': 'Romans', 'abbreviations': ['Ro', 'Rm']},
            {'book_name': '1 Corinthians', 'abbreviations': ['1Cor', '1 Co']},
        ]
        
        for abbrev_data in abbreviations_data:
            book = Book.query.filter_by(name=abbrev_data['book_name']).first()
            if book:
                for abbrev in abbrev_data['abbreviations']:
                    book_abbrev = BookAbbreviation(book_id=book.id, abbreviation=abbrev)
                    db.session.add(book_abbrev)
        
        db.session.commit()
        
        # Sample verses (from the outline)
        sample_verses = [
            {'book': 'Ephesians', 'chapter': 1, 'verse': 5, 'text': 'Having predestinated us unto the adoption of children by Jesus Christ to himself, according to the good pleasure of his will,'},
            {'book': 'Ephesians', 'chapter': 1, 'verse': 9, 'text': 'Having made known unto us the mystery of his will, according to his good pleasure which he hath purposed in himself:'},
            {'book': 'Ephesians', 'chapter': 5, 'verse': 1, 'text': 'Be ye therefore followers of God, as dear children;'},
            {'book': 'Ephesians', 'chapter': 5, 'verse': 2, 'text': 'And walk in love, as Christ also hath loved us, and hath given himself for us an offering and a sacrifice to God for a sweetsmelling savour.'},
            {'book': 'Ephesians', 'chapter': 5, 'verse': 8, 'text': 'For ye were sometimes darkness, but now are ye light in the Lord: walk as children of light:'},
            {'book': '1 John', 'chapter': 4, 'verse': 8, 'text': 'He that loveth not knoweth not God; for God is love.'},
            {'book': '1 John', 'chapter': 4, 'verse': 16, 'text': 'And we have known and believed the love that God hath to us. God is love; and he that dwelleth in love dwelleth in God, and God in him.'},
            {'book': '1 John', 'chapter': 1, 'verse': 5, 'text': 'This then is the message which we have heard of him, and declare unto you, that God is light, and in him is no darkness at all.'},
            {'book': '1 John', 'chapter': 3, 'verse': 1, 'text': 'Behold, what manner of love the Father hath bestowed upon us, that we should be called the sons of God: therefore the world knoweth us not, because it knew him not.'},
            {'book': 'John', 'chapter': 1, 'verse': 12, 'text': 'But as many as received him, to them gave he power to become the sons of God, even to them that believe on his name:'},
            {'book': 'John', 'chapter': 1, 'verse': 13, 'text': 'Which were born, not of blood, nor of the will of the flesh, nor of the will of man, but of God.'},
            {'book': 'Matthew', 'chapter': 5, 'verse': 48, 'text': 'Be ye therefore perfect, even as your Father which is in heaven is perfect.'},
            {'book': '2 Peter', 'chapter': 1, 'verse': 4, 'text': 'Whereby are given unto us exceeding great and precious promises: that by these ye might be partakers of the divine nature, having escaped the corruption that is in the world through lust.'},
        ]
        
        for verse_data in sample_verses:
            book = Book.query.filter_by(name=verse_data['book']).first()
            if book:
                verse = Verse(
                    book_id=book.id,
                    chapter=verse_data['chapter'],
                    verse=verse_data['verse'],
                    text=verse_data['text']
                )
                db.session.add(verse)
        
        db.session.commit()
        print("Sample Bible data populated successfully!")

