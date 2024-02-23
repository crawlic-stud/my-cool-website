from sqlmodel import Field

from .base import IntBasicModel, example


class User(IntBasicModel, table=True):
    __tablename__ = "users"  # type: ignore

    username: str = Field(max_length=100, min_length=3, **example("username"), index=True, unique=True)  # type: ignore
    hashed_password: str = Field(**example("hashed_password"))  # type: ignore
