from datetime import datetime, timedelta
from typing import Optional
from decouple import config
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError
from starlette.requests import Request
from db import database
from models import RoleType


class AuthManager:
    @staticmethod
    def encode_token(user):
        try:
            to_encode = {"sub": user["id"], "exp": datetime.utcnow() + timedelta(minutes=120)}
            return jwt.encode(to_encode, config('JWT_SECRET'), algorithm='HS256')
        except Exception as e:
            raise e


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)
        from models import user
        try:
            payload = jwt.decode(res.credentials, config('JWT_SECRET'), algorithms=['HS256'])
            user = await database.fetch_one(user.select().where(user.c.id == payload["sub"]))
            request.state.user = user
            return user
        except ExpiredSignatureError:
            raise HTTPException(401, "Token expired.")
        except InvalidTokenError:
            raise HTTPException(401, "Invalid token.")


oauth2_scheme = CustomHTTPBearer()


def is_complainer(request: Request):
    if not request.state.user["role"] == RoleType.complainer:
        raise HTTPException(status_code=403, detail="Forbidden")


def is_approver(request: Request):
    if not request.state.user["role"] == RoleType.approver:
        raise HTTPException(status_code=403, detail="Forbidden")


def is_admin(request: Request):
    if not request.state.user["role"] == RoleType.admin:
        raise HTTPException(status_code=403, detail="Forbidden")