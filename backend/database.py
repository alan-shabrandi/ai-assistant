from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from config import DATABASE_URL

db_pool = None

def initialize_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = AsyncConnectionPool(
                conninfo=DATABASE_URL,
                min_size=5,
                max_size=20,
                open=False
            )
            print("Async Database Connection Pool defined.")
        except Exception as e:
            print(f"Error defining async connection pool: {e}")
            raise e

async def open_pool():
    global db_pool
    if db_pool:
        await db_pool.open()
        print("Async Database Connection Pool opened successfully.")

async def close_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        print("Async Database Connection Pool closed.")

@asynccontextmanager
async def get_db():
    global db_pool
    if db_pool is None:
        raise RuntimeError("Async Database connection pool is not initialized.")
    
    async with db_pool.connection() as conn:
        yield conn