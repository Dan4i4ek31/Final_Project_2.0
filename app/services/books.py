from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.books import BookRepository
from app.schemes.books import BookCreate, BookUpdate
from app.models.books import BooksModel
from sqlalchemy.orm import joinedload


class BookService:
    def __init__(self, db: Session):
        self.repository = BookRepository(db)
        self.db = db

    def get_book(self, book_id: int) -> Optional[BooksModel]:
        # Загружаем с комментариями и связанными данными
        return self.db.query(BooksModel)\
            .options(joinedload(BooksModel.author),
                    joinedload(BooksModel.genre),
                    joinedload(BooksModel.book_comments))\
            .filter(BooksModel.id == book_id)\
            .first()

    def get_books(self, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        # Загружаем с комментариями и связанными данными
        books = self.db.query(BooksModel)\
            .options(joinedload(BooksModel.author),
                    joinedload(BooksModel.genre),
                    joinedload(BooksModel.book_comments))\
            .offset(skip)\
            .limit(limit)\
            .all()
        return books

    def get_books_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        books = self.db.query(BooksModel)\
            .options(joinedload(BooksModel.author),
                    joinedload(BooksModel.genre),
                    joinedload(BooksModel.book_comments))\
            .filter(BooksModel.author_id == author_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return books

    def get_books_by_genre(self, genre_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        books = self.db.query(BooksModel)\
            .options(joinedload(BooksModel.author),
                    joinedload(BooksModel.genre),
                    joinedload(BooksModel.book_comments))\
            .filter(BooksModel.genre_id == genre_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return books

    def search_books(self, title: str, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        books = self.db.query(BooksModel)\
            .options(joinedload(BooksModel.author),
                    joinedload(BooksModel.genre),
                    joinedload(BooksModel.book_comments))\
            .filter(BooksModel.title.ilike(f"%{title}%"))\
            .offset(skip)\
            .limit(limit)\
            .all()
        return books

    def create_book(self, book: BookCreate) -> BooksModel:
        return self.repository.create(book.dict())

    def update_book(self, book_id: int, book: BookUpdate) -> Optional[BooksModel]:
        db_book = self.repository.get(book_id)
        if db_book:
            return self.repository.update(db_book, book.dict(exclude_unset=True))
        return None

    def delete_book(self, book_id: int) -> Optional[BooksModel]:
        return self.repository.delete(book_id)