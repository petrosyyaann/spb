from fastapi import APIRouter, Depends
from models.user import User
from core.db import get_database, Session
from core.auth import get_user
from schemas.user import UserMe, UserMeUpdate
import core.errors as errors


router = APIRouter()


@router.get('/me',
            response_model=UserMe,
            responses=errors.with_errors())
async def get_me(user: User = Depends(get_user),
                 db: Session = Depends(get_database)):
    return UserMe(id=user.id,
                  name=user.user_info.name,
                  email=user.email,
                  username=user.username,
                  is_admin=user.is_admin,
                  surname=user.user_info.surname,
                  patronymic=user.user_info.name,
                  phone=user.user_info.phone,
                  position=user.user_info.position,
                  joined_at=user.user_info.joined_at)


@router.patch('/me',
              responses=errors.with_errors())
async def update_my_info(user_info: UserMeUpdate,
                         user: User = Depends(get_user),
                         db: Session = Depends(get_database)) -> UserMe:
    if user is None:
        raise errors.unauthorized()

    if user_info.name is not None:
        user.user_info.name = user_info.name
    if user_info.email is not None:
        user.email = user_info.email
    if user_info.username is not None:
        user.username = user_info.username
    if user_info.surname is not None:
        user.user_info.surname = user_info.surname
    if user_info.patronymic is not None:
        user.user_info.patronymic = user_info.patronymic
    if user_info.phone is not None:
        user.user_info.phone = user_info.phone
    if user_info.position is not None:
        user.user_info.position = user_info.position

    db.commit()
    return UserMe(id=user.id,
                  name=user.user_info.name,
                  email=user.email,
                  username=user.username,
                  surname=user.user_info.surname,
                  patronymic=user.user_info.name,
                  phone=user.user_info.phone,
                  position=user.user_info.position,
                  joined_at=user.user_info.joined_at)
