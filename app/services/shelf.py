from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.shelf import ShelfRepository
from app.schemes.shelf import ShelfCreate, ShelfUpdate
from app.models.shelf import ShelfModel


class ShelfService:
    def __init__(self, db: Session):
        self.repository = ShelfRepository(db)

    def get_shelf_entry(self, shelf_id: int) -> Optional[ShelfModel]:
        return self.repository.get(shelf_id)

    def get_shelf_entries(self, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.repository.get_all(skip, limit)

    def get_user_shelf(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.repository.get_by_user(user_id, skip, limit)

    def get_book_shelf_entries(self, book_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.repository.get_by_book(book_id, skip, limit)

    def get_user_book_entry(self, user_id: int, book_id: int) -> Optional[ShelfModel]:
        return self.repository.get_by_user_and_book(user_id, book_id)

    def get_read_books(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.repository.get_read_books(user_id, skip, limit)

    def add_to_shelf(self, shelf_data: ShelfCreate) -> ShelfModel:
        return self.repository.create(shelf_data.dict())

    def update_shelf_entry(self, shelf_id: int, shelf_data: ShelfUpdate) -> Optional[ShelfModel]:
        db_shelf = self.repository.get(shelf_id)
        if db_shelf:
            return self.repository.update(db_shelf, shelf_data.dict(exclude_unset=True))
        return None

    def remove_from_shelf(self, shelf_id: int) -> Optional[ShelfModel]:
        return self.repository.delete(shelf_id)

    def mark_as_read(self, shelf_id: int) -> Optional[ShelfModel]:
        db_shelf = self.repository.get(shelf_id)
        if db_shelf:
            db_shelf.status_read = True
            self.repository.db.commit()
            self.repository.db.refresh(db_shelf)
        return db_shelf