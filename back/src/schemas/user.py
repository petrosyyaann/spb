from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserMe(BaseModel):
    id: int
    name: str
    email: str
    username: str
    surname: str
    name: str
    is_admin: bool
    patronymic: Optional[str]
    phone: Optional[str]
    position: Optional[str]
    joined_at: datetime


class UserMeUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    username: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    position: Optional[str]
