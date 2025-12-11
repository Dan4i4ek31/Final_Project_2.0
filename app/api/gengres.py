from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.gengres import Genre, GenreCreate, GenreUpdate
from app.services.gengres import GenreService
from app.exceptions.gengres import (
    GenreNotFoundException,
    GenreAlreadyExistsException,
    GenreHasBooksException
)

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=List[Genre])
def read_genres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = GenreService(db)
    return service.get_genres(skip, limit)


@router.get("/{genre_id}", response_model=Genre)
def read_genre(genre_id: int, db: Session = Depends(get_db)):
    service = GenreService(db)
    genre = service.get_genre(genre_id)
    if genre is None:
        raise GenreNotFoundException(genre_id=genre_id)
    return genre


@router.get("/by-name/{name}", response_model=Genre)
def read_genre_by_name(name: str, db: Session = Depends(get_db)):
    service = GenreService(db)
    genre = service.get_genre_by_name(name)
    if genre is None:
        raise GenreNotFoundException(genre_name=name)
    return genre


@router.post("/", response_model=Genre)
def create_genre(genre: GenreCreate, db: Session = Depends(get_db)):
    service = GenreService(db)
    existing_genre = service.get_genre_by_name(genre.name)
    if existing_genre:
        raise GenreAlreadyExistsException(genre_name=genre.name)
    return service.create_genre(genre)


@router.put("/{genre_id}", response_model=Genre)
def update_genre(genre_id: int, genre: GenreUpdate, db: Session = Depends(get_db)):
    service = GenreService(db)
    db_genre = service.update_genre(genre_id, genre)
    if db_genre is None:
        raise GenreNotFoundException(genre_id=genre_id)
    return db_genre


@router.delete("/{genre_id}", response_model=Genre)
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    service = GenreService(db)
    db_genre = service.get_genre(genre_id)
    if db_genre is None:
        raise GenreNotFoundException(genre_id=genre_id)
    
    # Проверяем, есть ли у жанра книги
    if db_genre.books:
        raise GenreHasBooksException(genre_name=db_genre.name)
    
    deleted_genre = service.delete_genre(genre_id)
    return deleted_genre