from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BookCommentInBook(BaseModel):
    id: int
    comment_text: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название книги")
    description: Optional[str] = Field(None, max_length=2000, description="Описание книги")
    author_id: int = Field(..., ge=1, description="ID автора")
    genre_id: int = Field(..., ge=1, description="ID жанра")
    year: int = Field(..., ge=1000, le=2100, description="Год издания")


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Название книги")
    description: Optional[str] = Field(None, max_length=2000, description="Описание книги")
    author_id: Optional[int] = Field(None, ge=1, description="ID автора")
    genre_id: Optional[int] = Field(None, ge=1, description="ID жанра")
    year: Optional[int] = Field(None, ge=1000, le=2100, description="Год издания")


class Book(BookBase):
    id: int
    author_name: Optional[str] = None
    genre_name: Optional[str] = None
    comments: List[BookCommentInBook] = Field(default_factory=list, description="Комментарии к книге")
    
    class Config:
        from_attributes = True


class BookDetail(Book):
    shelf_count: int = Field(0, ge=0, description="Количество пользователей, добавивших книгу на полку")
    average_rating: Optional[float] = Field(None, ge=0, le=5, description="Средний рейтинг книги")