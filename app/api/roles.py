from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.exceptions.roles import RoleInUseException
from app.schemes.roles import Role, RoleCreate, RoleUpdate
from app.services.roles import RoleService
from app.exceptions.roles import (
    RoleNotFoundException,
    RoleAlreadyExistsException,
    RoleInUseException
)
router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = RoleService(db)
    return service.get_roles(skip, limit)


@router.get("/{role_id}", response_model=Role)
def read_role(role_id: int, db: Session = Depends(get_db)):
    service = RoleService(db)
    role = service.get_role(role_id)
    if role is None:
        raise RoleNotFoundException(role_id=role_id)
    return role


@router.post("/", response_model=Role)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    service = RoleService(db)
    existing_role = service.get_role_by_name(role.name)
    if existing_role:
        raise RoleAlreadyExistsException(role_name=role.name)
    return service.create_role(role)


@router.put("/{role_id}", response_model=Role)
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db)):
    service = RoleService(db)
    db_role = service.update_role(role_id, role)
    if db_role is None:
        raise RoleNotFoundException(role_id=role_id)
    return db_role


@router.delete("/{role_id}", response_model=Role)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    service = RoleService(db)
    db_role = service.get_role(role_id)
    if db_role is None:
        raise RoleNotFoundException(role_id=role_id)
    
    # Проверяем, используется ли роль
    if db_role.users:
        raise RoleInUseException(role_name=db_role.name)
    
    deleted_role = service.delete_role(role_id)
    return deleted_role