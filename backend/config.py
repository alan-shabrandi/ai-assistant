import os
from openai import AsyncOpenAI
import boto3
from botocore.client import Config

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10000
COOKIE_NAME = "access_token"

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    AI_CLIENT = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
    EMBEDDING_MODEL = "openai/text-embedding-3-small"
    DEFAULT_DIMENSION = 1536
    AI_MODEL_NAME = "qwen/qwen-2.5-72b-instruct"
else:
    AI_CLIENT = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama")
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
    full_url = f"https://{clean_endpoint}/storage/v1/s3"
    
    MINIO_CLIENT = boto3.client(
        "s3",
        endpoint_url=full_url,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="eu-central-1",
        config=Config(signature_version="s3v4")
    )
else:
    clean_endpoint = MINIO_ENDPOINT.replace("https://", "").replace("http://", "")
    
    if "localhost" in clean_endpoint or "127.0.0.1" in clean_endpoint:
        clean_endpoint = clean_endpoint.replace("localhost", "minio").replace("127.0.0.1", "minio")
        
    full_url = f"http://{clean_endpoint}"
    
    MINIO_CLIENT = boto3.client(
        "s3",
        endpoint_url=full_url,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(s3={'addressing_style': 'path'})
    )

try:
    if not IS_PRODUCTION:
        try:
            MINIO_CLIENT.head_bucket(Bucket=MINIO_BUCKET_NAME)
        except Exception:
            MINIO_CLIENT.create_bucket(Bucket=MINIO_BUCKET_NAME)
            print(f"Bucket '{MINIO_BUCKET_NAME}' created successfully on Local MinIO.")
    else:
        print("Connected to Supabase Storage via boto3 successfully.")
except Exception as e:
    print(f"Error initializing storage bucket: {e}")