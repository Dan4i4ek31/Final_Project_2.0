from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database.database import async_session_maker
from app.models.books import BooksModel
from app.models.authors import AuthorsModel
from app.models.gengres import GengresModel  #
from app.schemes.books import BookCreate, BookUpdate, BookResponse, BookWithRelations

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
    prefix="/books",
    tags=["books"]
)


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую книгу
    """
    # Проверяем существование автора
    author_stmt = select(AuthorsModel).where(AuthorsModel.id == book_data.author_id)
    author_result = await db.execute(author_stmt)
    author = author_result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            
            detail="Автор не найден"
        )
    
    # Проверяем существование жанра
    genre_stmt = select(GengresModel).where(GengresModel.id == book_data.genre_id)
    genre_result = await db.execute(genre_stmt)
    genre = genre_result.scalar_one_or_none()
    
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жанр не найден"
        )
    
    # Проверяем, нет ли уже книги с таким названием и автором
    existing_book_stmt = select(BooksModel).where(
        BooksModel.title == book_data.title,
        BooksModel.author_id == book_data.author_id,
        BooksModel.year == book_data.year
    )
    existing_book_result = await db.execute(existing_book_stmt)
    existing_book = existing_book_result.scalar_one_or_none()
    
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Книга с таким названием, автором и годом уже существует"
        )
    
    # Создаем книгу
    db_book = BooksModel(
        title=book_data.title,
        description=book_data.description,
        author_id=book_data.author_id,
        genre_id=book_data.genre_id,
        year=book_data.year
    )
    
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    
    # Добавляем имена автора и жанра в ответ
    book_response = BookResponse(
        **db_book.__dict__,
        author_name=author.name,
        genre_name=genre.name
    )
    
    return book_response


@router.get("/", response_model=List[BookResponse])
async def get_books(
    title: Optional[str] = Query(None, description="Поиск по названию"),
    author_id: Optional[int] = Query(None, description="Фильтр по автору"),
    genre_id: Optional[int] = Query(None, description="Фильтр по жанру"),
    year_from: Optional[int] = Query(None, description="Год от", ge=0),
    year_to: Optional[int] = Query(None, description="Год до", ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список книг с фильтрацией
    """
    stmt = select(
        BooksModel,
        AuthorsModel.name.label("author_name"),
        GengresModel.name.label("genre_name")
    ).join(
        AuthorsModel, BooksModel.author_id == AuthorsModel.id
    ).join(
        GengresModel, BooksModel.genre_id == GengresModel.id
    )
    
    # Применяем фильтры
    if title:
        stmt = stmt.where(BooksModel.title.ilike(f"%{title}%"))
    
    if author_id is not None:
        stmt = stmt.where(BooksModel.author_id == author_id)
    
    if genre_id is not None:
        stmt = stmt.where(BooksModel.genre_id == genre_id)
    
    if year_from is not None:
        stmt = stmt.where(BooksModel.year >= year_from)
    
    if year_to is not None:
        stmt = stmt.where(BooksModel.year <= year_to)
    
    # Пагинация
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    books = []
    for book_model, author_name, genre_name in rows:
        book_dict = book_model.__dict__
        book_response = BookResponse(
            **book_dict,
            author_name=author_name,
            genre_name=genre_name
        )
        books.append(book_response)
    
    return books


