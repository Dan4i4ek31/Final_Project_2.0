from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.users import UserModel
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, db: Session):
        super().__init__(UserModel, db)

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_role(self, role_id: int, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return self.db.query(UserModel).filter(UserModel.role_id == role_id).offset(skip).limit(limit).all()