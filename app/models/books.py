from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.book_comments import Book_commentsModel
    from app.models.gengres import GengresModel
    from app.models.authors import AuthorsModel
    from app.models.shelf import ShelfModel

class BooksModel(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=True)
    discription: Mapped[str] = mapped_column(String(200), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)
    authors: Mapped["AuthorsModel"] = relationship(back_populates="books")
    gengre_id: Mapped[int] = mapped_column(ForeignKey("gengre.id"), nullable=False)
    gengres: Mapped["GengresModel"] = relationship(back_populates="books")
    year: Mapped[int] = mapped_column(nullable=False)
    book_comments:Mapped[list["Book_commentsModel"]] = relationship(back_populates = "books")
    shelf:Mapped[list["ShelfModel"]] = relationship(back_populates = "books")
