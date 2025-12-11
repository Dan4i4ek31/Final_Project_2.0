from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.shelf import ShelfModel
from app.repositories.base import BaseRepository


class ShelfRepository(BaseRepository[ShelfModel]):
    def __init__(self, db: Session):
        super().__init__(ShelfModel, db)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.db.query(ShelfModel).filter(ShelfModel.user_id == user_id).offset(skip).limit(limit).all()

    def get_by_book(self, book_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.db.query(ShelfModel).filter(ShelfModel.book_id == book_id).offset(skip).limit(limit).all()

    def get_by_user_and_book(self, user_id: int, book_id: int) -> Optional[ShelfModel]:
        return self.db.query(ShelfModel).filter(
            ShelfModel.user_id == user_id,
            ShelfModel.book_id == book_id
        ).first()

    def get_read_books(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.db.query(ShelfModel).filter(
            ShelfModel.user_id == user_id,
            ShelfModel.status_read == True
        ).offset(skip).limit(limit).all()