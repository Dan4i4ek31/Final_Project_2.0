# 🔌 API Endpoints Маппинг

## ПОЛНОЕ соответствие эндпоинтов

| От Фронтенда (app.js) | К Бэкенду (API) | Описание |
|---|---|---|
| `/favorites/user/{user_id}?skip=0&limit=100` | `/shelf/user/{user_id}?skip=0&limit=100` | Получить избранное на полке я пользователя |
| `/products/?skip=0&limit=100&active_only=true` | `/books/?skip=0&limit=100` | Получить все книги |
| `/listings/?skip=0&limit=100&active_only=true` | ⚠️ НЕ существует | Нужна реализация |
| `/author-listings/?skip=0&limit=100&active_only=true` | ⚠️ НЕ существует | Нужна реализация |

## Доступные эндпоинты бэкенда

### Shelf (Favorites)
```
GET     /shelf/
        /shelf/{shelf_id}
        /shelf/user/{user_id}
        /shelf/user/{user_id}/book/{book_id}
        /shelf/user/{user_id}/read
        /shelf/book/{book_id}

POST    /shelf/
PUT     /shelf/{shelf_id}
        /shelf/{shelf_id}/mark-read

DELETE  /shelf/{shelf_id}
        /shelf/user/{user_id}/book/{book_id}
```

### Books
```
GET     /books/
        /books/{book_id}
        /books/author/{author_id}
        /books/genre/{genre_id}

POST    /books/
PUT     /books/{book_id}
DELETE  /books/{book_id}
```

### Authors
```
GET     /authors/
        /authors/{author_id}

POST    /authors/
PUT     /authors/{author_id}
DELETE  /authors/{author_id}
```

### Genres (Gengres)
```
GET     /gengres/
        /gengres/{genre_id}

POST    /gengres/
PUT     /gengres/{genre_id}
DELETE  /gengres/{genre_id}
```

### Users
```
GET     /users/
        /users/{user_id}

POST    /users/
PUT     /users/{user_id}
DELETE  /users/{user_id}
```

### Book Comments
```
GET     /book-comments/
        /book-comments/{comment_id}
        /book-comments/book/{book_id}

POST    /book-comments/
PUT     /book-comments/{comment_id}
DELETE  /book-comments/{comment_id}
```

### Roles
```
GET     /roles/
        /roles/{role_id}
```

## Примеры донастройки app.js

### Где оискивать в app.js (grep patterns):

```bash
# Найти все '/favorites/' вызовы
grep -n "'/favorites/" app/static/js/app.js

# Найти все '/products/' вызовы
grep -n "'/products/" app/static/js/app.js

# Найти все '/listings/' вызовы
grep -n "'/listings/" app/static/js/app.js

# Найти все '/author-listings/' вызовы
grep -n "'/author-listings/" app/static/js/app.js
```

## Потом сделаю: Search and Replace

```javascript
// В IDE (например VS Code):

// Find: /favorites/
// Replace: /shelf/

// Find: /products/
// Replace: /books/

// При делете вызовы /listings/ и /author-listings/
// эти данные нужно или:
// 1. Делетировать использование (эти таблицы не существуют)
// 2. Либо создать эти эндпоинты в бэкенде
```

## Шаги ПОСЛЕ исправления

1. Откройте DevTools (F12) в браузере
2. Понаблюдайте вкладку Network
3. При загрузке страницы должны быть реквесты к:
   - `/shelf/user/1` (должна быть 200 OK)
   - `/books/` (должна быть 200 OK)
4. Если все 404 - что-то иссп НОЕТО

## ✅ Проверочные тесты (curl)

```bash
# Тест избранного
curl http://localhost:8000/shelf/user/1

# Тест книг
curl http://localhost:8000/books/

# Тест статуса
curl http://localhost:8000/health
```
