from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.book_comments import BookCommentsModel
from app.repositories.base import BaseRepository


class BookCommentRepository(BaseRepository[BookCommentsModel]):
    def __init__(self, db: Session):
        super().__init__(BookCommentsModel, db)

    def get_by_book(self, book_id: int, skip: int = 0, limit: int = 100) -> List[BookCommentsModel]:
        return self.db.query(BookCommentsModel).filter(BookCommentsModel.book_id == book_id).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BookCommentsModel]:
        return self.db.query(BookCommentsModel).filter(BookCommentsModel.user_id == user_id).offset(skip).limit(limit).all()