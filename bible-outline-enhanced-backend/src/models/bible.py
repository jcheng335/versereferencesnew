from src.models.user import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    abbreviation = db.Column(db.String(10), nullable=False)
    testament = db.Column(db.String(3), nullable=False)  # 'OT' or 'NT'
    book_order = db.Column(db.Integer, nullable=False)
    total_chapters = db.Column(db.Integer, nullable=False)
    
    # Relationships
    verses = db.relationship('Verse', backref='book', lazy=True)
    abbreviations = db.relationship('BookAbbreviation', backref='book', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'testament': self.testament,
            'book_order': self.book_order,
            'total_chapters': self.total_chapters
        }

class Verse(db.Model):
    __tablename__ = 'verses'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    verse = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('book_id', 'chapter', 'verse'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_name': self.book.name,
            'chapter': self.chapter,
            'verse': self.verse,
            'text': self.text,
            'reference': f"{self.book.name} {self.chapter}:{self.verse}"
        }

class BookAbbreviation(db.Model):
    __tablename__ = 'book_abbreviations'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    abbreviation = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'abbreviation': self.abbreviation
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    original_filename = db.Column(db.String(255))
    processed_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'original_filename': self.original_filename,
            'processed_content': self.processed_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

