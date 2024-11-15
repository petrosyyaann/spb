from pydantic import BaseModel, EmailStr
from typing import Optional


class AccountCredentials(BaseModel):
    login: str
    password: str
    remember_me: Optional[bool] = True


class Refresh(BaseModel):
    refresh: str


class SignUpCredentials(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    surname: str
    patronymic: Optional[str]
