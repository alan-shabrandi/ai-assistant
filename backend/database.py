import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config import DATABASE_URL

db_pool = None

def initialize_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=5,
                maxconn=20,
                dsn=DATABASE_URL
            )
            print("Database Connection Pool initialized successfully.")
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            raise e

def close_pool():
    global db_pool
    if db_pool:
        db_pool.closeall()
        print("Database Connection Pool closed.")

@contextmanager
def get_db():
    global db_pool
    if db_pool is None:
        raise RuntimeError("Database connection pool is not initialized.")
    
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)