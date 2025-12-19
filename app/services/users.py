from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.users import UserModel
from app.schemes.user import UserCreate, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(UserModel).offset(skip).limit(limit).all()
    
    def get_user(self, user_id: int):
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def get_users_by_role(self, role_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(UserModel).filter(UserModel.role_id == role_id).offset(skip).limit(limit).all()
    
    def create_user(self, user: UserCreate):
        hashed_password = pwd_context.hash(user.password)
        
        db_user = UserModel(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,  
            role_id=user.role_id
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, email: str, password: str):
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Проверяем пароль
        if not pwd_context.verify(password, user.password_hash):
            return None
        
        return user
    
    def update_user(self, user_id: int, user: UserUpdate):
        db_user = self.get_user(user_id)
        if db_user:
            update_data = user.dict(exclude_unset=True)
            
            # Если обновляется пароль, нужно его хэшировать
            if 'password' in update_data:
                update_data['password_hash'] = pwd_context.hash(update_data.pop('password'))
            
            for key, value in update_data.items():
                setattr(db_user, key, value)
            
            self.db.commit()
            self.db.refresh(db_user)
        
        return db_user
    
    def delete_user(self, user_id: int):
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return db_user