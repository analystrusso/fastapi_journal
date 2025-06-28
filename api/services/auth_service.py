from datetime import datetime, timedelta
from typing import Optional
from api.models.user import User
from api.security.jwt_utils import create_jwt_token
from passlib.context import CryptContext
from api.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def authenticate_user(repo: UserRepository, username: str, password: str) -> Optional[dict]:
    users = await repo.get_user(username)
    if not users:
        return None
    for user in users:  # Assuming get_user returns a list of users
        if user["username"] == username and pwd_context.verify(password, user["hashed_password"]):
            return user
    return None


def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return create_jwt_token(to_encode)