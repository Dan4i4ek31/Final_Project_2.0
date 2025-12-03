from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.database import async_session_maker
from app.models.book_comments import Book_commentsModel
from app.models.books import BooksModel
from app.models.users import UserModel
from app.schemes.books_comments import BookCommentCreate, BookCommentUpdate, BookCommentResponse

# Создаем функцию get_db прямо здесь
async def get_db() -> AsyncSession: # type: ignore
    """
    Асинхронная зависимость для получения сессии БД.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

router = APIRouter(
    prefix="/book-comments",
    tags=["book-comments"]
)


@router.post("/", response_model=BookCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: BookCommentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый комментарий к книге
    """
    # Проверяем существование книги
    book_stmt = select(BooksModel).where(BooksModel.id == comment_data.book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена"
        )
    
    # Проверяем существование пользователя
    user_stmt = select(UserModel).where(UserModel.id == comment_data.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Создаем комментарий
    db_comment = Book_commentsModel(
        book_id=comment_data.book_id,
        user_id=comment_data.user_id,
        comment_text=comment_data.comment_text
    )
    
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    
    # Добавляем имена пользователя и книги в ответ
    comment_response = BookCommentResponse(
        **db_comment.__dict__,
        user_name=user.username if hasattr(user, 'username') else user.email,
        book_title=book.title
    )
    
    return comment_response


@router.get("/", response_model=List[BookCommentResponse])
async def get_comments(
    book_id: Optional[int] = Query(None, description="Фильтр по ID книги"),
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    order_by: str = Query("created_at", description="Сортировка (created_at, updated_at)"),
    order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список комментариев с фильтрацией
    """
    stmt = select(
        Book_commentsModel,
        UserModel.username.label("user_name"),
        BooksModel.title.label("book_title")
    ).join(
        UserModel, Book_commentsModel.user_id == UserModel.id
    ).join(
        BooksModel, Book_commentsModel.book_id == BooksModel.id
    )
    
    # Применяем фильтры
    if book_id is not None:
        stmt = stmt.where(Book_commentsModel.book_id == book_id)
    
    if user_id is not None:
        stmt = stmt.where(Book_commentsModel.user_id == user_id)
    
    # Сортировка
    if order_by == "created_at":
        if order == "desc":
            stmt = stmt.order_by(Book_commentsModel.created_at.desc())
        else:
            stmt = stmt.order_by(Book_commentsModel.created_at.asc())
    elif order_by == "updated_at":
        if order == "desc":
            stmt = stmt.order_by(Book_commentsModel.updated_at.desc())
        else:
            stmt = stmt.order_by(Book_commentsModel.updated_at.asc())
    
    # Пагинация
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    comments = []
    for comment_model, user_name, book_title in rows:
        comment_dict = comment_model.__dict__
        comment_response = BookCommentResponse(
            **comment_dict,
            user_name=user_name,
            book_title=book_title
        )
        comments.append(comment_response)
    
    return comments


@router.get("/{comment_id}", response_model=BookCommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить комментарий по ID
    """
    stmt = select(
        Book_commentsModel,
        UserModel.username.label("user_name"),
        BooksModel.title.label("book_title")
    ).join(
        UserModel, Book_commentsModel.user_id == UserModel.id
    ).join(
        BooksModel, Book_commentsModel.book_id == BooksModel.id
    ).where(Book_commentsModel.id == comment_id)
    
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    comment, user_name, book_title = row
    
    comment_response = BookCommentResponse(
        **comment.__dict__,
        user_name=user_name,
        book_title=book_title
    )
    
    return comment_response


@router.patch("/{comment_id}", response_model=BookCommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: BookCommentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить комментарий
    """
    stmt = select(Book_commentsModel).where(Book_commentsModel.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    # Проверяем, что пользователь обновляет свой комментарий
    # (В реальном приложении здесь должна быть проверка авторизации)
    
    # Обновляем только переданные поля
    update_data = comment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    
    await db.commit()
    await db.refresh(comment)
    
    # Получаем актуальные данные пользователя и книги для ответа
    user_stmt = select(UserModel).where(UserModel.id == comment.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    book_stmt = select(BooksModel).where(BooksModel.id == comment.book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()
    
    user_name = user.username if user and hasattr(user, 'username') else None
    book_title = book.title if book else None
    
    comment_response = BookCommentResponse(
        **comment.__dict__,
        user_name=user_name,
        book_title=book_title
    )
    
    return comment_response


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить комментарий
    """
    stmt = select(Book_commentsModel).where(Book_commentsModel.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    # Проверяем, что пользователь удаляет свой комментарий
    # (В реальном приложении здесь должна быть проверка авторизации)
    
    await db.delete(comment)
    await db.commit()
    
    return None


@router.get("/book/{book_id}/comments", response_model=List[BookCommentResponse])
async def get_book_comments(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все комментарии к конкретной книге
    """
    # Проверяем существование книги
    book_stmt = select(BooksModel).where(BooksModel.id == book_id)
    book_result = await db.execute(book_stmt)
    book = book_result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена"
        )
    
    stmt = select(
        Book_commentsModel,
        UserModel.username.label("user_name"),
        BooksModel.title.label("book_title")
    ).join(
        UserModel, Book_commentsModel.user_id == UserModel.id
    ).join(
        BooksModel, Book_commentsModel.book_id == BooksModel.id
    ).where(
        Book_commentsModel.book_id == book_id
    ).order_by(
        Book_commentsModel.created_at.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    comments = []
    for comment_model, user_name, book_title in rows:
        comment_dict = comment_model.__dict__
        comment_response = BookCommentResponse(
            **comment_dict,
            user_name=user_name,
            book_title=book_title
        )
        comments.append(comment_response)
    
    return comments


@router.get("/user/{user_id}/comments", response_model=List[BookCommentResponse])
async def get_user_comments(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все комментарии конкретного пользователя
    """
    # Проверяем существование пользователя
    user_stmt = select(UserModel).where(UserModel.id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    stmt = select(
        Book_commentsModel,
        UserModel.username.label("user_name"),
        BooksModel.title.label("book_title")
    ).join(
        UserModel, Book_commentsModel.user_id == UserModel.id
    ).join(
        BooksModel, Book_commentsModel.book_id == BooksModel.id
    ).where(
        Book_commentsModel.user_id == user_id
    ).order_by(
        Book_commentsModel.created_at.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    comments = []
    for comment_model, user_name, book_title in rows:
        comment_dict = comment_model.__dict__
        comment_response = BookCommentResponse(
            **comment_dict,
            user_name=user_name,
            book_title=book_title
        )
        comments.append(comment_response)
    
    return comments


@router.get("/stats/count")
async def get_comments_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику по комментариям
    """
    # Общее количество комментариев
    total_stmt = select(func.count()).select_from(Book_commentsModel)
    total_result = await db.execute(total_stmt)
    total_comments = total_result.scalar()
    
    # Количество комментариев по книгам (топ 5)
    book_stmt = select(
        BooksModel.title,
        func.count().label("count")
    ).join(
        Book_commentsModel, Book_commentsModel.book_id == BooksModel.id
    ).group_by(
        BooksModel.id, BooksModel.title
    ).order_by(
        func.count().desc()
    ).limit(5)
    
    book_result = await db.execute(book_stmt)
    comments_by_book = book_result.all()
    
    # Количество комментариев по пользователям (топ 5)
    user_stmt = select(
        UserModel.username,
        func.count().label("count")
    ).join(
        Book_commentsModel, Book_commentsModel.user_id == UserModel.id
    ).group_by(
        UserModel.id, UserModel.username
    ).order_by(
        func.count().desc()
    ).limit(5)
    
    user_result = await db.execute(user_stmt)
    comments_by_user = user_result.all()
    
    # Среднее количество комментариев на книгу
    avg_stmt = select(func.avg(func.count())).select_from(Book_commentsModel).group_by(Book_commentsModel.book_id)
    avg_result = await db.execute(avg_stmt)
    avg_comments = avg_result.scalar()
    
    return {
        "total_comments": total_comments,
        "avg_comments_per_book": float(avg_comments) if avg_comments else 0,
        "top_books_comments": [{"book": book, "count": count} for book, count in comments_by_book],
        "top_users_comments": [{"user": user, "count": count} for user, count in comments_by_user]
    }