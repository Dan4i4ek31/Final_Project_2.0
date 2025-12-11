from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.book_comments import BookCommentRepository
from app.schemes.book_comments import BookCommentCreate, BookCommentUpdate
from app.models.book_comments import BookCommentsModel


class BookCommentService:
    def __init__(self, db: Session):
        self.repository = BookCommentRepository(db)

    def get_comment(self, comment_id: int) -> Optional[BookCommentsModel]:
        return self.repository.get(comment_id)

    def get_comments(self, skip: int = 0, limit: int = 100) -> List[BookCommentsModel]:
        return self.repository.get_all(skip, limit)

    def get_comments_by_book(self, book_id: int, skip: int = 0, limit: int = 100) -> List[BookCommentsModel]:
        return self.repository.get_by_book(book_id, skip, limit)

    def get_comments_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BookCommentsModel]:
        return self.repository.get_by_user(user_id, skip, limit)

    def create_comment(self, comment: BookCommentCreate) -> BookCommentsModel:
        return self.repository.create(comment.dict())

    def update_comment(self, comment_id: int, comment: BookCommentUpdate) -> Optional[BookCommentsModel]:
        db_comment = self.repository.get(comment_id)
        if db_comment:
            return self.repository.update(db_comment, comment.dict(exclude_unset=True))
        return None

    def delete_comment(self, comment_id: int) -> Optional[BookCommentsModel]:
        return self.repository.delete(comment_id)