import os
from openai import OpenAI
from minio import Minio

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
    
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

IS_PRODUCTION = MINIO_ENDPOINT and "supabase" in MINIO_ENDPOINT.lower()

if IS_PRODUCTION:
    clean_endpoint = MINIO_ENDPOINT.replace("https://", "").replace("http://", "").split("/")[0]
else:
    clean_endpoint = MINIO_ENDPOINT.replace("https://", "").replace("http://", "").split("/")[0]

MINIO_CLIENT = Minio(
    clean_endpoint,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=True if IS_PRODUCTION else False,
    region="eu-central-1" if IS_PRODUCTION else None
)

if IS_PRODUCTION:
    MINIO_CLIENT._base_url.is_aws = False
    MINIO_CLIENT._base_url.bucket_path = lambda bucket_name: f"/storage/v1/s3/{bucket_name}"
    MINIO_CLIENT._base_url.object_path = lambda bucket_name, object_name: f"/storage/v1/s3/{bucket_name}/{object_name}"

try:
    if not IS_PRODUCTION:
        if not MINIO_CLIENT.bucket_exists(MINIO_BUCKET_NAME):
            MINIO_CLIENT.make_bucket(MINIO_BUCKET_NAME)
            print(f"Bucket '{MINIO_BUCKET_NAME}' created successfully on Local MinIO.")
    else:
        print("Connected to Supabase Storage successfully.")
except Exception as e:
    print(f"Error connecting to Storage or initializing bucket: {e}")