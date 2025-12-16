from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.authors import AuthorsModel
    from app.models.gengres import GengresModel
    from app.models.shelf import ShelfModel
    from app.models.book_comments import BookCommentsModel


class BooksModel(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Внешние ключи
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("gengres.id"), nullable=False)
    
    # Связи
    author: Mapped["AuthorsModel"] = relationship(back_populates="books")
    genre: Mapped["GengresModel"] = relationship(back_populates="books")
    shelf_entries: Mapped[list["ShelfModel"]] = relationship(back_populates="book")
    book_comments: Mapped[list["BookCommentsModel"]] = relationship(back_populates="book")