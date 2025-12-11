from pydantic import BaseModel
from typing import Optional


class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    author_id: int
    genre_id: int
    year: int


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None
    genre_id: Optional[int] = None
    year: Optional[int] = None


class Book(BookBase):
    id: int

    class Config:
        from_attributes = True