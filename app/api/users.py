from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.user import User, UserCreate, UserUpdate
from app.services.users import UserService
from app.exceptions.users import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserHasBooksException,
    UserHasCommentsException
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_users(skip, limit)


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if user is None:
        raise UserNotFoundException(user_id=user_id)
    return user


@router.get("/by-email/{email}", response_model=User)
def read_user_by_email(email: str, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user_by_email(email)
    if user is None:
        raise UserNotFoundException(email=email)
    return user


@router.get("/by-role/{role_id}", response_model=List[User])
def read_users_by_role(role_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_users_by_role(role_id, skip, limit)


@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    existing_user = service.get_user_by_email(user.email)
    if existing_user:
        raise UserAlreadyExistsException(email=user.email)
    return service.create_user(user)


@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate_user(email, password)
    if not user:
        raise InvalidCredentialsException()
    return {"message": "Login successful", "user_id": user.id, "email": user.email}


@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    db_user = service.update_user(user_id, user)
    if db_user is None:
        raise UserNotFoundException(user_id=user_id)
    return db_user


@router.delete("/{user_id}", response_model=User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    db_user = service.get_user(user_id)
    if db_user is None:
        raise UserNotFoundException(user_id=user_id)
    
    # Проверяем, есть ли у пользователя книги на полке
    if db_user.shelf:
        raise UserHasBooksException()
    
    # Проверяем, есть ли у пользователя комментарии
    if db_user.book_comments:
        raise UserHasCommentsException()
    
    deleted_user = service.delete_user(user_id)
    return deleted_user