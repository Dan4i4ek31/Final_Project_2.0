from fastapi import HTTPException, status


class RoleNotFoundException(HTTPException):
    def __init__(self, role_id: int = None, role_name: str = None):
        if role_id is not None:
            detail = f"Role with id {role_id} not found"
        elif role_name is not None:
            detail = f"Role '{role_name}' not found"
        else:
            detail = "Role not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class RoleAlreadyExistsException(HTTPException):
    def __init__(self, role_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_name}' already exists"
        )


class RoleInUseException(HTTPException):
    def __init__(self, role_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role '{role_name}' because it is assigned to users"
        )