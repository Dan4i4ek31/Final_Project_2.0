from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.books import BooksModel

class Book_commentsModel(Base):
    __tablename__ = "book_comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), nullable=False)
    books:Mapped["BooksModel"] = relationship(back_populates="book_comments")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user:Mapped["UserModel"] = relationship(back_populates="book_comments")
    comment_text: Mapped[int] = mapped_column(String(200))
    data: Mapped[int] = mapped_column(nullable=False)
