from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.books import BookRepository
from app.schemes.books import BookCreate, BookUpdate
from app.models.books import BooksModel

class BookService:
    def __init__(self, db: Session):
        self.repository = BookRepository(db)
        self.db = db

    def get_book(self, book_id: int) -> Optional[BooksModel]:
        return self.repository.get(book_id)

    def get_books(self, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        # Используем joined load для автора и жанра
        books = self.repository.get_all(skip, limit)
        return books

    def get_books_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        return self.repository.get_by_author(author_id, skip, limit)

    def get_books_by_genre(self, genre_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        return self.repository.get_by_genre(genre_id, skip, limit)

    def search_books(self, title: str, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        return self.repository.search_by_title(title, skip, limit)

    def create_book(self, book: BookCreate) -> BooksModel:
        return self.repository.create(book.dict())

    def update_book(self, book_id: int, book: BookUpdate) -> Optional[BooksModel]:
        db_book = self.repository.get(book_id)
        if db_book:
            return self.repository.update(db_book, book.dict(exclude_unset=True))
        return None

    def delete_book(self, book_id: int) -> Optional[BooksModel]:
        return self.repository.delete(book_id)