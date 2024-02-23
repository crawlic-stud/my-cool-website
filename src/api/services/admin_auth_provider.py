from datetime import timedelta
import logging
from typing import Optional, Sequence
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import (
    AdminUser,
    AuthProvider,
    RequestResponseEndpoint,
    BaseHTTPMiddleware,
    Middleware,
    ASGIApp,
)
from starlette_admin.exceptions import LoginFailed
from starlette_admin.base import BaseAdmin
from jose import JWTError, jwt

from . import auth_service
import exceptions
from database import users
from database.crud import async_session
import settings


logger = logging.getLogger("admin_auth")


class UsernameAndPasswordProvider(AuthProvider):
    def __init__(
        self,
        login_path: str = "/login",
        logout_path: str = "/logout",
        allow_paths: Sequence[str] | None = None,
    ) -> None:
        super().__init__(login_path, logout_path, allow_paths)
        self.admin_prefix = ""

    def get_middleware(self, admin: "BaseAdmin") -> Middleware:
        """
        This method returns the authentication middleware required for the admin interface
        to enable authentication
        """

        provider: type[self] = admin.auth_provider
        provider.admin_prefix = admin.base_url
        return Middleware(AuthMiddleware, provider=self)

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        try:
            # logger.debug(f"{username=}, {password=}")
            user = await auth_service.authenticate_user(username, password)
            token_expires = timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
            token = auth_service.create_access_token(
                {"sub": user.username}, token_expires
            )
            request.session.update({"token": token, "username": username})
            return response
        except exceptions.Unauthorized as e:
            raise LoginFailed("Invalid username or password") from e

    async def is_authenticated(self, request: Request) -> bool:
        token = request.session.get("token", None)

        if not token:
            return False

        try:
            payload = jwt.decode(
                token, settings.auth.SECRET_KEY, algorithms=[settings.auth.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                return False
        except JWTError:
            return False

        async with async_session() as session:
            user = await users.get_user_by_username(username, session)
        if user is None:
            return False

        return True

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        username = request.session.get("username", "Admin")
        return AdminUser(username=username)
    

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        provider: UsernameAndPasswordProvider,
        allow_paths: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__(app)
        self.provider = provider
        self.allow_paths = list(allow_paths) if allow_paths is not None else []
        self.allow_paths.extend(
            [
                self.provider.login_path,
                "/statics/css/tabler.min.css",
                "/statics/css/fontawesome.min.css",
                "/statics/js/vendor/jquery.min.js",
                "/statics/js/vendor/tabler.min.js",
                "/statics/js/vendor/js.cookie.min.js",
            ]
        )  # Allow static files needed for the login page
        self.allow_paths.extend(
            self.provider.allow_paths if self.provider.allow_paths is not None else []
        )
        self.allow_paths = [self.provider.admin_prefix + p for p in self.allow_paths]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        is_authenticated = await self.provider.is_authenticated(request)
        request_path = request.scope["path"]
        if request_path not in self.allow_paths and not is_authenticated:
            url = "{url}?{query_params}".format(
                url=request.url_for(request.app.state.ROUTE_NAME + ":login"),
                query_params=urlencode({"next": str(request.url)}),
            )
            return RedirectResponse(
                url,
                status_code=303,
            )
        return await call_next(request)
