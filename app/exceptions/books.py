from fastapi import HTTPException, status


class BookNotFoundException(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )


class BookAlreadyExistsException(HTTPException):
    def __init__(self, title: str, author_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book '{title}' by author {author_id} already exists"
        )


class BookHasCommentsException(HTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete book '{book_title}' because it has comments"
        )


class BookInShelfException(HTTPException):
    def __init__(self, book_title: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete book '{book_title}' because it is in user shelves"
        )