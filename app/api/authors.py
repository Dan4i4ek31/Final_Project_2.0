from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, extract
from datetime import date, datetime
from app.database.database import async_session_maker
from app.models.authors import AuthorsModel
from app.models.books import BooksModel
from app.schemes.authors import AuthorCreate, AuthorUpdate, AuthorResponse, AuthorWithBooks

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
    prefix="/authors",
    tags=["authors"]
)


@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создать нового автора
    """
    # Проверяем, нет ли уже автора с таким именем
    existing_author_stmt = select(AuthorsModel).where(
        func.lower(AuthorsModel.name) == func.lower(author_data.name)
    )
    existing_author_result = await db.execute(existing_author_stmt)
    existing_author = existing_author_result.scalar_one_or_none()
    
    if existing_author:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Автор с таким именем уже существует"
        )
    
    # Создаем автора
    db_author = AuthorsModel(
        name=author_data.name,
        biography=author_data.biography,
        birth_date=author_data.birth_date,
        country=author_data.country
    )
    
    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    
    # Подсчитываем количество книг автора
    book_count_stmt = select(func.count()).where(BooksModel.author_id == db_author.id)
    book_count_result = await db.execute(book_count_stmt)
    book_count = book_count_result.scalar()
    
    author_response = AuthorResponse(
        **db_author.__dict__,
        book_count=book_count
    )
    
    return author_response


@router.get("/", response_model=List[AuthorResponse])
async def get_authors(
    name: Optional[str] = Query(None, description="Поиск по имени"),
    country: Optional[str] = Query(None, description="Фильтр по стране"),
    min_books: Optional[int] = Query(None, description="Минимальное количество книг", ge=0),
    max_books: Optional[int] = Query(None, description="Максимальное количество книг", ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    sort_by: str = Query("name", description="Сортировка (name, book_count, created_at, birth_date)"),
    order: str = Query("asc", description="Порядок сортировки (asc, desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список авторов с фильтрацией и сортировкой
    """
    # Создаем базовый запрос с подсчетом книг
    stmt = select(
        AuthorsModel,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, AuthorsModel.id == BooksModel.author_id
    ).group_by(
        AuthorsModel.id
    )
    
    # Применяем фильтры
    if name:
        stmt = stmt.where(AuthorsModel.name.ilike(f"%{name}%"))
    
    if country:
        stmt = stmt.where(AuthorsModel.country.ilike(f"%{country}%"))
    
    # Фильтр по количеству книг
    if min_books is not None or max_books is not None:
        having_clause = []
        if min_books is not None:
            having_clause.append(func.count(BooksModel.id) >= min_books)
        if max_books is not None:
            having_clause.append(func.count(BooksModel.id) <= max_books)
        
        if having_clause:
            from sqlalchemy import and_
            stmt = stmt.having(and_(*having_clause))
    
    # Применяем сортировку
    if sort_by == "name":
        if order == "desc":
            stmt = stmt.order_by(AuthorsModel.name.desc())
        else:
            stmt = stmt.order_by(AuthorsModel.name.asc())
    elif sort_by == "book_count":
        if order == "desc":
            stmt = stmt.order_by(func.count(BooksModel.id).desc())
        else:
            stmt = stmt.order_by(func.count(BooksModel.id).asc())
    elif sort_by == "created_at":
        if order == "desc":
            stmt = stmt.order_by(AuthorsModel.created_at.desc())
        else:
            stmt = stmt.order_by(AuthorsModel.created_at.asc())
    elif sort_by == "birth_date":
        if order == "desc":
            stmt = stmt.order_by(AuthorsModel.birth_date.desc())
        else:
            stmt = stmt.order_by(AuthorsModel.birth_date.asc())
    
    # Пагинация
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    authors = []
    for author_model, book_count in rows:
        author_dict = author_model.__dict__
        author_response = AuthorResponse(
            **author_dict,
            book_count=book_count
        )
        authors.append(author_response)
    
    return authors


