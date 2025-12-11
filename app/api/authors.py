from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.authors import Author, AuthorCreate, AuthorUpdate
from app.services.authors import AuthorService
from app.exceptions.authors import (
    AuthorNotFoundException,
    AuthorAlreadyExistsException,
    AuthorHasBooksException
)

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=List[Author])
def read_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = AuthorService(db)
    return service.get_authors(skip, limit)


@router.get("/{author_id}", response_model=Author)
def read_author(author_id: int, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)
    if author is None:
        raise AuthorNotFoundException(author_id=author_id)
    return author


@router.get("/by-name/{name}", response_model=Author)
def read_author_by_name(name: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author_by_name(name)
    if author is None:
        raise AuthorNotFoundException(author_name=name)
    return author


@router.post("/", response_model=Author)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    service = AuthorService(db)
    existing_author = service.get_author_by_name(author.name)
    if existing_author:
        raise AuthorAlreadyExistsException(author_name=author.name)
    return service.create_author(author)


@router.put("/{author_id}", response_model=Author)
def update_author(author_id: int, author: AuthorUpdate, db: Session = Depends(get_db)):
    service = AuthorService(db)
    db_author = service.update_author(author_id, author)
    if db_author is None:
        raise AuthorNotFoundException(author_id=author_id)
    return db_author


@router.delete("/{author_id}", response_model=Author)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    service = AuthorService(db)
    db_author = service.get_author(author_id)
    if db_author is None:
        raise AuthorNotFoundException(author_id=author_id)
    
    # Проверяем, есть ли у автора книги
    if db_author.books:
        raise AuthorHasBooksException(author_name=db_author.name)
    
    deleted_author = service.delete_author(author_id)
    return deleted_author