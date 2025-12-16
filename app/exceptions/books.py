from fastapi import HTTPException, status


class BookNotFoundException(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )


class BookAlreadyExistsException(HTTPException):
    def __init__(self, title: str, author_id: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Книга '{title}' автора с ID {author_id} уже существует"
        )


class BookHasCommentsException(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить книгу с ID {book_id}, так как к ней есть комментарии"
        )


class BookInShelfException(HTTPException):
    def __init__(self, book_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить книгу с ID {book_id}, так как она находится на полках у пользователей"
        )


class InvalidBookDataException(HTTPException):
    def __init__(self, detail: str = "Неверные данные книги"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )