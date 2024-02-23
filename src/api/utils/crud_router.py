from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import crud
from ..schemas.responses import PaginatedItems


class CRUDRouter(APIRouter):
    def __init__(
        self,
        model: type[SQLModel],
        prefix: str,
        tags: list[str | Enum] | None = None,
        dependencies: list[Any] | None = None,
        responses: dict[int | str, dict[str, Any]] | None = None,
    ):
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
        )
        self.model = model

    def add_get_all_route(
        self,
        model: type[SQLModel],
        description: str | None = None,
        name: str | None = None,
        **extra_args
    ):
        self.add_api_route(
            "",
            self._get_all(model),
            response_model=PaginatedItems[model],
            status_code=status.HTTP_200_OK,
            methods=["GET"],
            description=description,
            name=name,
            **extra_args
        )
        return self

    def add_get_by_id_route(
        self,
        model: type[SQLModel],
        description: str | None = None,
        name: str | None = None,
        **extra_args
    ):
        self.add_api_route(
            "/{id}",
            self._get_by_id(model),
            response_model=model,
            status_code=status.HTTP_200_OK,
            methods=["GET"],
            description=description,
            name=name,
            **extra_args
        )
        return self

    def add_create_route(
        self,
        model: type[SQLModel],
        description: str | None = None,
        name: str | None = None,
        **extra_args
    ):
        self.add_api_route(
            "",
            self._create(model),
            response_model=model,
            status_code=status.HTTP_200_OK,
            methods=["POST"],
            description=description,
            name=name,
            **extra_args
        )
        return self

    def add_update_route(
        self,
        model: type[SQLModel],
        description: str | None = None,
        name: str | None = None,
        **extra_args
    ):
        self.add_api_route(
            "/{id}",
            self._update(model),
            response_model=model,
            status_code=status.HTTP_200_OK,
            methods=["PATCH"],
            description=description,
            name=name,
            **extra_args
        )
        return self

    def add_delete_by_id_route(
        self,
        model: type[SQLModel],
        description: str | None = None,
        name: str | None = None,
        **extra_args
    ):
        self.add_api_route(
            "/{id}",
            self._delete(model),
            response_model=model,
            status_code=status.HTTP_200_OK,
            methods=["DELETE"],
            description=description,
            name=name,
            **extra_args
        )
        return self

    def _get_all(self, model: type[SQLModel]):
        async def route(
            offset: int = Query(default=0, ge=0),
            limit: int = Query(default=crud.DEFAULT_LIMIT, le=crud.DEFAULT_LIMIT, ge=0),
            session: AsyncSession = Depends(crud.get_async_session),
        ):
            items = await crud.get_all(session, model, offset, limit)
            return PaginatedItems(items=items)

        return route

    def _get_by_id(self, model: type[SQLModel]):
        async def route(
            object_id: int, session: AsyncSession = Depends(crud.get_async_session)
        ):
            return await crud.get_by_id(object_id, session, model)

        return route

    def _create(self, model: type[SQLModel]):
        async def route(
            data: model,
            session: AsyncSession = Depends(crud.get_async_session),
        ):
            return await crud.create(data, session, model)

        return route

    def _delete(self, model: type[SQLModel]):
        async def route(
            object_id: int, session: AsyncSession = Depends(crud.get_async_session)
        ):
            return await crud.delete_by_id(object_id, session, model)

        return route

    def _update(self, model: type[SQLModel]):
        async def route(
            object_id: int,
            data: model,
            session: AsyncSession = Depends(crud.get_async_session),
        ):
            return await crud.update_by_id(object_id, session, data, model)

        return route
