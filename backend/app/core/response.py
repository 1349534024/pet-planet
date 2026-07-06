from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: str = "SUCCESS"
    message: str = "success"
    data: Any = None


class PageData(BaseModel):
    items: list[Any]
    page: int
    page_size: int
    total: int


def success(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(message=message, data=data)


def page_response(items: list[Any], page: int, page_size: int, total: int) -> ApiResponse:
    return success(PageData(items=items, page=page, page_size=page_size, total=total).model_dump())
