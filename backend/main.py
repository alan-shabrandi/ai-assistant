import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from utils import limiter

from routers import auth, chat, document
from vector_store import SimpleVectorStore
from database import initialize_pool, open_pool, close_pool, get_db

logger = logging.getLogger(__name__)

async def init_general_tables():
    async with get_db() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL
                    );
                """)
                
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id SERIAL PRIMARY KEY,
                        session_id UUID NOT NULL,
                        username VARCHAR(50) NOT NULL,
                        role VARCHAR(10) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                    );
                """)
                await conn.commit()
                logger.info("General database tables initialized successfully.")
            except Exception as e:
                await conn.rollback()
                logger.error(f"Failed to initialize general database tables: {e}", exc_info=True)
                raise e


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_pool()
    await open_pool()
    
    try:
        print("Initializing database tables...")
        await init_general_tables()
        
        store = SimpleVectorStore()
        await store.init_vector_table()
        
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        logger.error(f"Critical error during startup: {e}", exc_info=True)
        
    yield
    
    await close_pool()

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."}
    )

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai-assistant-murex-beta.vercel.app"
]

FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(document.router)