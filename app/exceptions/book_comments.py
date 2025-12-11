from fastapi import HTTPException, status


class CommentNotFoundException(HTTPException):
    def __init__(self, comment_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found"
        )


class CommentTooLongException(HTTPException):
    def __init__(self, max_length: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comment exceeds maximum length of {max_length} characters"
        )


class CommentEditNotAllowedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to edit this comment"
        )


class CommentDeleteNotAllowedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this comment"
        )