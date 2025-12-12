import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi import FastAPI, Request
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Library Management API",
    description="API для управления библиотекой книг",
    version="1.0.0"
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

# СОЗДАЕМ ПАПКИ, ЕСЛИ ОНИ НЕ СУЩЕСТВУЮТ
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Монтируем статические файлы по пути /app/static
app.mount("/app/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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