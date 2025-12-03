from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BookCommentBase(BaseModel):
    book_id: int
    user_id: int
    comment_text: str

class BookCommentCreate(BookCommentBase):
    pass

class BookCommentUpdate(BaseModel):
    comment_text: Optional[str] = None

class BookCommentInDB(BookCommentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class BookCommentResponse(BookCommentInDB):
    user_name: Optional[str] = None
    book_title: Optional[str] = None

class BookCommentWithRelations(BookCommentResponse):
    user: Optional[dict] = None
    book: Optional[dict] = None