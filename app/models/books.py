from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from app.models.authors import AuthorsModel
from app.models.book_comments import BookCommentsModel
from app.models.gengres import GengresModel
from app.models.shelf import ShelfModel

class BooksModel(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("gengres.id"), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    
    # Отношения
    author: Mapped["AuthorsModel"] = relationship(back_populates="books", lazy="joined")
    genre: Mapped["GengresModel"] = relationship(back_populates="books", lazy="joined")
    book_comments: Mapped[list["BookCommentsModel"]] = relationship(back_populates="book", lazy="select")
    shelf_entries: Mapped[list["ShelfModel"]] = relationship(back_populates="book", lazy="select")