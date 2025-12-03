from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.shelf import ShelfModel
from app.schemes.shelf import ShelfCreate, ShelfUpdate

class ShelfRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, shelf_data: ShelfCreate) -> ShelfModel:
        db_shelf = ShelfModel(**shelf_data.model_dump())
        self.db.add(db_shelf)
        self.db.commit()
        self.db.refresh(db_shelf)
        return db_shelf
    
    def get_by_id(self, shelf_id: int) -> Optional[ShelfModel]:
        return self.db.query(ShelfModel)\
            .filter(ShelfModel.id == shelf_id)\
            .first()
    
    def get_by_user_and_book(self, user_id: int, book_id: int) -> Optional[ShelfModel]:
        return self.db.query(ShelfModel)\
            .filter(ShelfModel.user_id == user_id, ShelfModel.book_id == book_id)\
            .first()
    
    def get_user_shelves(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.db.query(ShelfModel)\
            .filter(ShelfModel.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_user_shelves_with_books(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ShelfModel]:
        return self.db.query(ShelfModel)\
            .options(joinedload(ShelfModel.book))\
            .filter(ShelfModel.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def update(self, shelf: ShelfModel, shelf_data: ShelfUpdate) -> ShelfModel:
        update_data = shelf_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(shelf, field, value)
        
        self.db.commit()
        self.db.refresh(shelf)
        return shelf
    
    def delete(self, shelf: ShelfModel) -> None:
        self.db.delete(shelf)
        self.db.commit()
    
    def count_user_shelves(self, user_id: int) -> int:
        return self.db.query(ShelfModel)\
            .filter(ShelfModel.user_id == user_id)\
            .count()