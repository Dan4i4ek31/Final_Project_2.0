from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class BookCommentBase(BaseModel):
    book_id: int
    user_id: int
    comment_text: str


class BookCommentCreate(BookCommentBase):
    pass


class BookCommentUpdate(BaseModel):
    comment_text: Optional[str] = None


class BookComment(BookCommentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True