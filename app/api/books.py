from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.books import Book, BookCreate, BookUpdate, BookDetail
from app.services.books import BookService
from app.exceptions.books import (
    BookNotFoundException,
    BookAlreadyExistsException,
    BookHasCommentsException,
    BookInShelfException
)

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[Book])
def read_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Получить список книг с пагинацией.
    """
    service = BookService(db)
    books = service.get_books(skip, limit)
    
    # Преобразуем в формат ответа
    result = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author_id": book.author_id,
            "genre_id": book.genre_id,
            "year": book.year,
            "author_name": book.author.name if book.author else None,
            "genre_name": book.genre.name if book.genre else None,
            "comments": []
        }
        
        # Добавляем комментарии, если они есть
        if book.book_comments:
            for comment in book.book_comments:
                book_data["comments"].append({
                    "id": comment.id,
                    "comment_text": comment.comment_text,
                    "user_id": comment.user_id,
                    "created_at": comment.created_at
                })
        
        result.append(book_data)
    
    return result


@router.get("/{book_id}", response_model=BookDetail)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Получить книгу по ID с детальной информацией.
    """
    service = BookService(db)
    book = service.get_book(book_id)
    
    if book is None:
        raise BookNotFoundException(book_id=book_id)
    
    # Получаем количество записей на полке для этой книги
    from app.models.shelf import ShelfModel
    shelf_count = db.query(ShelfModel).filter(ShelfModel.book_id == book_id).count()
    
    # Собираем ответ
    response = {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "author_id": book.author_id,
        "genre_id": book.genre_id,
        "year": book.year,
        "author_name": book.author.name if book.author else None,
        "genre_name": book.genre.name if book.genre else None,
        "shelf_count": shelf_count,
        "average_rating": None,  # Можно добавить расчет рейтинга позже
        "comments": []
    }
    
    # Добавляем комментарии
    if book.book_comments:
        for comment in book.book_comments:
            response["comments"].append({
                "id": comment.id,
                "comment_text": comment.comment_text,
                "user_id": comment.user_id,
                "created_at": comment.created_at
            })
    
    return response


@router.post("/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Создать новую книгу.
    """
    service = BookService(db)
    
    # Проверяем, существует ли уже книга с таким названием и автором
    existing_books = service.search_books(book.title)
    for existing in existing_books:
        if existing.author_id == book.author_id:
            raise BookAlreadyExistsException(title=book.title, author_id=book.author_id)
    
    # Создаем книгу
    new_book = service.create_book(book)
    
    # Загружаем снова с отношениями для ответа
    book_with_relations = service.get_book(new_book.id)
    
    return {
        "id": new_book.id,
        "title": new_book.title,
        "description": new_book.description,
        "author_id": new_book.author_id,
        "genre_id": new_book.genre_id,
        "year": new_book.year,
        "author_name": book_with_relations.author.name if book_with_relations and book_with_relations.author else None,
        "genre_name": book_with_relations.genre.name if book_with_relations and book_with_relations.genre else None,
        "comments": []
    }


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """
    Обновить информацию о книге.
    """
    service = BookService(db)
    
    # Проверяем существование книги
    existing_book = service.get_book(book_id)
    if existing_book is None:
        raise BookNotFoundException(book_id=book_id)
    
    # Обновляем книгу
    updated_book = service.update_book(book_id, book)
    if updated_book is None:
        raise BookNotFoundException(book_id=book_id)
    
    # Загружаем снова с отношениями
    book_with_relations = service.get_book(book_id)
    
    return {
        "id": updated_book.id,
        "title": updated_book.title,
        "description": updated_book.description,
        "author_id": updated_book.author_id,
        "genre_id": updated_book.genre_id,
        "year": updated_book.year,
        "author_name": book_with_relations.author.name if book_with_relations and book_with_relations.author else None,
        "genre_name": book_with_relations.genre.name if book_with_relations and book_with_relations.genre else None,
        "comments": []
    }


@router.delete("/{book_id}", response_model=Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Удалить книгу.
    """
    service = BookService(db)
    
    # Проверяем существование книги
    book = service.get_book(book_id)
    if book is None:
        raise BookNotFoundException(book_id=book_id)
    
    # Проверяем, есть ли комментарии к книге
    if book.book_comments and len(book.book_comments) > 0:
        raise BookHasCommentsException(book_id=book_id)
    
    # Проверяем, есть ли книга на полках у пользователей
    from app.models.shelf import ShelfModel
    shelf_entries = db.query(ShelfModel).filter(ShelfModel.book_id == book_id).first()
    if shelf_entries:
        raise BookInShelfException(book_id=book_id)
    
    # Удаляем книгу
    deleted_book = service.delete_book(book_id)
    
    return {
        "id": deleted_book.id,
        "title": deleted_book.title,
        "description": deleted_book.description,
        "author_id": deleted_book.author_id,
        "genre_id": deleted_book.genre_id,
        "year": deleted_book.year,
        "author_name": book.author.name if book.author else None,
        "genre_name": book.genre.name if book.genre else None,
        "comments": []
    }


@router.get("/search/", response_model=List[Book])
def search_books(
    title: str = Query("", description="Название книги для поиска"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Поиск книг по названию.
    """
    service = BookService(db)
    books = service.search_books(title, skip, limit)
    
    result = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author_id": book.author_id,
            "genre_id": book.genre_id,
            "year": book.year,
            "author_name": book.author.name if book.author else None,
            "genre_name": book.genre.name if book.genre else None,
            "comments": []
        }
        
        if book.book_comments:
            for comment in book.book_comments:
                book_data["comments"].append({
                    "id": comment.id,
                    "comment_text": comment.comment_text,
                    "user_id": comment.user_id,
                    "created_at": comment.created_at
                })
        
        result.append(book_data)
    
    return result


@router.get("/author/{author_id}", response_model=List[Book])
def get_books_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Получить книги по автору.
    """
    service = BookService(db)
    books = service.get_books_by_author(author_id, skip, limit)
    
    result = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author_id": book.author_id,
            "genre_id": book.genre_id,
            "year": book.year,
            "author_name": book.author.name if book.author else None,
            "genre_name": book.genre.name if book.genre else None,
            "comments": []
        }
        
        if book.book_comments:
            for comment in book.book_comments:
                book_data["comments"].append({
                    "id": comment.id,
                    "comment_text": comment.comment_text,
                    "user_id": comment.user_id,
                    "created_at": comment.created_at
                })
        
        result.append(book_data)
    
    return result


@router.get("/genre/{genre_id}", response_model=List[Book])
def get_books_by_genre(
    genre_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Получить книги по жанру.
    """
    service = BookService(db)
    books = service.get_books_by_genre(genre_id, skip, limit)
    
    result = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author_id": book.author_id,
            "genre_id": book.genre_id,
            "year": book.year,
            "author_name": book.author.name if book.author else None,
            "genre_name": book.genre.name if book.genre else None,
            "comments": []
        }
        
        if book.book_comments:
            for comment in book.book_comments:
                book_data["comments"].append({
                    "id": comment.id,
                    "comment_text": comment.comment_text,
                    "user_id": comment.user_id,
                    "created_at": comment.created_at
                })
        
        result.append(book_data)
    
    return result