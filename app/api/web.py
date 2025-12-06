from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/web", tags=["Фронтенд"])

@router.get("/", response_class=HTMLResponse)
async def get_index_html(request: Request):
    """Простая страница с редиректом на главный веб-интерфейс"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/" />
    </head>
    <body>
        <p>Перенаправление на <a href="/">главную страницу</a>...</p>
    </body>
    </html>
    """