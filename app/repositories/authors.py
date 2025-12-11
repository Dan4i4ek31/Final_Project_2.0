from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.authors import AuthorsModel
from app.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorsModel]):
    def __init__(self, db: Session):
        super().__init__(AuthorsModel, db)

    def get_by_name(self, name: str) -> Optional[AuthorsModel]:
        return self.db.query(AuthorsModel).filter(AuthorsModel.name == name).first()