from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, date

class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None  # используем date вместо datetime для даты рождения
    country: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    country: Optional[str] = None

class AuthorInDB(AuthorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class AuthorResponse(AuthorInDB):
    book_count: Optional[int] = 0
    age: Optional[int] = None
    
    @field_validator('age', mode='before')
    def calculate_age(cls, v, info):
        if 'birth_date' in info.data and info.data['birth_date']:
            today = date.today()
            birth_date = info.data['birth_date']
            if isinstance(birth_date, datetime):
                birth_date = birth_date.date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        return None

class AuthorWithBooks(AuthorResponse):
    books: Optional[List[dict]] = None