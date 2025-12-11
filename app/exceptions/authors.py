from fastapi import HTTPException, status


class AuthorNotFoundException(HTTPException):
    def __init__(self, author_id: int = None, author_name: str = None):
        if author_id is not None:
            detail = f"Author with id {author_id} not found"
        elif author_name is not None:
            detail = f"Author '{author_name}' not found"
        else:
            detail = "Author not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class AuthorAlreadyExistsException(HTTPException):
    def __init__(self, author_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Author '{author_name}' already exists"
        )


class AuthorHasBooksException(HTTPException):
    def __init__(self, author_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete author '{author_name}' because they have books"
        )