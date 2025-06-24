from fastapi import Depends, Request, Cookie
from api.repositories.user_repository import UserRepository
from fastapi import Request, HTTPException, status, Depends
from api.security.jwt_utils import decode_jwt_token  # your decode function
from jose import JWTError
import asyncpg




def get_db_pool(request: Request) -> asyncpg.Pool:
    pool = request.app.state.db_pool
    if pool is None:
        raise RuntimeError("Database pool is not initialized")
    return pool


def get_user_repo(request: Request) -> UserRepository:
    repo = request.app.state.user_repo
    if not isinstance(repo, UserRepository):
        raise RuntimeError("User repository is not initialized")
    return repo

async def get_current_user_from_cookie(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    payload = decode_jwt_token(access_token)

    username = payload.get("sub")
    role = payload.get("role")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return {"username": username, "role": role}


async def require_admin(user=Depends(get_current_user_from_cookie)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
