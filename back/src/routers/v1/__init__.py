from fastapi import APIRouter
from routers.v1.auth import router as auth_router
from routers.v1.user import router as user_router


router = APIRouter(prefix="/v1")
router.include_router(auth_router, prefix="/auth", tags=["Auth"])

router.include_router(user_router, prefix="/user", tags=["User"])
