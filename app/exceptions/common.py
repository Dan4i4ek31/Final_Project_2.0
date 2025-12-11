from fastapi import status
from .base import BaseAPIException


class ValidationException(BaseAPIException):
    """Исключение для ошибок валидации"""
    
    @property
    def status_code(self) -> int:
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @property
    def default_detail(self) -> str:
        return "Validation error"


class UnauthorizedException(BaseAPIException):
    """Исключение для случаев, когда пользователь не авторизован"""
    
    @property
    def status_code(self) -> int:
        return status.HTTP_401_UNAUTHORIZED
    
    @property
    def default_detail(self) -> str:
        return "Unauthorized"


class ForbiddenException(BaseAPIException):
    """Исключение для случаев, когда доступ запрещен"""
    
    @property
    def status_code(self) -> int:
        return status.HTTP_403_FORBIDDEN
    
    @property
    def default_detail(self) -> str:
        return "Forbidden"


class InternalServerErrorException(BaseAPIException):
    """Исключение для внутренних ошибок сервера"""
    
    @property
    def status_code(self) -> int:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @property
    def default_detail(self) -> str:
        return "Internal server error"


class BadRequestException(BaseAPIException):
    """Исключение для неверных запросов"""
    
    @property
    def status_code(self) -> int:
        return status.HTTP_400_BAD_REQUEST
    
    @property
    def default_detail(self) -> str:
        return "Bad request"