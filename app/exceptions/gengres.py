from fastapi import HTTPException, status


class GenreNotFoundException(HTTPException):
    def __init__(self, genre_id: int = None, genre_name: str = None):
        if genre_id is not None:
            detail = f"Genre with id {genre_id} not found"
        elif genre_name is not None:
            detail = f"Genre '{genre_name}' not found"
        else:
            detail = "Genre not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class GenreAlreadyExistsException(HTTPException):
    def __init__(self, genre_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Genre '{genre_name}' already exists"
        )


class GenreHasBooksException(HTTPException):
    def __init__(self, genre_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete genre '{genre_name}' because it has associated books"
        )