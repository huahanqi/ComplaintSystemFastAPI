from fastapi import APIRouter
from managers import UserManager
from schemas.request.user import UserLoginIn, UserRegisterIn

router = APIRouter(tags=["Auth"])


@router.post("/register/")
async def register(user_data: UserRegisterIn):
    token = await UserManager.register(user_data.dict())
    return {"token": token}


@router.post("/login/")
async def login(user_data: UserLoginIn):
    token = await UserManager.login(user_data.dict())
    return {"token": token}
