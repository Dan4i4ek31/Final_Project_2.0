from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.gengres import GengresModel
from app.repositories.base import BaseRepository


class GenreRepository(BaseRepository[GengresModel]):
    def __init__(self, db: Session):
        super().__init__(GengresModel, db)

    def get_by_name(self, name: str) -> Optional[GengresModel]:
        return self.db.query(GengresModel).filter(GengresModel.name == name).first()