import api.config
from fastapi import FastAPI, Request, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from api.depends import get_current_user_from_cookie, require_admin
from dotenv import load_dotenv
import logging
import fastapi_cache.decorator as fcd
import os
import asyncpg
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from api.controllers.journal_router import router as journal_router
from api.controllers.auth_router import router as auth_router
from api.repositories.user_repository import UserRepository
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
fcd.logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")
    
    app.state.db_pool = await asyncpg.create_pool(database_url)
    app.state.user_repo = UserRepository(app.state.db_pool)
    logging.info("Database pool created")

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    FastAPICache.init(
        RedisBackend(redis), 
        prefix="fastapi-cache", 
        )
    
    await FastAPILimiter.init(redis)
    logging.info("Redis connection established")


    yield
    
    
    await app.state.db_pool.close()
    logging.info("Database pool closed")

    await redis.close()
    logging.info("Redis connection closed")

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/docs", include_in_schema=False)
async def protected_docs(user=Depends(require_admin)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Protected Docs")

@app.get("/openapi.json", include_in_schema=False)
async def protected_openapi(user=Depends(require_admin)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)

app.include_router(journal_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )
