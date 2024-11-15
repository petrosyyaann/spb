from fastapi import APIRouter, Depends, Request, Response, Body, Cookie, status

import core.errors as errors
from core.auth import get_user_session, init_user_tokens, refresh_user_tokens
from core.db import Session, get_database
from models.user import User
from schemas.auth import Refresh, AccountCredentials, SignUpCredentials
from crud.user import get_user_by_email_or_username, create_user, user_credentials_are_unique
from settings import settings

router = APIRouter()


@router.post("/login",
             response_model=Refresh,
             responses=errors.with_errors(errors.invalid_credentials()))
async def login(request: Request,
                response: Response,
                credentials: AccountCredentials,
                db: Session = Depends(get_database)) -> Refresh:
    user = get_user_by_email_or_username(login=credentials.login,
                                         db=db)
    if user is None:
        raise errors.invalid_credentials()
    if not user.verify_password(credentials.password):
        raise errors.invalid_credentials()

    refresh = init_user_tokens(user,
                               request=request,
                               response=response,
                               db=db)
    return Refresh(refresh=refresh)


@router.post("/refresh",
             response_model=Refresh,
             responses=errors.with_errors(errors.unauthorized(),
                                          errors.token_expired(),
                                          errors.token_validation_failed()))
async def refresh_token(request: Request,
                        response: Response,
                        access: str = Cookie(None),
                        params: Refresh = Body(),
                        db: Session = Depends(get_database)) -> Refresh:
    refresh = refresh_user_tokens(access=access,
                                  refresh=params.refresh,
                                  request=request,
                                  response=response,
                                  db=db)
    return Refresh(refresh=refresh)


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT,
               responses=errors.with_errors(errors.unauthorized(),
                                            errors.token_expired(),
                                            errors.token_validation_failed()))
async def logout_user(response: Response,
                      session=Depends(get_user_session),
                      db: Session = Depends(get_database)):
    response.delete_cookie(key="access")
    db.delete(session)
    db.commit()


@router.post("/signup",
             status_code=201,
             responses=errors.with_errors(errors.password_too_weak(),
                                          errors.auth_data_is_not_unique()))
async def sign_up(credentials: SignUpCredentials,
                  db: Session = Depends(get_database)):
    if len(credentials.password) < settings.MINIMAL_PASSWORD_LENGTH:
        raise errors.password_too_weak()
    if not user_credentials_are_unique(credentials.email, credentials.username, db):
        raise errors.auth_data_is_not_unique()
    create_user(username=credentials.username,
                email=credentials.email,
                name=credentials.name,
                surname=credentials.surname,
                patronymic=credentials.patronymic,
                is_admin=True,
                password=credentials.password,
                db=db)
