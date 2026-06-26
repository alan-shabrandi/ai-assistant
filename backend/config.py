import os
from openai import OpenAI

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10000
COOKIE_NAME = "access_token"

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    AI_CLIENT = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
    EMBEDDING_MODEL = "openai/text-embedding-3-small"
    DEFAULT_DIMENSION = 1536
    AI_MODEL_NAME = "qwen/qwen-2.5-72b-instruct"
else:
    AI_CLIENT = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
    EMBEDDING_MODEL = "nomic-embed-text"
    DEFAULT_DIMENSION = 768
    AI_MODEL_NAME = "my-qwen3"