from .roles import router as roles_router
from .users import router as users_router
from .books import router as books_router
from .gengres import router as genres_router
from .authors import router as authors_router
from .book_comments import router as book_comments_router
from .shelf import router as shelf_router

__all__ = [
    "roles_router",
    "users_router",
    "books_router",
    "genres_router",
    "authors_router",
    "book_comments_router",
    "shelf_router",
]