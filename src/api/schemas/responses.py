from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class Status(BaseModel):
    status: bool
    detail: str | None = None


class Items(BaseModel, Generic[T]):
    items: list[T]


class PaginatedItems(Items, Generic[T]):
    page_index: int = 0
    page_size: int = 0
    total_pages: int = 0
