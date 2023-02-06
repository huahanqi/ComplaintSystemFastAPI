from asyncpg import UniqueViolationError
from fastapi import HTTPException
from passlib.context import CryptContext
from db import database
from managers.auth import AuthManager
from models import user, RoleType
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserManager:
    @staticmethod
    async def register(user_data):
        data = user_data
        data["password"] = pwd_context.hash(data["password"])
        q = user.insert().values(**data)
        try:
            id_ = await database.execute(q)
        except UniqueViolationError:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        user_do = await database.fetch_one(user.select().where(user.c.id == id_))
        return AuthManager.encode_token(user_do)

    @staticmethod
    async def login(user_data):
        user_do = await database.fetch_one(user.select().where(user.c.email == user_data["email"]))
        if not user_do:
            raise HTTPException(status_code=400, detail="Wrong email or password")
        elif not pwd_context.verify(user_data["password"], user_do["password"]):
            raise HTTPException(status_code=400, detail="Wrong email or password")
        return AuthManager.encode_token(user_do)

    @staticmethod
    async def get_all_users():
        return await database.fetch_all(user.select())

    @staticmethod
    async def get_user_by_email(email):
        return await database.fetch_one(user.select().where(user.c.email == email))

    @staticmethod
    async def change_role(role: RoleType, user_id):
        await database.execute(user.update().where(user.c.id == user_id).values(role=role))

