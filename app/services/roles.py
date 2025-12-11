from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.roles import RoleRepository
from app.schemes.roles import RoleCreate, RoleUpdate
from app.models.roles import RoleModel


class RoleService:
    def __init__(self, db: Session):
        self.repository = RoleRepository(db)

    def get_role(self, role_id: int) -> Optional[RoleModel]:
        return self.repository.get(role_id)

    def get_role_by_name(self, name: str) -> Optional[RoleModel]:
        return self.repository.get_by_name(name)

    def get_roles(self, skip: int = 0, limit: int = 100) -> List[RoleModel]:
        return self.repository.get_all(skip, limit)

    def create_role(self, role: RoleCreate) -> RoleModel:
        return self.repository.create(role.dict())

    def update_role(self, role_id: int, role: RoleUpdate) -> Optional[RoleModel]:
        db_role = self.repository.get(role_id)
        if db_role:
            return self.repository.update(db_role, role.dict(exclude_unset=True))
        return None

    def delete_role(self, role_id: int) -> Optional[RoleModel]:
        return self.repository.delete(role_id)