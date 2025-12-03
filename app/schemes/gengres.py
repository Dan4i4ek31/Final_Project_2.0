from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None

class GenreCreate(GenreBase):
    pass

class GenreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GenreInDB(GenreBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class GenreResponse(GenreInDB):
    book_count: Optional[int] = 0

class GenreWithBooks(GenreResponse):
    books: Optional[List[dict]] = None