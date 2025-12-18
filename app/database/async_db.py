# app/database/async_db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

# Преобразуем DATABASE_URL для async
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foliant.db")

# Если используется SQLite, преобразуем в aiosqlite
if DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Создаем async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Создаем async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency для использования в маршрутах
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
