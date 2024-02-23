import logging
from datetime import datetime, timedelta
from typing import Any, Literal, Optional

from fastapi import BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from tables.user import User
from tables.auth import ResetPasswordCode
from schemas.token import TokenData, Token
import settings
import exceptions
from utils import misc
from database import users, crud as db
from . import email_service


logger = logging.getLogger("auth")

pwd_context = CryptContext(
    schemes=settings.auth.SCHEMES, deprecated=settings.auth.DEPRECATED
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.auth.TOKEN_URL)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str) -> User:
    async with db.async_session() as session:  # type: ignore
        user = await users.get_user_by_username(username, session)
    if not user or not verify_password(password, user.hashed_password):
        raise exceptions.Unauthorized(f"Incorrect username or password")
    return user


def create_access_token(data: dict[str, Any], expires: Optional[timedelta]) -> str:
    to_encode = data.copy()
    if expires:
        expire = datetime.utcnow() + expires
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credential_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW_Authenticate": "Bearer"},
    )
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.auth.SECRET_KEY, algorithms=[settings.auth.ALGORITHM]
        )

        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credential_exc
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exc

    async with db.async_session() as session:  # type: ignore
        user = await users.get_user_by_username(token_data.username, session)
    if user is None:
        raise exceptions.NotFound("User not found")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise exceptions.BadRequest("Inactive user")
    return current_user


async def process_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Optional[Token]:
    user = await authenticate_user(form_data.username, form_data.password)
    token_expires = timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    if user:
        token = create_access_token({"sub": user.username}, token_expires)
        return Token(access_token=token, token_type="bearer")


async def create_reset_password_code(
    username: str, session: AsyncSession, bg_tasks: BackgroundTasks
):
    code = str(misc.random_6_digit_number())
    logger.debug(f"{code=}")
    reset_code = ResetPasswordCode(
        username=username,
        hashed_code=get_password_hash(code),
        expires=misc.utcnow() + timedelta(minutes=30),
    )
    bg_tasks.add_task(email_service.send_confirmation_code_to_user, username, code)
    try:
        return await db.upsert(reset_code, session, ResetPasswordCode, ["username"])
    except IntegrityError as e:
        raise exceptions.NotFound(f"User with username={username} not found") from e


async def verify_reset_password_code(
    username: str, plain_code: str, session: AsyncSession
) -> Literal[True]:
    code: ResetPasswordCode = await db.get_first_where(
        session,
        ResetPasswordCode,
        ResetPasswordCode.username == username,
        error_msg=f"Code for user={username} wasn't set",
    )
    is_correct = verify_password(plain_code, code.hashed_code)
    if not is_correct:
        raise exceptions.BadRequest("Code is incorrect")
    elif code.expires < misc.utcnow():
        raise exceptions.BadRequest("Code expired, consider resending email")
    return True
