import asyncpg
from typing import Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_user(self, username: str) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users WHERE username = $1", username)
            return [dict(row) for row in rows] if rows else None


    

    async def create_user(self, username: str, password: str) -> dict:
        hashed_pw = pwd_context.hash(password)
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
            INSERT INTO users (username, hashed_password)
            VALUES ($1, $2)
            RETURNING *
            """, username, hashed_pw)
            return dict(row)