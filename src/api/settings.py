from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class DbSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int


class EnvSettings(BaseSettings):
    PROJECT_NAME: str
    IS_TEST: bool

    # caddy proxy settings
    EXT_ENDPOINT1: str
    LOCAL_1: str
    LOCAL_2: str

    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # CryptContext
    SCHEMES: list[str] = ["bcrypt"]
    DEPRECATED: str = "auto"

    # token route
    TOKEN_URL: str = "/api/auth/login"


class EmailSettings(BaseSettings):
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_PORT: int
    EMAIL_SERVER: str


load_dotenv()
db = DbSettings()  # type: ignore
auth = AuthSettings()  # type: ignore
env = EnvSettings()  # type: ignore
email = EmailSettings()  # type: ignore
