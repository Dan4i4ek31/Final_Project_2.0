from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.books import Book, BookCreate, BookUpdate
from app.services.books import BookService
from app.exceptions.books import (
    BookNotFoundException,
    BookAlreadyExistsException,
    BookHasCommentsException,
    BookInShelfException
)

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.get_books(skip, limit)


@router.get("/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    book = service.get_book(book_id)
    if book is None:
        raise BookNotFoundException(book_id=book_id)
    return book


@router.get("/by-author/{author_id}", response_model=List[Book])
def read_books_by_author(author_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.get_books_by_author(author_id, skip, limit)


@router.get("/by-genre/{genre_id}", response_model=List[Book])
def read_books_by_genre(genre_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.get_books_by_genre(genre_id, skip, limit)


@router.get("/search/{title}", response_model=List[Book])
def search_books(title: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.search_books(title, skip, limit)


@router.post("/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    service = BookService(db)
    # Проверяем, существует ли книга с таким же названием и автором
    books_by_author = service.get_books_by_author(book.author_id)
    for existing_book in books_by_author:
        if existing_book.title.lower() == book.title.lower():
            raise BookAlreadyExistsException(title=book.title, author_id=book.author_id)
    return service.create_book(book)


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    service = BookService(db)
    db_book = service.update_book(book_id, book)
    if db_book is None:
        raise BookNotFoundException(book_id=book_id)
    return db_book


@router.delete("/{book_id}", response_model=Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    db_book = service.get_book(book_id)
    if db_book is None:
        raise BookNotFoundException(book_id=book_id)
    
    # Проверяем, есть ли у книги комментарии
    if db_book.book_comments:
        raise BookHasCommentsException(book_title=db_book.title)
    
    # Проверяем, находится ли книга на полках пользователей
    if db_book.shelf_entries:
        raise BookInShelfException(book_title=db_book.title)
    
    deleted_book = service.delete_book(book_id)
    return deleted_book