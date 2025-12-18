from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine
from app.models import (
    RoleModel,
    UserModel,
    BooksModel,
    AuthorsModel,
    GengresModel,
    BookCommentsModel,
    ShelfModel
)


class RoleAdmin(ModelView, model=RoleModel):
    """Admin view для ролей пользователей"""
    column_list = [RoleModel.id, RoleModel.name]
    column_details_exclude_list = [RoleModel.users]
    page_size = 10
    name = "Роль"
    name_plural = "Роли"
    icon = "fa-solid fa-shield"


class UserAdmin(ModelView, model=UserModel):
    """Admin view для пользователей"""
    column_list = [
        UserModel.id,
        UserModel.email,
        UserModel.name,
        UserModel.role_id
    ]
    column_details_exclude_list = [
        UserModel.password_hash,
        UserModel.book_comments,
        UserModel.shelf
    ]
    page_size = 10
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"


class AuthorsAdmin(ModelView, model=AuthorsModel):
    """Admin view для авторов"""
    column_list = [
        AuthorsModel.id,
        AuthorsModel.name,
    ]
    page_size = 10
    name = "Автор"
    name_plural = "Авторы"
    icon = "fa-solid fa-pen-nib"


class GengresAdmin(ModelView, model=GengresModel):
    """Admin view для жанров"""
    column_list = [
        GengresModel.id,
        GengresModel.name,
    ]
    page_size = 10
    name = "Жанр"
    name_plural = "Жанры"
    icon = "fa-solid fa-bookmark"


class BooksAdmin(ModelView, model=BooksModel):
    """Admin view для книг"""
    column_list = [
        BooksModel.id,
        BooksModel.title,
        BooksModel.author_id,
        BooksModel.genre_id,
        BooksModel.year,
    ]
    column_details_exclude_list = [
        BooksModel.description,
        BooksModel.book_comments
    ]
    page_size = 10
    name = "Книга"
    name_plural = "Книги"
    icon = "fa-solid fa-book"


class BookCommentsAdmin(ModelView, model=BookCommentsModel):
    """Admin view для комментариев к книгам"""
    column_list = [
        BookCommentsModel.id,
        BookCommentsModel.user_id,
        BookCommentsModel.book_id,
        BookCommentsModel.comment_text,
        BookCommentsModel.created_at
    ]
    page_size = 10
    name = "Комментарий"
    name_plural = "Комментарии"
    icon = "fa-solid fa-comments"


class ShelfAdmin(ModelView, model=ShelfModel):
    """Admin view для полок пользователей"""
    column_list = [
        ShelfModel.id,
        ShelfModel.user_id,
        ShelfModel.book_id,
        ShelfModel.status_read
    ]
    page_size = 10
    name = "Полка"
    name_plural = "Полки"
    icon = "fa-solid fa-library"


def setup_admin(app, engine: AsyncEngine):
    """Инициализация админ-панели
    
    Args:
        app: FastAPI приложение
        engine: AsyncEngine для SQLAlchemy
    """
    admin = Admin(
        app=app,
        engine=engine,
        title="Library Admin",
        logo_url="https://raw.githubusercontent.com/aminalaee/sqladmin/main/docs/assets/images/logo.png",
        base_url="/admin",
        authentication_backend=None,  # Можно добавить аутентификацию позже
    )
    
    # Регистрируем ModelViews
    admin.register_model(RoleAdmin)
    admin.register_model(UserAdmin)
    admin.register_model(AuthorsAdmin)
    admin.register_model(GengresAdmin)
    admin.register_model(BooksAdmin)
    admin.register_model(BookCommentsAdmin)
    admin.register_model(ShelfAdmin)
    
    return admin
