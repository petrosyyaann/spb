from fastapi import APIRouter
from routers.v1.auth import router as auth_router
from routers.v1.user import router as user_router
from routers.v1.upload import router as upload_router
from routers.v1.sprint import router as sprint_router


router = APIRouter(prefix="/v1")
router.include_router(auth_router, prefix="/auth", tags=["Auth"])

router.include_router(user_router, prefix="/user", tags=["User"])
router.include_router(upload_router, prefix="/upload", tags=["Upload"])
router.include_router(sprint_router, prefix="/sprint", tags=["Sprint"])
