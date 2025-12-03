from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.database import async_session_maker
from app.models.gengres import GengresModel
from app.models.books import BooksModel
from app.schemes.gengres import GenreCreate, GenreUpdate, GenreResponse, GenreWithBooks

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
    prefix="/genres",
    tags=["genres"]
)


@router.post("/", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre_data: GenreCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый жанр
    """
    # Проверяем, нет ли уже жанра с таким названием
    existing_genre_stmt = select(GengresModel).where(
        func.lower(GengresModel.name) == func.lower(genre_data.name)
    )
    existing_genre_result = await db.execute(existing_genre_stmt)
    existing_genre = existing_genre_result.scalar_one_or_none()
    
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Жанр с таким названием уже существует"
        )
    
    # Создаем жанр
    db_genre = GengresModel(
        name=genre_data.name,
        description=genre_data.description
    )
    
    db.add(db_genre)
    await db.commit()
    await db.refresh(db_genre)
    
    # Подсчитываем количество книг в жанре
    book_count_stmt = select(func.count()).where(BooksModel.genre_id == db_genre.id)
    book_count_result = await db.execute(book_count_stmt)
    book_count = book_count_result.scalar()
    
    genre_response = GenreResponse(
        **db_genre.__dict__,
        book_count=book_count
    )
    
    return genre_response


@router.get("/", response_model=List[GenreResponse])
async def get_genres(
    name: Optional[str] = Query(None, description="Поиск по названию"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    sort_by: str = Query("name", description="Сортировка (name, book_count, created_at)"),
    order: str = Query("asc", description="Порядок сортировки (asc, desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список жанров с фильтрацией и сортировкой
    """
    # Создаем базовый запрос с подсчетом книг
    stmt = select(
        GengresModel,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, GengresModel.id == BooksModel.genre_id
    ).group_by(
        GengresModel.id
    )
    
    # Применяем фильтр по названию
    if name:
        stmt = stmt.where(GengresModel.name.ilike(f"%{name}%"))
    
    # Применяем сортировку
    if sort_by == "name":
        if order == "desc":
            stmt = stmt.order_by(GengresModel.name.desc())
        else:
            stmt = stmt.order_by(GengresModel.name.asc())
    elif sort_by == "book_count":
        if order == "desc":
            stmt = stmt.order_by(func.count(BooksModel.id).desc())
        else:
            stmt = stmt.order_by(func.count(BooksModel.id).asc())
    elif sort_by == "created_at":
        if order == "desc":
            stmt = stmt.order_by(GengresModel.created_at.desc())
        else:
            stmt = stmt.order_by(GengresModel.created_at.asc())
    
    # Пагинация
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    genres = []
    for genre_model, book_count in rows:
        genre_dict = genre_model.__dict__
        genre_response = GenreResponse(
            **genre_dict,
            book_count=book_count
        )
        genres.append(genre_response)
    
    return genres


@router.get("/{genre_id}", response_model=GenreWithBooks)
async def get_genre(
    genre_id: int,
    include_books: bool = Query(False, description="Включить список книг"),
    skip_books: int = Query(0, ge=0),
    limit_books: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить жанр по ID с опциональным списком книг
    """
    stmt = select(GengresModel).where(GengresModel.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalar_one_or_none()
    
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )
    
    # Подсчитываем количество книг
    book_count_stmt = select(func.count()).where(BooksModel.genre_id == genre_id)
    book_count_result = await db.execute(book_count_stmt)
    book_count = book_count_result.scalar()
    
    # Получаем книги жанра, если нужно
    books = []
    if include_books:
        books_stmt = select(BooksModel).where(
            BooksModel.genre_id == genre_id
        ).offset(skip_books).limit(limit_books)
        
        books_result = await db.execute(books_stmt)
        books_models = books_result.scalars().all()
        
        books = [
            {
                "id": book.id,
                "title": book.title,
                "year": book.year,
                "author_id": book.author_id
            }
            for book in books_models
        ]
    
    genre_response = GenreWithBooks(
        **genre.__dict__,
        book_count=book_count,
        books=books if include_books else None
    )
    
    return genre_response


@router.patch("/{genre_id}", response_model=GenreResponse)
async def update_genre(
    genre_id: int,
    genre_data: GenreUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить информацию о жанре
    """
    stmt = select(GengresModel).where(GengresModel.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalar_one_or_none()
    
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )
    
    # Если меняется название, проверяем уникальность
    if genre_data.name is not None and genre_data.name != genre.name:
        existing_genre_stmt = select(GengresModel).where(
            func.lower(GengresModel.name) == func.lower(genre_data.name),
            GengresModel.id != genre_id
        )
        existing_genre_result = await db.execute(existing_genre_stmt)
        existing_genre = existing_genre_result.scalar_one_or_none()
        
        if existing_genre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Жанр с таким названием уже существует"
            )
    
    # Обновляем только переданные поля
    update_data = genre_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(genre, field, value)
    
    await db.commit()
    await db.refresh(genre)
    
    # Подсчитываем количество книг
    book_count_stmt = select(func.count()).where(BooksModel.genre_id == genre_id)
    book_count_result = await db.execute(book_count_stmt)
    book_count = book_count_result.scalar()
    
    genre_response = GenreResponse(
        **genre.__dict__,
        book_count=book_count
    )
    
    return genre_response


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить жанр
    """
    stmt = select(GengresModel).where(GengresModel.id == genre_id)
    result = await db.execute(stmt)
    genre = result.scalar_one_or_none()
    
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )
    
    # Проверяем, есть ли книги в этом жанре
    books_stmt = select(func.count()).where(BooksModel.genre_id == genre_id)
    books_result = await db.execute(books_stmt)
    book_count = books_result.scalar()
    
    if book_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить жанр, так как к нему привязано {book_count} книг"
        )
    
    await db.delete(genre)
    await db.commit()
    
    return None


@router.get("/{genre_id}/books", response_model=dict)
async def get_genre_books(
    genre_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все книги определенного жанра
    """
    # Проверяем существование жанра
    genre_stmt = select(GengresModel).where(GengresModel.id == genre_id)
    genre_result = await db.execute(genre_stmt)
    genre = genre_result.scalar_one_or_none()
    
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )
    
    # Получаем книги
    books_stmt = select(
        BooksModel
    ).where(
        BooksModel.genre_id == genre_id
    ).offset(skip).limit(limit)
    
    books_result = await db.execute(books_stmt)
    books = books_result.scalars().all()
    
    # Получаем общее количество для пагинации
    total_stmt = select(func.count()).where(BooksModel.genre_id == genre_id)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()
    
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "year": book.year,
            "author_id": book.author_id,
            "created_at": book.created_at
        }
        for book in books
    ]
    
    return {
        "genre": {
            "id": genre.id,
            "name": genre.name,
            "description": genre.description
        },
        "books": books_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/stats/popular")
async def get_popular_genres(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить самые популярные жанры (по количеству книг)
    """
    stmt = select(
        GengresModel.name,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, GengresModel.id == BooksModel.genre_id
    ).group_by(
        GengresModel.id, GengresModel.name
    ).order_by(
        func.count(BooksModel.id).desc()
    ).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "genre": genre_name,
            "book_count": book_count
        }
        for genre_name, book_count in rows
    ]


@router.get("/stats/summary")
async def get_genres_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить сводную статистику по жанрам
    """
    # Общее количество жанров
    total_genres_stmt = select(func.count()).select_from(GengresModel)
    total_genres_result = await db.execute(total_genres_stmt)
    total_genres = total_genres_result.scalar()
    
    # Жанры без книг
    genres_without_books_stmt = select(func.count()).select_from(GengresModel).outerjoin(
        BooksModel, GengresModel.id == BooksModel.genre_id
    ).where(BooksModel.id.is_(None))
    
    genres_without_books_result = await db.execute(genres_without_books_stmt)
    genres_without_books = genres_without_books_result.scalar()
    
    # Среднее количество книг на жанр
    avg_books_stmt = select(func.avg(func.count(BooksModel.id))).select_from(GengresModel).outerjoin(
        BooksModel, GengresModel.id == BooksModel.genre_id
    ).group_by(GengresModel.id)
    
    avg_books_result = await db.execute(avg_books_stmt)
    avg_books = avg_books_result.scalar()
    
    # Жанры с наибольшим и наименьшим количеством книг
    max_books_stmt = select(
        GengresModel.name,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, GengresModel.id == BooksModel.genre_id
    ).group_by(
        GengresModel.id, GengresModel.name
    ).order_by(
        func.count(BooksModel.id).desc()
    ).limit(1)
    
    max_books_result = await db.execute(max_books_stmt)
    max_books_row = max_books_result.first()
    
    min_books_stmt = select(
        GengresModel.name,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, GengresModel.id == BooksModel.genre_id
    ).group_by(
        GengresModel.id, GengresModel.name
    ).order_by(
        func.count(BooksModel.id).asc()
    ).limit(1)
    
    min_books_result = await db.execute(min_books_stmt)
    min_books_row = min_books_result.first()
    
    return {
        "total_genres": total_genres,
        "genres_without_books": genres_without_books,
        "avg_books_per_genre": float(avg_books) if avg_books else 0,
        "most_popular_genre": {
            "name": max_books_row[0] if max_books_row else None,
            "book_count": max_books_row[1] if max_books_row else 0
        },
        "least_popular_genre": {
            "name": min_books_row[0] if min_books_row else None,
            "book_count": min_books_row[1] if min_books_row else 0
        }
    }