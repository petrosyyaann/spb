import json
import re
import uuid
import jwt
import core.errors as errors
from typing import Dict, Any, Tuple
from fastapi import Request, Response, Cookie, Depends
from datetime import datetime, timedelta, timezone
from models.user import User, UserSession
from schemas.auth import Refresh
from core.db import Session, get_database
from crud.auth import create_session, get_session_by_id, delete_session, update_session
from settings import settings

agent_parse = re.compile(r"^([\w]*)\/([\d\.]*)\s*(\((.*?)\)\s*(.*))?$")


def set_cookie(access: str, response: Response, max_age: int):
    response.set_cookie("access", access, httponly=True, samesite="lax", max_age=max_age)


def get_user_agent_info(request: Request):
    ip = request.client[0]
    user_agent = request.headers.get("user-agent")
    if "X-Forwarded-For" in request.headers:
        info = [request.headers["X-Forwarded-For"]]
    elif "Forwarded" in request.headers:
        info = [request.headers["Forwarded"]]
    else:
        info = [ip]
    match = agent_parse.fullmatch(user_agent)
    if match:
        info += list(match.groups())
    return "".join(json.dumps(info, ensure_ascii=False, separators=(",", ":")))


def create_user_token_payloads(session: int,
                               identity: str,
                               invalid_after: datetime,
                               now: datetime) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    access_payload = {
        "role": "access",
        "session": session,
        "identity": identity,
        "type": "user",
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE)
    }
    refresh_payload = {
        "role": "refresh",
        "session": session,
        "identity": identity,
        "type": "user",
        "exp": invalid_after
    }

    return access_payload, refresh_payload


def encode_token(payload) -> str:
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def decode_token(token: str, token_type: str, suppress: bool = False) -> Dict[str, Any]:
    try:
        data = jwt.decode(token,
                          settings.JWT_SECRET,
                          algorithms=['HS256'],
                          options={"require": ["exp", "role", "session", "type", "identity"]})
        if data["role"] != token_type:
            raise errors.token_validation_failed()
        return data
    except jwt.ExpiredSignatureError:
        if suppress:
            data = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'],
                              options={"verify_signature": False})
            if data["role"] != token_type:
                raise errors.token_validation_failed()
            return data
        raise errors.token_expired()
    except jwt.DecodeError:
        raise errors.token_validation_failed()


def init_user_tokens(user: User,
                     request: Request,
                     response: Response,
                     db: Session) -> str:
    now = datetime.now(timezone.utc)
    session: UserSession = create_session(user.id,
                                          fingerprint=get_user_agent_info(request),
                                          identity=f"{uuid.uuid1(int(now.timestamp()))}",
                                          invalid_after=now + timedelta(hours=settings.JWT_REFRESH_EXPIRE),
                                          db=db)

    access_payload, refresh_payload = create_user_token_payloads(session.id,
                                                                 session.identity,
                                                                 session.invalid_after,
                                                                 now)
    access = encode_token(access_payload)
    refresh = encode_token(refresh_payload)

    set_cookie(access, response, settings.JWT_REFRESH_EXPIRE * 3600)
    return refresh


def check_session(session_id: int,
                  db: Session,
                  request: Request,
                  identity: str) -> UserSession:
    session: UserSession = get_session_by_id(session_id, db)
    if session is None:
        raise errors.unauthorized()
    if session.fingerprint != get_user_agent_info(request) or session.identity != identity:
        delete_session(session, db)
        raise errors.unauthorized()

    return session


def verify_user_access(access: str,
                       request: Request,
                       db: Session) -> UserSession:
    access_payload = decode_token(access, "access")
    session = check_session(access_payload["session"],
                            db,
                            request,
                            access_payload["identity"])

    return session


def refresh_user_tokens(access: str,
                        refresh: str,
                        request: Request,
                        response: Response,
                        db: Session) -> str:
    access_payload = decode_token(access, "access", suppress=True)
    refresh_payload = decode_token(refresh, "refresh")
    if access_payload["identity"] != refresh_payload["identity"]:
        raise errors.token_validation_failed()

    session: UserSession = get_session_by_id(access_payload["session"], db)
    if session is None:
        raise errors.unauthorized()
    if session.fingerprint != get_user_agent_info(request) or session.identity != access_payload["identity"]:
        delete_session(session, db)
        raise errors.unauthorized()

    now = datetime.now(timezone.utc)
    identity = f"{uuid.uuid1(int(now.timestamp()))}"
    invalid_after = now + timedelta(hours=settings.JWT_REFRESH_EXPIRE)
    update_session(session.id,
                   identity,
                   invalid_after,
                   db)

    access_payload, refresh_payload = create_user_token_payloads(session.id,
                                                                 identity,
                                                                 invalid_after,
                                                                 now)
    access = encode_token(access_payload)
    refresh = encode_token(refresh_payload)

    set_cookie(access, response, settings.JWT_REFRESH_EXPIRE * 3600)
    return refresh


async def get_user_session(request: Request,
                           access: str = Cookie(None),
                           db: Session = Depends(get_database)) -> UserSession:
    session = verify_user_access(access, request, db)
    return session


async def get_user(session: UserSession = Depends(get_user_session)) -> User:
    return session.user