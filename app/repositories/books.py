from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.books import BooksModel
from app.models.authors import AuthorsModel
from app.models.gengres import GengresModel
from app.models.book_comments import BookCommentsModel
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[BooksModel]):
    def __init__(self, db: Session):
        super().__init__(BooksModel, db)
    
    def get_with_relations(self, book_id: int) -> Optional[BooksModel]:
        """
        Получить книгу с автором, жанром и комментариями.
        """
        return self.db.query(BooksModel)\
            .options(
                joinedload(BooksModel.author),
                joinedload(BooksModel.genre),
                joinedload(BooksModel.book_comments)
            )\
            .filter(BooksModel.id == book_id)\
            .first()
    
    def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        """
        Получить все книги с авторами, жанрами и комментариями.
        """
        return self.db.query(BooksModel)\
            .options(
                joinedload(BooksModel.author),
                joinedload(BooksModel.genre),
                joinedload(BooksModel.book_comments)
            )\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_title_and_author(self, title: str, author_id: int) -> Optional[BooksModel]:
        """
        Получить книгу по названию и автору.
        """
        return self.db.query(BooksModel)\
            .filter(BooksModel.title == title, BooksModel.author_id == author_id)\
            .first()
    
    def get_by_author_with_relations(self, author_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        """
        Получить книги автора с жанрами и комментариями.
        """
        return self.db.query(BooksModel)\
            .options(
                joinedload(BooksModel.author),
                joinedload(BooksModel.genre),
                joinedload(BooksModel.book_comments)
            )\
            .filter(BooksModel.author_id == author_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_genre_with_relations(self, genre_id: int, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        """
        Получить книги жанра с авторами и комментариями.
        """
        return self.db.query(BooksModel)\
            .options(
                joinedload(BooksModel.author),
                joinedload(BooksModel.genre),
                joinedload(BooksModel.book_comments)
            )\
            .filter(BooksModel.genre_id == genre_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def search_with_relations(self, title: str, skip: int = 0, limit: int = 100) -> List[BooksModel]:
        """
        Поиск книг по названию с авторами, жанрами и комментариями.
        """
        return self.db.query(BooksModel)\
            .options(
                joinedload(BooksModel.author),
                joinedload(BooksModel.genre),
                joinedload(BooksModel.book_comments)
            )\
            .filter(BooksModel.title.ilike(f"%{title}%"))\
            .offset(skip)\
            .limit(limit)\
            .all()