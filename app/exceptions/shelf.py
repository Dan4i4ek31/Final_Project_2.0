from fastapi import HTTPException, status


class ShelfEntryNotFoundException(HTTPException):
    def __init__(self, shelf_id: int = None, user_id: int = None, book_id: int = None):
        if shelf_id is not None:
            detail = f"Shelf entry with id {shelf_id} not found"
        elif user_id is not None and book_id is not None:
            detail = f"Shelf entry for user {user_id} and book {book_id} not found"
        else:
            detail = "Shelf entry not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class BookAlreadyInShelfException(HTTPException):
    def __init__(self, user_id: int, book_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book {book_id} is already in shelf for user {user_id}"
        )


class ShelfLimitExceededException(HTTPException):
    def __init__(self, max_books: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shelf limit exceeded. Maximum {max_books} books allowed"
        )


class BookNotInShelfException(HTTPException):
    def __init__(self, user_id: int, book_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book {book_id} is not in shelf for user {user_id}"
        )