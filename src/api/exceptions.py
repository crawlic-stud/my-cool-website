from fastapi import HTTPException, status


class BadRequest(HTTPException):
    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class Unauthorized(HTTPException):
    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class Forbidden(HTTPException):
    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotFound(HTTPException):
    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class Conflict(HTTPException):
    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, headers)


class InternalServerError(HTTPException):
    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)