@router.get("/{author_id}", response_model=AuthorWithBooks)
async def get_author(
    author_id: int,
    include_books: bool = Query(False, description="Включить список книг"),
    skip_books: int = Query(0, ge=0),
    limit_books: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить автора по ID с опциональным списком книг
    """
    stmt = select(AuthorsModel).where(AuthorsModel.id == author_id)
    result = await db.execute(stmt)
    author = result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден"
        )
    
    # Подсчитываем количество книг
    book_count_stmt = select(func.count()).where(BooksModel.author_id == author_id)
    book_count_result = await db.execute(book_count_stmt)
    book_count = book_count_result.scalar()
    
    # Получаем книги автора, если нужно
    books = []
    if include_books:
        books_stmt = select(BooksModel).where(
            BooksModel.author_id == author_id
        ).offset(skip_books).limit(limit_books)
        
        books_result = await db.execute(books_stmt)
        books_models = books_result.scalars().all()
        
        books = [
            {
                "id": book.id,
                "title": book.title,
                "year": book.year,
                "genre_id": book.genre_id,
                "description": book.description
            }
            for book in books_models
        ]
    
    author_response = AuthorWithBooks(
        **author.__dict__,
        book_count=book_count,
        books=books if include_books else None
    )
    
    return author_response


@router.patch("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить информацию об авторе
    """
    stmt = select(AuthorsModel).where(AuthorsModel.id == author_id)
    result = await db.execute(stmt)
    author = result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден"
        )
    
    # Если меняется имя, проверяем уникальность
    if author_data.name is not None and author_data.name != author.name:
        existing_author_stmt = select(AuthorsModel).where(
            func.lower(AuthorsModel.name) == func.lower(author_data.name),
            AuthorsModel.id != author_id
        )
        existing_author_result = await db.execute(existing_author_stmt)
        existing_author = existing_author_result.scalar_one_or_none()
        
        if existing_author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Автор с таким именем уже существует"
            )
    
    # Обновляем только переданные поля
    update_data = author_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(author, field, value)
    
    await db.commit()
    await db.refresh(author)
    
    # Подсчитываем количество книг
    book_count_stmt = select(func.count()).where(BooksModel.author_id == author_id)
    book_count_result = await db.execute(book_count_stmt)
    book_count = book_count_result.scalar()
    
    author_response = AuthorResponse(
        **author.__dict__,
        book_count=book_count
    )
    
    return author_response


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить автора
    """
    stmt = select(AuthorsModel).where(AuthorsModel.id == author_id)
    result = await db.execute(stmt)
    author = result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден"
        )
    
    # Проверяем, есть ли книги у этого автора
    books_stmt = select(func.count()).where(BooksModel.author_id == author_id)
    books_result = await db.execute(books_stmt)
    book_count = books_result.scalar()
    
    if book_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить автора, так как у него есть {book_count} книг"
        )
    
    await db.delete(author)
    await db.commit()
    
    return None


@router.get("/{author_id}/books", response_model=dict)
async def get_author_books(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: str = Query("year", description="Сортировка (title, year, created_at)"),
    order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все книги определенного автора
    """
    # Проверяем существование автора
    author_stmt = select(AuthorsModel).where(AuthorsModel.id == author_id)
    author_result = await db.execute(author_stmt)
    author = author_result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден"
        )
    
    # Получаем книги
    books_stmt = select(
        BooksModel
    ).where(
        BooksModel.author_id == author_id
    )
    
    # Сортировка
    if sort_by == "title":
        if order == "desc":
            books_stmt = books_stmt.order_by(BooksModel.title.desc())
        else:
            books_stmt = books_stmt.order_by(BooksModel.title.asc())
    elif sort_by == "year":
        if order == "desc":
            books_stmt = books_stmt.order_by(BooksModel.year.desc())
        else:
            books_stmt = books_stmt.order_by(BooksModel.year.asc())
    elif sort_by == "created_at":
        if order == "desc":
            books_stmt = books_stmt.order_by(BooksModel.created_at.desc())
        else:
            books_stmt = books_stmt.order_by(BooksModel.created_at.asc())
    
    # Пагинация
    books_stmt = books_stmt.offset(skip).limit(limit)
    
    books_result = await db.execute(books_stmt)
    books = books_result.scalars().all()
    
    # Получаем общее количество для пагинации
    total_stmt = select(func.count()).where(BooksModel.author_id == author_id)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()
    
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "year": book.year,
            "genre_id": book.genre_id,
            "created_at": book.created_at
        }
        for book in books
    ]
    
    return {
        "author": {
            "id": author.id,
            "name": author.name,
            "country": author.country
        },
        "books": books_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/stats/popular")
async def get_popular_authors(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить самых популярных авторов (по количеству книг)
    """
    stmt = select(
        AuthorsModel.name,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, AuthorsModel.id == BooksModel.author_id
    ).group_by(
        AuthorsModel.id, AuthorsModel.name
    ).order_by(
        func.count(BooksModel.id).desc()
    ).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "author": author_name,
            "book_count": book_count
        }
        for author_name, book_count in rows
    ]


@router.get("/stats/by-country")
async def get_authors_by_country(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику авторов по странам
    """
    stmt = select(
        AuthorsModel.country,
        func.count(AuthorsModel.id).label("author_count"),
        func.count(BooksModel.id).label("total_books")
    ).outerjoin(
        BooksModel, AuthorsModel.id == BooksModel.author_id
    ).group_by(
        AuthorsModel.country
    ).order_by(
        func.count(AuthorsModel.id).desc()
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "country": country if country else "Не указана",
            "author_count": author_count,
            "total_books": total_books
        }
        for country, author_count, total_books in rows
    ]


@router.get("/search/", response_model=List[AuthorResponse])
async def search_authors(
    q: str = Query(..., description="Поисковый запрос (по имени, биографии, стране)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск авторов по имени, биографии или стране
    """
    stmt = select(
        AuthorsModel,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, AuthorsModel.id == BooksModel.author_id
    ).where(
        or_(
            AuthorsModel.name.ilike(f"%{q}%"),
            AuthorsModel.biography.ilike(f"%{q}%"),
            AuthorsModel.country.ilike(f"%{q}%")
        )
    ).group_by(
        AuthorsModel.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    authors = []
    for author_model, book_count in rows:
        author_dict = author_model.__dict__
        author_response = AuthorResponse(
            **author_dict,
            book_count=book_count
        )
        authors.append(author_response)
    
    return authors


@router.get("/birthdays/upcoming")
async def get_upcoming_birthdays(
    days: int = Query(30, description="Количество дней вперед", ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить авторов, у которых скоро день рождения
    """
    from datetime import timedelta
    
    today = date.today()
    end_date = today + timedelta(days=days)
    
    # Запрос для авторов с днями рождения в указанном диапазоне
    stmt = select(
        AuthorsModel,
        func.count(BooksModel.id).label("book_count")
    ).outerjoin(
        BooksModel, AuthorsModel.id == BooksModel.author_id
    ).where(
        AuthorsModel.birth_date.is_not(None)
    ).group_by(
        AuthorsModel.id
    )
    
    result = await db.execute(stmt)
    all_authors = result.all()
    
    upcoming_authors = []
    
    for author_model, book_count in all_authors:
        if author_model.birth_date:
            birth_date = author_model.birth_date.date() if isinstance(author_model.birth_date, datetime) else author_model.birth_date
            
            # Создаем дату дня рождения в текущем году
            birthday_this_year = birth_date.replace(year=today.year)
            
            # Если день рождения в этом году уже прошел, берем следующий год
            if birthday_this_year < today:
                birthday_this_year = birth_date.replace(year=today.year + 1)
            
            # Проверяем, попадает ли день рождения в диапазон
            if today <= birthday_this_year <= end_date:
                days_until = (birthday_this_year - today).days
                
                author_dict = author_model.__dict__
                author_response = AuthorResponse(
                    **author_dict,
                    book_count=book_count
                )
                
                upcoming_authors.append({
                    "author": author_response,
                    "birthday": birthday_this_year,
                    "days_until": days_until
                })
    
    # Сортируем по приближающемуся дню рождения
    upcoming_authors.sort(key=lambda x: x["days_until"])
    
    return upcoming_authors