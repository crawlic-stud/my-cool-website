from fastapi import BackgroundTasks, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.token import Token
from schemas.responses import Status
from schemas.user_schema import UserOut
from schemas.http_error import HTTPError
from schemas.reset_password_schema import ResetPassword, SendEmailCode
from services import auth_service
from database import users, crud
from utils import docs
import exceptions


router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/login",
    description=docs.create("Входит по логину и паролю или возвращает новый токен"),
    responses={
        **HTTPError.get_docs(status.HTTP_401_UNAUTHORIZED),
        **HTTPError.get_docs(status.HTTP_500_INTERNAL_SERVER_ERROR),
    },
)
async def login(user_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    token = await auth_service.process_token(user_data)
    if not token:
        raise exceptions.InternalServerError(detail="Invalid user data")
    return token


@router.post(
    "/register",
    description=docs.create("Регистрирует нового пользователя"),
    responses={**HTTPError.get_docs(status.HTTP_409_CONFLICT)},
)
async def register(
    user_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(crud.get_async_session),
) -> UserOut:
    return await users.create_user_if_not_exists(
        user_data.username, auth_service.get_password_hash(user_data.password), session
    )


@router.post(
    "/password/reset",
    description=docs.create(
        "Меняет пароль пользователя на новый",
        notes=[
            "Меняет только при условии что отправленный в ```body``` код верный и его срок действия не истек",
            "Если пользователь не существует - возвращается ошибка",
        ],
    ),
    responses={
        **HTTPError.get_docs(status.HTTP_400_BAD_REQUEST),
        **HTTPError.get_docs(status.HTTP_404_NOT_FOUND),
    },
)
async def reset_password(
    body: ResetPassword,
    session: AsyncSession = Depends(crud.get_async_session),
) -> Status:
    # don't need to check result, because if code is wrong it returns error
    _ = await auth_service.verify_reset_password_code(body.username, body.code, session)
    await users.update_user_password(
        body.username, auth_service.get_password_hash(body.new_password), session
    )
    return Status(status=True, detail="User password updated successfully")


@router.post(
    "/password/send_code",
    description=docs.create("Отправляет код на почту пользователя"),
    responses={**HTTPError.get_docs(status.HTTP_404_NOT_FOUND)},
)
async def send_reset_password_code(
    body: SendEmailCode,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(crud.get_async_session),
):
    return await auth_service.create_reset_password_code(
        str(body.username), session, bg_tasks
    )
