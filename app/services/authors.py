from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.authors import AuthorRepository
from app.schemes.authors import AuthorCreate, AuthorUpdate
from app.models.authors import AuthorsModel


class AuthorService:
    def __init__(self, db: Session):
        self.repository = AuthorRepository(db)

    def get_author(self, author_id: int) -> Optional[AuthorsModel]:
        return self.repository.get(author_id)

    def get_author_by_name(self, name: str) -> Optional[AuthorsModel]:
        return self.repository.get_by_name(name)

    def get_authors(self, skip: int = 0, limit: int = 100) -> List[AuthorsModel]:
        return self.repository.get_all(skip, limit)

    def create_author(self, author: AuthorCreate) -> AuthorsModel:
        return self.repository.create(author.dict())

    def update_author(self, author_id: int, author: AuthorUpdate) -> Optional[AuthorsModel]:
        db_author = self.repository.get(author_id)
        if db_author:
            return self.repository.update(db_author, author.dict())
        return None

    def delete_author(self, author_id: int) -> Optional[AuthorsModel]:
        return self.repository.delete(author_id)