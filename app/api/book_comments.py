from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemes.book_comments import BookComment, BookCommentCreate, BookCommentUpdate
from app.services.book_comments import BookCommentService
from app.exceptions.book_comments import (
    CommentNotFoundException,
    CommentTooLongException,
    CommentEditNotAllowedException,
    CommentDeleteNotAllowedException
)

router = APIRouter(prefix="/book-comments", tags=["book-comments"])


@router.get("/", response_model=List[BookComment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookCommentService(db)
    return service.get_comments(skip, limit)


@router.get("/{comment_id}", response_model=BookComment)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    service = BookCommentService(db)
    comment = service.get_comment(comment_id)
    if comment is None:
        raise CommentNotFoundException(comment_id=comment_id)
    return comment


@router.get("/by-book/{book_id}", response_model=List[BookComment])
def read_comments_by_book(book_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookCommentService(db)
    return service.get_comments_by_book(book_id, skip, limit)


@router.get("/by-user/{user_id}", response_model=List[BookComment])
def read_comments_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = BookCommentService(db)
    return service.get_comments_by_user(user_id, skip, limit)


@router.post("/", response_model=BookComment)
def create_comment(comment: BookCommentCreate, db: Session = Depends(get_db)):
    # Проверяем длину комментария
    if len(comment.comment_text) > 200:
        raise CommentTooLongException(max_length=200)
    
    service = BookCommentService(db)
    return service.create_comment(comment)


@router.put("/{comment_id}", response_model=BookComment)
def update_comment(comment_id: int, comment: BookCommentUpdate, db: Session = Depends(get_db)):
    service = BookCommentService(db)
    
    # Проверяем существование комментария
    db_comment = service.get_comment(comment_id)
    if db_comment is None:
        raise CommentNotFoundException(comment_id=comment_id)
    
    # Здесь можно добавить проверку прав на редактирование
    # Например, разрешить редактировать только автору комментария
    # if db_comment.user_id != current_user.id:
    #     raise CommentEditNotAllowedException()
    
    # Проверяем длину комментария, если текст обновляется
    if comment.comment_text and len(comment.comment_text) > 200:
        raise CommentTooLongException(max_length=200)
    
    updated_comment = service.update_comment(comment_id, comment)
    return updated_comment


@router.delete("/{comment_id}", response_model=BookComment)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    service = BookCommentService(db)
    db_comment = service.get_comment(comment_id)
    if db_comment is None:
        raise CommentNotFoundException(comment_id=comment_id)
    
    # Здесь можно добавить проверку прав на удаление
    # Например, разрешить удалять только автору комментария или администратору
    # if db_comment.user_id != current_user.id and not current_user.is_admin:
    #     raise CommentDeleteNotAllowedException()
    
    deleted_comment = service.delete_comment(comment_id)
    return deleted_comment