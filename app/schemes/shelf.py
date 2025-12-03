from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ShelfBase(BaseModel):
    book_id: int
    user_id: int
    status_read: Optional[bool] = False


class ShelfCreate(ShelfBase):
    pass


class ShelfUpdate(BaseModel):
    status_read: Optional[bool] = None


class ShelfInDB(ShelfBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ShelfResponse(ShelfInDB):
    pass