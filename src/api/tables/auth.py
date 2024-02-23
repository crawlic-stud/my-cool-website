from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, types


class ResetPasswordCode(SQLModel, table=True):
    __tablename__ = "reset_password_codes"

    username: str = Field(primary_key=True, foreign_key="users.username")
    expires: datetime = Field(sa_column=Column(type_=types.TIMESTAMP(timezone=True)))
    hashed_code: str
    