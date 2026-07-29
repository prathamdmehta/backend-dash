class AppException(Exception):
    """
    Base class for every application-level error. Routes and services
    raise these instead of FastAPI's HTTPException directly, so every
    error in the app goes through one consistent response shape
    (see app/main.py's exception handler).
    """

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, detail: str, error_code: str | None = None):
        self.detail = detail
        if error_code:
            self.error_code = error_code
        super().__init__(detail)


class NotFoundException(AppException):
    status_code = 404
    error_code = "not_found"


class UnauthorizedException(AppException):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenException(AppException):
    status_code = 403
    error_code = "forbidden"


class ConflictException(AppException):
    status_code = 409
    error_code = "conflict"


class BadRequestException(AppException):
    status_code = 400
    error_code = "bad_request"
