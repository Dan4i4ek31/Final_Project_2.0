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
    books = service.get_books(skip, limit)
    
    # Преобразуем объекты модели в словари с дополнительными полями
    result = []
    for book in books:
        book_dict = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author_id": book.author_id,
            "genre_id": book.genre_id,
            "year": book.year,
            "author_name": book.author.name if book.author else None,
            "genre_name": book.genre.name if book.genre else None
        }
        result.append(book_dict)
    
    return result

@router.get("/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    service = BookService(db)
    book = service.get_book(book_id)
    if book is None:
        raise BookNotFoundException(book_id=book_id)
    
    # Возвращаем с именами автора и жанра
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "author_id": book.author_id,
        "genre_id": book.genre_id,
        "year": book.year,
        "author_name": book.author.name if book.author else None,
        "genre_name": book.genre.name if book.genre else None
    }

# Остальные методы остаются без изменений...