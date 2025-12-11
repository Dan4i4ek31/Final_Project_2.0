from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.roles import RoleModel
from app.repositories.base import BaseRepository

class RoleRepository(BaseRepository[RoleModel]):
    def __init__(self, db: Session):
        super().__init__(RoleModel, db)

    def get_by_name(self, name: str) -> Optional[RoleModel]:
        return self.db.query(RoleModel).filter(RoleModel.name == name).first()