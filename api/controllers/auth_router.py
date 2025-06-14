# api/controllers/auth_router.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi_limiter.depends import RateLimiter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.depends import get_user_repo
from datetime import timedelta
from api.models.user import UserCreate
from api.security.jwt_utils import create_jwt_token
from api.services.auth_service import authenticate_user, create_access_token
from api.repositories.user_repository import UserRepository
from passlib.context import CryptContext
import asyncpg
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates")


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
    
    token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=30),
    )

    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=1800,
    )
    return response

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
