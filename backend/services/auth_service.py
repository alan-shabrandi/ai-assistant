import logging
import psycopg
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool

from database import get_db
from schemas import UserRegister
from security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)

DUMMY_HASH = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

async def register_user(user_data: UserRegister) -> None:
    hashed_pwd = await run_in_threadpool(hash_password, user_data.password)
    
    async with get_db() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(
                    "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
                    (user_data.username, hashed_pwd)
                )
            except psycopg.errors.UniqueViolation:
                raise HTTPException(status_code=400, detail="Username already exists")
            except psycopg.Error as db_err:
                logger.error(f"Database internal error during registration: {db_err}", exc_info=True)
                raise HTTPException(status_code=500, detail="Internal server error")


async def authenticate_user(username: str, password_raw: str) -> str:
    user_row = None
    
    async with get_db() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(
                    "SELECT hashed_password FROM users WHERE username = %s", 
                    (username,)
                )
                user_row = await cur.fetchone()
            except psycopg.Error as db_err:
                logger.error(f"Database error during login for user {username}: {db_err}", exc_info=True)
                raise HTTPException(status_code=500, detail="Internal server error")
        
    hashed_pwd = user_row[0] if user_row else DUMMY_HASH
    
    is_valid = await run_in_threadpool(verify_password, password_raw, hashed_pwd)
    
    if not user_row or not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    return create_access_token(data={"sub": username})