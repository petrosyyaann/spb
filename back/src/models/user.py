from passlib.context import CryptContext
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import String, TIMESTAMP, ForeignKey, Boolean, func, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

from models.base import Base

pwd_context = CryptContext(schemes=["sha256_crypt"])


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    __password: Mapped[str] = mapped_column("password", String, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default="False")

    user_info: Mapped[List["UserInfo"]] = relationship(back_populates="user", uselist=False, passive_deletes=True)
    sessions: Mapped["UserSession"] = relationship(back_populates="user", uselist=True, passive_deletes=True)

    @hybrid_property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = pwd_context.hash(password)

    @hybrid_method
    def verify_password(self, password):
        return pwd_context.verify(password, self.__password)


class UserSession(Base):
    __tablename__ = "user_session"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete='CASCADE'),
                                         nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(nullable=False)
    invalid_after: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    identity: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions", passive_deletes=True, uselist=False)


class UserInfo(Base):
    __tablename__ = "user_info"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete='CASCADE'), primary_key=True)
    surname: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    patronymic: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(String(16), nullable=True)
    position: Mapped[str] = mapped_column(String(128), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                server_default=func.current_timestamp())

    user: Mapped["User"] = relationship(back_populates="user_info", uselist=False, passive_deletes=True)