@router.get("/{book_id}", response_model=BookWithRelations)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить книгу по ID с детальной информацией
    """
    # Получаем книгу с автором и жанром
    stmt = select(
        BooksModel,
        AuthorsModel,
        GengresModel
    ).join(
        AuthorsModel, BooksModel.author_id == AuthorsModel.id
    ).join(
        GengresModel, BooksModel.genre_id == GengresModel.id
    ).where(BooksModel.id == book_id)
    
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена"
        )
    
    book, author, genre = row
    
    # Подсчитываем количество комментариев
    from app.models.book_comments import Book_commentsModel
    comment_stmt = select(func.count()).where(Book_commentsModel.book_id == book_id)
    comment_result = await db.execute(comment_stmt)
    comment_count = comment_result.scalar()
    
    # Подсчитываем количество на полках
    from app.models.shelf import ShelfModel
    shelf_stmt = select(func.count()).where(ShelfModel.book_id == book_id)
    shelf_result = await db.execute(shelf_stmt)
    shelf_count = shelf_result.scalar()
    
    book_response = BookWithRelations(
        **book.__dict__,
        author_name=author.name,
        genre_name=genre.name,
        author={"id": author.id, "name": author.name} if author else None,
        genre={"id": genre.id, "name": genre.name} if genre else None,
        comment_count=comment_count,
        shelf_count=shelf_count
    )
    
    return book_response


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить информацию о книге
    """
    stmt = select(BooksModel).where(BooksModel.id == book_id)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена"
        )
    
    # Проверяем автора, если он обновляется
    if book_data.author_id is not None:
        author_stmt = select(AuthorsModel).where(AuthorsModel.id == book_data.author_id)
        author_result = await db.execute(author_stmt)
        author = author_result.scalar_one_or_none()
        
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Автор не найден"
            )
    
    # Проверяем жанр, если он обновляется
    if book_data.genre_id is not None:
        genre_stmt = select(GengresModel).where(GengresModel.id == book_data.genre_id)
        genre_result = await db.execute(genre_stmt)
        genre = genre_result.scalar_one_or_none()
        
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Жанр не найден"
            )
    
    # Обновляем только переданные поля
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    await db.commit()
    await db.refresh(book)
    
    # Получаем актуальные данные автора и жанра для ответа
    if book_data.author_id is not None or book_data.genre_id is not None:
        author_stmt = select(AuthorsModel).where(AuthorsModel.id == book.author_id)
        author_result = await db.execute(author_stmt)
        author = author_result.scalar_one_or_none()
        
        genre_stmt = select(GengresModel).where(GengresModel.id == book.genre_id)
        genre_result = await db.execute(genre_stmt)
        genre = genre_result.scalar_one_or_none()
        
        author_name = author.name if author else None
        genre_name = genre.name if genre else None
    else:
        author_name = None
        genre_name = None
    
    book_response = BookResponse(
        **book.__dict__,
        author_name=author_name,
        genre_name=genre_name
    )
    
    return book_response


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить книгу
    """
    stmt = select(BooksModel).where(BooksModel.id == book_id)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена"
        )
    
    await db.delete(book)
    await db.commit()
    
    return None


@router.get("/search/", response_model=List[BookResponse])
async def search_books(
    q: str = Query(..., description="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск книг по названию, описанию, автору или жанру
    """
    stmt = select(
        BooksModel,
        AuthorsModel.name.label("author_name"),
        GengresModel.name.label("genre_name")
    ).join(
        AuthorsModel, BooksModel.author_id == AuthorsModel.id
    ).join(
        GengresModel, BooksModel.genre_id == GengresModel.id
    ).where(
        or_(
            BooksModel.title.ilike(f"%{q}%"),
            BooksModel.description.ilike(f"%{q}%"),
            AuthorsModel.name.ilike(f"%{q}%"),
            GengresModel.name.ilike(f"%{q}%")
        )
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    books = []
    for book_model, author_name, genre_name in rows:
        book_dict = book_model.__dict__
        book_response = BookResponse(
            **book_dict,
            author_name=author_name,
            genre_name=genre_name
        )
        books.append(book_response)
    
    return books


@router.get("/stats/count")
async def get_books_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статистику по книгам
    """
    # Общее количество книг
    total_stmt = select(func.count()).select_from(BooksModel)
    total_result = await db.execute(total_stmt)
    total_books = total_result.scalar()
    
    # Книг по годам (последние 5 лет)
    from datetime import datetime
    current_year = datetime.now().year
    year_stmt = select(
        BooksModel.year,
        func.count().label("count")
    ).where(
        BooksModel.year >= current_year - 5
    ).group_by(
        BooksModel.year
    ).order_by(
        BooksModel.year.desc()
    )
    
    year_result = await db.execute(year_stmt)
    books_by_year = year_result.all()
    
    # Книг по жанрам (топ 5)
    genre_stmt = select(
        GengresModel.name,
        func.count().label("count")
    ).join(
        BooksModel, BooksModel.genre_id == GengresModel.id
    ).group_by(
        GengresModel.id, GengresModel.name
    ).order_by(
        func.count().desc()
    ).limit(5)
    
    genre_result = await db.execute(genre_stmt)
    books_by_genre = genre_result.all()
    
    return {
        "total_books": total_books,
        "books_by_year": [{"year": year, "count": count} for year, count in books_by_year],
        "top_genres": [{"genre": genre, "count": count} for genre, count in books_by_genre]
    }