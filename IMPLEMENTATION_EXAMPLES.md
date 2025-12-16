# Примеры реализации обложек книг

На тот случай, если вы хотите имплементировать отображение обложек в вашем приложении.

## 1. HTML/Jinja2 Шаблоны

### Простые карточки книг

```html
<div class="book-card">
    {% if book.cover_image %}
        <img src="{{ book.cover_image }}" 
             alt="{{ book.title }}" 
             class="book-cover"
             loading="lazy">
    {% else %}
        <div class="book-cover placeholder">
            <span class="no-cover-icon">📚</span>
        </div>
    {% endif %}
    
    <div class="book-info">
        <h3 class="book-title">{{ book.title }}</h3>
        <p class="book-author">{{ book.author_name }}</p>
        <p class="book-year">{{ book.year }}</p>
    </div>
</div>
```

### с CSS стилизацией

```html
<style>
    .book-card {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .book-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .book-cover {
        width: 100%;
        height: 300px;
        object-fit: cover;
        background-color: #f5f5f5;
    }
    
    .book-cover.placeholder {
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-size: 48px;
    }
    
    .book-info {
        padding: 16px;
    }
    
    .book-title {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
        color: #333;
    }
    
    .book-author {
        margin: 0 0 4px 0;
        font-size: 14px;
        color: #666;
    }
    
    .book-year {
        margin: 0;
        font-size: 12px;
        color: #999;
    }
</style>
```

## 2. Python Код для Repository

### Получение книг с обложками

```python
from sqlalchemy.orm import Session
from app.models.books import BooksModel

def get_books_with_covers(session: Session, skip: int = 0, limit: int = 10):
    """
    Получить книги с обложками, сортированные по году
    """
    books = session.query(BooksModel)\
        .filter(BooksModel.cover_image.isnot(None))\
        .order_by(BooksModel.year.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return books

def get_books_without_covers(session: Session):
    """
    Получить книги без обложек
    """
    books = session.query(BooksModel)\
        .filter(BooksModel.cover_image.is_(None))\
        .all()
    return books

def update_book_cover(session: Session, book_id: int, cover_url: str):
    """
    Обновить URL обложки книги
    """
    book = session.query(BooksModel).filter(BooksModel.id == book_id).first()
    if book:
        book.cover_image = cover_url
        session.commit()
        return book
    return None
```

## 3. FastAPI Нтровки

### Эндпоинт для получения книг с обложками

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemes.books import Book
from app.database.database import get_db
from app.models.books import BooksModel

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/with-covers", response_model=list[Book])
async def get_books_with_covers(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Получить все книги с обложками
    """
    books = db.query(BooksModel)\
        .filter(BooksModel.cover_image.isnot(None))\
        .offset(skip)\
        .limit(limit)\
        .all()
    return books

@router.get("/by-genre/{genre_name}/with-covers", response_model=list[Book])
async def get_books_by_genre_with_covers(
    genre_name: str,
    db: Session = Depends(get_db)
):
    """
    Получить книги определенного жанра с обложками
    """
    books = db.query(BooksModel)\
        .join(BooksModel.genre)\
        .filter(
            (BooksModel.cover_image.isnot(None)) &
            (GengresModel.name == genre_name)
        )\
        .all()
    return books

@router.put("/{book_id}/cover")
async def update_book_cover(
    book_id: int,
    cover_url: str,
    db: Session = Depends(get_db)
):
    """
    Обновить URL обложки книги
    """
    book = db.query(BooksModel).filter(BooksModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book.cover_image = cover_url
    db.commit()
    db.refresh(book)
    return book
```

## 4. Данные JSON API

### Ответ для стособрания

```json
[
  {
    "id": 1,
    "title": "Война и мир",
    "description": "Эпическое полотно жизни и смерти...",
    "year": 1869,
    "author_name": "Лев Толстой",
    "genre_name": "Роман",
    "cover_image": "https://images.gr-assets.com/books/1462971869l/656.jpg",
    "comments": []
  },
  {
    "id": 21,
    "title": "Гарри Поттер и философский камень",
    "description": "Волшебное путешествие...",
    "year": 1997,
    "author_name": "Джоан Роулинг",
    "genre_name": "Фантастика",
    "cover_image": "https://images.gr-assets.com/books/1474154022l/3.jpg",
    "comments": [
      {
        "id": 1,
        "comment_text": "Очень хорошая книга!",
        "user_id": 5,
        "created_at": "2025-12-16T10:30:00"
      }
    ]
  }
]
```

## 5. Галерея книг

### реструктура HTML

```html
<div class="books-gallery">
    {% for book in books %}
    <div class="book-item">
        <div class="book-image-container">
            {% if book.cover_image %}
                <img src="{{ book.cover_image }}" 
                     alt="{{ book.title }}" 
                     class="book-image"
                     data-book-id="{{ book.id }}">
            {% else %}
                <div class="book-image book-image-placeholder">
                    <span>📚</span>
                </div>
            {% endif %}
            
            <!-- Оверлей с акциями -->
            <div class="book-overlay">
                <a href="/books/{{ book.id }}" class="btn btn-primary">Не Посмотреть</a>
                <button class="btn btn-secondary" onclick="addToShelf({{ book.id }})">Добавить На Полку</button>
            </div>
        </div>
        
        <div class="book-details">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">{{ book.author_name }}</p>
        </div>
    </div>
    {% endfor %}
</div>

<style>
    .books-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 20px;
        padding: 20px;
    }
    
    .book-item {
        cursor: pointer;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .book-image-container {
        position: relative;
        width: 100%;
        padding-bottom: 133.33%;
        overflow: hidden;
        background-color: #f0f0f0;
    }
    
    .book-image,
    .book-image-placeholder {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
    }
    
    .book-image-placeholder {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .book-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .book-item:hover .book-overlay {
        opacity: 1;
    }
    
    .book-details {
        padding: 12px;
    }
</style>
```

## 6. Оптимизация ак и Кэширование

### Нискотые картинки

```html
<!-- Ленивая загрузка -->
<img src="{{ book.cover_image }}" 
     alt="{{ book.title }}" 
     loading="lazy"
     width="200"
     height="300">
```

### Кэширование через CDN

```python
import requests
from functools import lru_cache

@lru_cache(maxsize=128)
def get_book_with_cover(book_id: int):
    """
    Получить книгу с кэшированием
    """
    # Получение из БД
    book = db.query(BooksModel).filter(BooksModel.id == book_id).first()
    return book
```

---

🌟 Андроид усть можно играть с CSS и JavaScript для составния интересных интерфейсов! 📚✨
