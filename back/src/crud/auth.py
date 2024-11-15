from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import Union
from models.user import UserSession
from core.db import Session


def create_session(user_id: int,
                   fingerprint: str,
                   identity: str,
                   invalid_after: datetime,
                   db: Session) -> UserSession:
    session = UserSession(user_id=user_id,
                          fingerprint=fingerprint,
                          identity=identity,
                          invalid_after=invalid_after)
    db.add(session)
    db.commit()
    return session


def get_session_by_id(session_id: int,
                      db: Session) -> Union[UserSession, None]:
    stmt = (select(UserSession).where(UserSession.id == session_id)
            .options(selectinload(UserSession.user)))
    res = db.execute(stmt)
    return res.scalar_one_or_none()


def delete_session(session: UserSession,
                   db: Session) -> None:
    db.delete(session)
    db.commit()


def update_session(session_id: int,
                   identity: str,
                   invalid_after: datetime,
                   db: Session) -> None:
    stmt = (update(UserSession)
            .where(UserSession.id == session_id)
            .values(identity=identity,
                    invalid_after=invalid_after))
    res = db.execute(stmt)
    db.commit()
    res.close()
