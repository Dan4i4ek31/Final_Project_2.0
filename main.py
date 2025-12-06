import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.shelf import router as shelf_router
from app.api.books import router as books_router
from app.api.books_comments import router as books_comments_router
from app.api.gengres import router as gengres_router
from app.api.authors import router as authors_router

app = FastAPI(title="individual_project_template", version="0.0.1")

# Настройка статических файлов
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Подключаем API роутеры
app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(shelf_router)
app.include_router(books_router)
app.include_router(books_comments_router)
app.include_router(gengres_router)
app.include_router(authors_router)

# HTML страницы
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)