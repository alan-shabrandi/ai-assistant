from contextlib import contextmanager
import psycopg2
from config import DATABASE_URL

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()