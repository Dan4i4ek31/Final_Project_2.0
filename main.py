import uvicorn
from fastapi import FastAPI
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.shelf import router as shelf_router
from app.api.books import router as books_router
from app.api.books_comments import router as books_comments_router
from app.api.gengres import router as gengres_router
from app.api.authors import router as authors_router

app = FastAPI(title="individual_project_template", version="0.0.1")

app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(shelf_router)
app.include_router(books_router)
app.include_router(books_comments_router)
app.include_router(gengres_router)
app.include_router(authors_router)


if __name__ == "__main__":
    uvicorn.run(app=app)
