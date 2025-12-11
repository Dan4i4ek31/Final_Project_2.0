from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.book_comments import BookCommentsModel
    from app.models.gengres import GengresModel
    from app.models.authors import AuthorsModel
    from app.models.shelf import ShelfModel

class BooksModel(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    author: Mapped["AuthorsModel"] = relationship(back_populates="books")
    genre_id: Mapped[int] = mapped_column(ForeignKey("gengres.id"), nullable=False)
    genre: Mapped["GengresModel"] = relationship(back_populates="books")
    year: Mapped[int] = mapped_column(nullable=False)
    book_comments: Mapped[list["BookCommentsModel"]] = relationship(back_populates="book")
    shelf_entries: Mapped[list["ShelfModel"]] = relationship(back_populates="book")