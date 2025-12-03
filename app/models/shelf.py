from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.books import BooksModel

class ShelfModel(Base):
    __tablename__ = "Shelf"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), nullable=False)
    book:Mapped["BooksModel"] = relationship(back_populates="shelf")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user:Mapped["UserModel"] = relationship(back_populates="shelf")
    status_read: Mapped[bool] = mapped_column(Boolean, default=False)