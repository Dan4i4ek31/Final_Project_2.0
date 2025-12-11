from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.users import UserRepository
from app.schemes.user import UserCreate, UserUpdate
from app.models.users import UserModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user(self, user_id: int) -> Optional[UserModel]:
        return self.repository.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.repository.get_by_email(email)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return self.repository.get_all(skip, limit)

    def get_users_by_role(self, role_id: int, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return self.repository.get_by_role(role_id, skip, limit)

    def create_user(self, user: UserCreate) -> UserModel:
        user_data = user.dict()
        user_data["password_hash"] = pwd_context.hash(user.password)
        del user_data["password"]
        return self.repository.create(user_data)

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[UserModel]:
        db_user = self.repository.get(user_id)
        if db_user:
            update_data = user.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["password_hash"] = pwd_context.hash(update_data["password"])
                del update_data["password"]
            return self.repository.update(db_user, update_data)
        return None

    def delete_user(self, user_id: int) -> Optional[UserModel]:
        return self.repository.delete(user_id)

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.password_hash):
            return None
        return user