import logging
import psycopg
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from database import get_db
from schemas import UserRegister
from security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)

async def register_user(user_data: UserRegister):
    hashed_pwd = await run_in_threadpool(hash_password, user_data.password)
    
    try:
        async with get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
                    (user_data.username, hashed_pwd)
                )
                await conn.commit()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        logger.error(f"Database error during registration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def authenticate_user(username: str, password_raw: str) -> str:
    try:
        async with get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT hashed_password FROM users WHERE username = %s", (username,))
                user_row = await cur.fetchone()
    except Exception as e:
        logger.error(f"Database error during login for user {username}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
        
    if not user_row:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    hashed_pwd = user_row[0]
    
    is_valid = await run_in_threadpool(verify_password, password_raw, hashed_pwd)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    token = create_access_token(data={"sub": username})
    return token