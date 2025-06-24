# api/controllers/journal_router.py

import os
import logging
import redis
import requests
import json
from pathlib import Path
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from api.depends import get_current_user_from_cookie
from api.repositories.postgres_repository import PostgresDB
from api.services import EntryService
from api.models.entry import EntryCreate, EntryUpdate

router = APIRouter()



async def get_entry_service() -> AsyncGenerator[EntryService, None]:
    async with PostgresDB() as db:
        yield EntryService(db)



BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"


templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/journal", response_class=HTMLResponse)
async def journal_page(request: Request, current_user: str = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse("journal.html", {"request": request, "user": current_user})

@router.post("/entries/", dependencies=[Depends(RateLimiter(times=50, seconds=10))])
async def create_entry(
    request: Request,
    entry: EntryCreate,
    entry_service: EntryService = Depends(get_entry_service)
):    
    try:
        await entry_service.create_entry(entry.model_dump())
    except HTTPException as e:
        if e.status_code == 409:
            raise HTTPException(
                status_code=409, detail="You already have an entry for today."
            )
        raise e

    return JSONResponse(content={"detail": "Entry created successfully"}, status_code=201)


@router.get("/entries", dependencies=[Depends(RateLimiter(times=10, seconds=10))])
@cache(expire=1)
async def get_all_entries(request: Request):
    logging.info(f"Fetching entries")
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.get_entries()
    return result

@router.get("/entries/{entry_id}", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
@cache(expire=10)
async def get_entry(request: Request, entry_id: str):
    logging.info(f"Fetching entry {entry_id}")
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.get_entry(entry_id)
        if not result:
            raise HTTPException(status_code=404, detail="Entry not found")
        return result

@router.patch("/entries/{entry_id}", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def update_entry(
    request: Request,
    entry_id: str,
    entry_update: EntryUpdate
):
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.update_entry(entry_id, entry_update.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return result

@router.delete("/entries/{entry_id}", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def delete_entry(request: Request, entry_id: str):
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.delete_entry(entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"detail": "Entry deleted"}

@router.delete("/entries", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def delete_all_entries(request: Request):
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        await entry_service.delete_all_entries()
    return {"detail": "All entries deleted"}



