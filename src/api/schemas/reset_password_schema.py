from pydantic import BaseModel, EmailStr


class SendEmailCode(BaseModel):
    username: EmailStr


class ResetPassword(BaseModel):
    username: str
    code: str
    new_password: str
