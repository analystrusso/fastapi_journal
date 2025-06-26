# api/controllers/auth_router.py

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi_limiter.depends import RateLimiter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from api.depends import get_user_repo
from datetime import timedelta
from api.models.user import UserCreate
from api.security.jwt_utils import create_access_token, SECRET_KEY, ALGORITHM
from api.services.auth_service import authenticate_user
from api.repositories.user_repository import UserRepository
from passlib.context import CryptContext
from jose import jwt, JWTError
import os

# Use redis-py (merged aioredis)
from redis.asyncio import Redis

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = Redis.from_url(REDIS_URL)

@router.post("/register", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def register_user(
    user: UserCreate,
    repo: UserRepository = Depends(get_user_repo),
):
    existing_user = await repo.get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    await repo.create_user(user.username, user.password)
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: UserRepository = Depends(get_user_repo),
):
    user = await authenticate_user(repo, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token, jti = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=30),
    )

    await redis.setex(f"jti:{jti}", 1800, "valid")  # 30 minutes

    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        max_age=1800,
    )
    return response

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/logout")
async def logout(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti")
            if jti:
                await redis.delete(f"jti:{jti}")
        except JWTError:
            pass  # Invalid token, ignore

    response = JSONResponse({"message": "Logout successful"})
    response.delete_cookie("access_token")
    return response
