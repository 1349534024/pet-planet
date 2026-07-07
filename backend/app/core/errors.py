from enum import StrEnum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR


class ErrorCode(StrEnum):
    success = "SUCCESS"
    validation_error = "VALIDATION_ERROR"
    unauthorized = "UNAUTHORIZED"
    forbidden = "FORBIDDEN"
    not_found = "NOT_FOUND"
    conflict = "CONFLICT"
    rate_limited = "RATE_LIMITED"
    internal_error = "INTERNAL_ERROR"
    auth_invalid_phone = "AUTH_INVALID_PHONE"
    auth_invalid_code = "AUTH_INVALID_CODE"
    auth_token_expired = "AUTH_TOKEN_EXPIRED"
    auth_invalid_password = "AUTH_INVALID_PASSWORD"
    user_not_found = "USER_NOT_FOUND"
    user_disabled = "USER_DISABLED"
    user_real_name_required = "USER_REAL_NAME_REQUIRED"
    pet_not_found = "PET_NOT_FOUND"
    pet_permission_denied = "PET_PERMISSION_DENIED"
    file_invalid_type = "FILE_INVALID_TYPE"
    file_too_large = "FILE_TOO_LARGE"
    audit_not_found = "AUDIT_NOT_FOUND"
    audit_already_reviewed = "AUDIT_ALREADY_REVIEWED"
    audit_invalid_status = "AUDIT_INVALID_STATUS"
    order_not_found = "ORDER_NOT_FOUND"
    order_status_invalid = "ORDER_STATUS_INVALID"
    payment_callback_invalid = "PAYMENT_CALLBACK_INVALID"


class AppException(Exception):
    def __init__(self, code: ErrorCode, message: str, status_code: int = HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return error_response(exc.code.value, exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(ErrorCode.validation_error.value, str(exc.errors()), HTTP_400_BAD_REQUEST)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return error_response(str(exc.status_code), str(exc.detail), exc.status_code)

    @app.exception_handler(Exception)
    async def handle_unknown_exception(_: Request, exc: Exception) -> JSONResponse:
        return error_response(ErrorCode.internal_error.value, str(exc), HTTP_500_INTERNAL_SERVER_ERROR)
