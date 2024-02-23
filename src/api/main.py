from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette_admin.contrib.sqlmodel.admin import Admin
from starlette_admin.i18n import I18nConfig
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from alembic.command import upgrade
from alembic.config import Config

from routes import api
from database.crud import engine, async_session
from database import users
from admin import UserView
from tables.user import User
from services import auth_service
from services import admin_auth_provider
import settings


if settings.env.IS_TEST:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not settings.env.IS_TEST:
        upgrade(Config("alembic.ini"), revision="head")
        async with async_session() as session:
            await users.create_superuser(
                settings.env.SUPERUSER_USERNAME,
                auth_service.get_password_hash(settings.env.SUPERUSER_PASSWORD),
                session,
            )
    yield

    logging.info("shutdown FastAPI...")  # shutdown


app = FastAPI(lifespan=lifespan)
app.include_router(api)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = Admin(
    engine,
    title=app.title,
    i18n_config=I18nConfig(default_locale="ru", language_switcher=["ru", "en"]),
    auth_provider=admin_auth_provider.UsernameAndPasswordProvider(
        login_path="/login", logout_path="/logout", allow_paths=[]
    ),
    middlewares=[Middleware(SessionMiddleware, secret_key=settings.auth.SECRET_KEY)],
)
admin.add_view(UserView(User, icon="fa fa-users"))
admin.mount_to(app)


if __name__ == "__main__":
    uvicorn.run(app)  # for debugging
