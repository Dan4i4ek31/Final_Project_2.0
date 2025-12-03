from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.shelf import ShelfModel
from app.schemes.shelf import ShelfCreate, ShelfUpdate, ShelfResponse

# Импортируем ваш async_session_maker
from app.database.database import async_session_maker

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
    prefix="/shelves",
    tags=["shelves"]
)


@router.post("/", response_model=ShelfResponse, status_code=status.HTTP_201_CREATED)
async def add_book_to_shelf(
    shelf_data: ShelfCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Добавить книгу на полку пользователя
    """
    # Проверяем, есть ли уже такая книга на полке пользователя
    stmt = select(ShelfModel).where(
        ShelfModel.user_id == shelf_data.user_id,
        ShelfModel.book_id == shelf_data.book_id
    )
    result = await db.execute(stmt)
    existing_shelf = result.scalar_one_or_none()
    
    if existing_shelf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Эта книга уже находится на полке пользователя"
        )
    
    # Создаем новую запись на полке
    db_shelf = ShelfModel(
        book_id=shelf_data.book_id,
        user_id=shelf_data.user_id,
        status_read=shelf_data.status_read
    )
    
    db.add(db_shelf)
    await db.commit()
    await db.refresh(db_shelf)
    
    return db_shelf


@router.get("/", response_model=List[ShelfResponse])
async def get_shelves(
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    book_id: Optional[int] = Query(None, description="Фильтр по ID книги"),
    status_read: Optional[bool] = Query(None, description="Фильтр по статусу прочтения"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все записи на полках с возможностью фильтрации
    """
    stmt = select(ShelfModel)
    
    # Применяем фильтры, если они указаны
    if user_id is not None:
        stmt = stmt.where(ShelfModel.user_id == user_id)
    
    if book_id is not None:
        stmt = stmt.where(ShelfModel.book_id == book_id)
    
    if status_read is not None:
        stmt = stmt.where(ShelfModel.status_read == status_read)
    
    # Выполняем запрос с пагинацией
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    shelves = result.scalars().all()
    
    return shelves


@router.get("/{shelf_id}", response_model=ShelfResponse)
async def get_shelf(
    shelf_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить конкретную запись с полки по ID
    """
    stmt = select(ShelfModel).where(ShelfModel.id == shelf_id)
    result = await db.execute(stmt)
    shelf = result.scalar_one_or_none()
    
    if not shelf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись на полке не найдена"
        )
    
    return shelf


@router.get("/user/{user_id}/books", response_model=List[ShelfResponse])
async def get_user_books(
    user_id: int,
    status_read: Optional[bool] = Query(None, description="Фильтр по статусу прочтения"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все книги пользователя с его полки
    """
    stmt = select(ShelfModel).where(ShelfModel.user_id == user_id)
    
    if status_read is not None:
        stmt = stmt.where(ShelfModel.status_read == status_read)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    shelves = result.scalars().all()
    
    return shelves


@router.patch("/{shelf_id}", response_model=ShelfResponse)
async def update_shelf_status(
    shelf_id: int,
    shelf_data: ShelfUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить статус прочтения книги на полке
    """
    # Находим запись на полке
    stmt = select(ShelfModel).where(ShelfModel.id == shelf_id)
    result = await db.execute(stmt)
    shelf = result.scalar_one_or_none()
    
    if not shelf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись на полке не найдена"
        )
    
    # Обновляем только переданные поля
    update_data = shelf_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shelf, field, value)
    
    await db.commit()
    await db.refresh(shelf)
    
    return shelf


@router.put("/{shelf_id}/read", response_model=ShelfResponse)
async def mark_as_read(
    shelf_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Отметить книгу как прочитанную
    """
    stmt = select(ShelfModel).where(ShelfModel.id == shelf_id)
    result = await db.execute(stmt)
    shelf = result.scalar_one_or_none()
    
    if not shelf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись на полке не найдена"
        )
    
    shelf.status_read = True
    await db.commit()
    await db.refresh(shelf)
    
    return shelf


@router.put("/{shelf_id}/unread", response_model=ShelfResponse)
async def mark_as_unread(
    shelf_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Отметить книгу как непрочитанную
    """
    stmt = select(ShelfModel).where(ShelfModel.id == shelf_id)
    result = await db.execute(stmt)
    shelf = result.scalar_one_or_none()
    
    if not shelf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись на полке не найдена"
        )
    
    shelf.status_read = False
    await db.commit()
    await db.refresh(shelf)
    
    return shelf


@router.delete("/{shelf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book_from_shelf(
    shelf_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить книгу с полки пользователя
    """
    stmt = select(ShelfModel).where(ShelfModel.id == shelf_id)
    result = await db.execute(stmt)
    shelf = result.scalar_one_or_none()
    
    if not shelf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись на полке не найдена"
        )
    
    await db.delete(shelf)
    await db.commit()
    
    return None


@router.get("/user/{user_id}/stats")
async def get_user_reading_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику чтения пользователя
    """
    # Получаем все книги пользователя
    stmt = select(ShelfModel).where(ShelfModel.user_id == user_id)
    result = await db.execute(stmt)
    user_shelves = result.scalars().all()
    
    total_books = len(user_shelves)
    read_books = sum(1 for shelf in user_shelves if shelf.status_read)
    unread_books = total_books - read_books
    
    return {
        "user_id": user_id,
        "total_books": total_books,
        "read_books": read_books,
        "unread_books": unread_books,
        "reading_progress": f"{(read_books / total_books * 100):.1f}%" if total_books > 0 else "0%"
    }


@router.get("/book/{book_id}/users", response_model=List[ShelfResponse])
async def get_book_readers(
    book_id: int,
    status_read: Optional[bool] = Query(None, description="Фильтр по статусу прочтения"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить всех пользователей, у которых есть эта книга на полке
    """
    stmt = select(ShelfModel).where(ShelfModel.book_id == book_id)
    
    if status_read is not None:
        stmt = stmt.where(ShelfModel.status_read == status_read)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    shelves = result.scalars().all()
    
    return shelves