from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.gengres import GenreRepository
from app.schemes.gengres import GenreCreate, GenreUpdate
from app.models.gengres import GengresModel


class GenreService:
    def __init__(self, db: Session):
        self.repository = GenreRepository(db)

    def get_genre(self, genre_id: int) -> Optional[GengresModel]:
        return self.repository.get(genre_id)

    def get_genre_by_name(self, name: str) -> Optional[GengresModel]:
        return self.repository.get_by_name(name)

    def get_genres(self, skip: int = 0, limit: int = 100) -> List[GengresModel]:
        return self.repository.get_all(skip, limit)

    def create_genre(self, genre: GenreCreate) -> GengresModel:
        return self.repository.create(genre.dict())

    def update_genre(self, genre_id: int, genre: GenreUpdate) -> Optional[GengresModel]:
        db_genre = self.repository.get(genre_id)
        if db_genre:
            return self.repository.update(db_genre, genre.dict())
        return None

    def delete_genre(self, genre_id: int) -> Optional[GengresModel]:
        return self.repository.delete(genre_id)