from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.shelf import Shelf, ShelfCreate, ShelfUpdate
from app.services.shelf import ShelfService
from app.exceptions.shelf import (
    ShelfEntryNotFoundException,
    BookAlreadyInShelfException,
    ShelfLimitExceededException,
    BookNotInShelfException
)

router = APIRouter(prefix="/shelf", tags=["shelf"])


@router.get("/", response_model=List[Shelf])
def read_shelf_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ShelfService(db)
    return service.get_shelf_entries(skip, limit)


@router.get("/{shelf_id}", response_model=Shelf)
def read_shelf_entry(shelf_id: int, db: Session = Depends(get_db)):
    service = ShelfService(db)
    shelf_entry = service.get_shelf_entry(shelf_id)
    if shelf_entry is None:
        raise ShelfEntryNotFoundException(shelf_id=shelf_id)
    return shelf_entry


@router.get("/user/{user_id}", response_model=List[Shelf])
def read_user_shelf(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ShelfService(db)
    return service.get_user_shelf(user_id, skip, limit)


@router.get("/book/{book_id}", response_model=List[Shelf])
def read_book_shelf_entries(book_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ShelfService(db)
    return service.get_book_shelf_entries(book_id, skip, limit)


@router.get("/user/{user_id}/book/{book_id}", response_model=Shelf)
def read_user_book_entry(user_id: int, book_id: int, db: Session = Depends(get_db)):
    service = ShelfService(db)
    shelf_entry = service.get_user_book_entry(user_id, book_id)
    if shelf_entry is None:
        raise ShelfEntryNotFoundException(user_id=user_id, book_id=book_id)
    return shelf_entry


@router.get("/user/{user_id}/read", response_model=List[Shelf])
def read_read_books(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ShelfService(db)
    return service.get_read_books(user_id, skip, limit)


@router.post("/", response_model=Shelf)
def add_to_shelf(shelf: ShelfCreate, db: Session = Depends(get_db)):
    service = ShelfService(db)
    
    # Проверяем, не существует ли уже такой записи
    existing_entry = service.get_user_book_entry(shelf.user_id, shelf.book_id)
    if existing_entry:
        raise BookAlreadyInShelfException(user_id=shelf.user_id, book_id=shelf.book_id)
    
    # Проверяем лимит книг на полке пользователя
    user_books = service.get_user_shelf(shelf.user_id)
    if len(user_books) >= 100:  # Лимит 100 книг
        raise ShelfLimitExceededException(max_books=100)
    
    return service.add_to_shelf(shelf)


@router.put("/{shelf_id}", response_model=Shelf)
def update_shelf_entry(shelf_id: int, shelf: ShelfUpdate, db: Session = Depends(get_db)):
    service = ShelfService(db)
    db_shelf = service.update_shelf_entry(shelf_id, shelf)
    if db_shelf is None:
        raise ShelfEntryNotFoundException(shelf_id=shelf_id)
    return db_shelf


@router.put("/{shelf_id}/mark-read", response_model=Shelf)
def mark_as_read(shelf_id: int, db: Session = Depends(get_db)):
    service = ShelfService(db)
    db_shelf = service.mark_as_read(shelf_id)
    if db_shelf is None:
        raise ShelfEntryNotFoundException(shelf_id=shelf_id)
    return db_shelf


@router.delete("/{shelf_id}", response_model=Shelf)
def remove_from_shelf(shelf_id: int, db: Session = Depends(get_db)):
    service = ShelfService(db)
    db_shelf = service.remove_from_shelf(shelf_id)
    if db_shelf is None:
        raise ShelfEntryNotFoundException(shelf_id=shelf_id)
    return db_shelf


@router.delete("/user/{user_id}/book/{book_id}", response_model=Shelf)
def remove_book_from_shelf(user_id: int, book_id: int, db: Session = Depends(get_db)):
    service = ShelfService(db)
    shelf_entry = service.get_user_book_entry(user_id, book_id)
    if shelf_entry is None:
        raise BookNotInShelfException(user_id=user_id, book_id=book_id)
    
    deleted_entry = service.remove_from_shelf(shelf_entry.id)
    return deleted_entry