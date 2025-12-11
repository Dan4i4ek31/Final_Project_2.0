from fastapi import FastAPI
import uvicorn
from app.api import (
    roles_router,
    users_router,
    books_router,
    genres_router,
    authors_router,
    book_comments_router,
    shelf_router
)

app = FastAPI(
    title="Library Management API",
    description="API для управления библиотекой книг",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(books_router)
app.include_router(genres_router)
app.include_router(authors_router)
app.include_router(book_comments_router)
app.include_router(shelf_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Library Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)