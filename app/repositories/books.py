from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.books import BooksModel
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[BooksModel]):
    def __init__(self, db: Session):
        super().__init__(BooksModel, db)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        return self.db.query(BooksModel).filter(BooksModel.author_id == author_id).offset(skip).limit(limit).all()

    def get_by_genre(self, genre_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        return self.db.query(BooksModel).filter(BooksModel.genre_id == genre_id).offset(skip).limit(limit).all()

    def search_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        return self.db.query(BooksModel).filter(BooksModel.title.ilike(f"%{title}%")).offset(skip).limit(limit).all()