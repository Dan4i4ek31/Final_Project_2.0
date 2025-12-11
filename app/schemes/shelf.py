from pydantic import BaseModel
from typing import Optional


class ShelfBase(BaseModel):
    book_id: int
    user_id: int
    status_read: bool = False


class ShelfCreate(ShelfBase):
    pass


class ShelfUpdate(BaseModel):
    status_read: Optional[bool] = None


class Shelf(ShelfBase):
    id: int

    class Config:
        from_attributes = True