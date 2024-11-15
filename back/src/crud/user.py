from sqlalchemy.orm import undefer_group
from core.db import Session
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count
from dataclasses import dataclass
from typing import Optional, Dict, Any
from models.user import User, UserInfo


@dataclass
class UserCredentials:
    username: str
    email: str
    password: str


def get_user_by_email_or_username(login: str,
                                  db: Session) -> Optional[User]:
    user: User | None = (db.query(User).options(undefer_group("sensitive"))
                         .filter(or_(User.email == login.lower(),
                                     User.username == login))
                         .first())
    return user


def is_user_email_unique(email: str,
                         db: Session) -> bool:
    stmt = select(User.email).where(User.email == email)
    res = db.execute(stmt)
    return True if res.scalar_one_or_none() is None else False


def user_credentials_are_unique(email: str,
                                username: str,
                                db: Session) -> bool:
    stmt = select(User.email).where(or_(User.username == email.lower(),
                                        User.email == username))
    res = db.execute(stmt)
    return True if res.scalar_one_or_none() is None else False


def create_user(username: str,
                email: str,
                name: str,
                surname: str,
                is_admin: bool,
                password: str,
                db: Session,
                patronymic: str = None) -> UserCredentials:
    user = User(username=username,
                email=email,
                password=password,
                is_admin=is_admin)
    db.add(user)
    db.flush()
    user_info = UserInfo(user_id=user.id,
                         surname=surname,
                         name=name,
                         patronymic=patronymic)
    db.add(user_info)
    db.commit()
    return UserCredentials(username=username,
                           email=email,
                           password=password)


def count_users_in_system(db: Session) -> int:
    stmt = select(count()).select_from(User)
    res = db.execute(stmt)
    return res.scalar_one()


def update_users_password(user_id: int,
                          password: str,
                          db: Session) -> None:
    stmt = (update(User).where(User.id == user_id)
            .values(password=password))
    db.execute(stmt)
    db.commit()


def get_user_by_id(user_id: int,
                   db: Session) -> User | None:
    stmt = (select(User).where(User.id == user_id)
            .options(selectinload(User.user_info)))
    res = db.execute(stmt)
    return res.scalar_one_or_none()


def select_user_info_update_params(name: Optional[str],
                                   surname: Optional[str],
                                   patronymic: Optional[str],
                                   phone: Optional[str],
                                   position: Optional[str]) -> Dict[str, Any]:
    results = {}
    if name is not None:
        results['name'] = name
    if surname is not None:
        results['surname'] = surname
    if patronymic is not None:
        results['patronymic'] = patronymic
    if phone is not None:
        results['phone'] = phone
    if position is not None:
        results['position'] = position
    return results


def update_user_info(user_id: int,
                     name: Optional[str],
                     surname: Optional[str],
                     patronymic: Optional[str],
                     phone: Optional[str],
                     email: Optional[str],
                     position: Optional[str],
                     db: Session) -> None:
    update_user_info_data = select_user_info_update_params(name=name,
                                                           surname=surname,
                                                           patronymic=patronymic,
                                                           phone=phone,
                                                           position=position)
    if update_user_info_data:
        stmt = (update(UserInfo).where(UserInfo.user_id == user_id)
                .values(**update_user_info_data))
        db.execute(stmt)
        db.commit()
    if email is not None:
        stmt = (update(User).where(User.id == user_id)
                .values(email=email))
        db.execute(stmt)
        db.commit()
