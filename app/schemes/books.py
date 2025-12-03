from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Базовые схемы
class BookBase(BaseModel):
    title: str
    description: Optional[str] = None  # исправлено опечатку discription -> description
    author_id: int
    genre_id: int  # исправлено gengre -> genre для единообразия
    year: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None
    genre_id: Optional[int] = None
    year: Optional[int] = None

# Схемы для ответов
class BookInDB(BookBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class BookResponse(BookInDB):
    author_name: Optional[str] = None
    genre_name: Optional[str] = None

# Схемы для связанных данных
class AuthorBase(BaseModel):
    id: int
    name: str

class GenreBase(BaseModel):
    id: int
    name: str

class BookWithRelations(BookResponse):
    author: Optional[AuthorBase] = None
    genre: Optional[GenreBase] = None
    comment_count: Optional[int] = 0
    shelf_count: Optional[int] = 0