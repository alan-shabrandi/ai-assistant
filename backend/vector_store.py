from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from io import BytesIO

from config import DATABASE_URL, AI_CLIENT, EMBEDDING_MODEL, DEFAULT_DIMENSION
from database import get_db


def extract_and_chunk_pdf(file_stream: BytesIO, chunk_size: int = 600, chunk_overlap: int = 100) -> list[str]:
    reader = PdfReader(file_stream)
    full_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(full_text)


class SimpleVectorStore:
    def __init__(self, dimension: int = DEFAULT_DIMENSION):
        self.dimension = dimension

    async def init_db(self):
        async with get_db() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
                    await cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS documents (
                            id SERIAL PRIMARY KEY,
                            session_id UUID NOT NULL,
                            file_name VARCHAR(255),
                            content TEXT,
                            embedding vector({self.dimension})
                        );
                    """)
                    
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
                except Exception as e:
                    await conn.rollback()
                    print(f"Failed to initialize database tables: {e}")
                    raise e

    def get_embedding(self, text: str) -> list[float]:
        response = AI_CLIENT.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    async def add_documents(self, chunks: list[str], file_name: str, session_id: str):
        if not chunks:
            return
            
        data_to_insert = []
        for chunk in chunks:
            try:
                emb = self.get_embedding(chunk)
                data_to_insert.append((session_id, file_name, chunk, emb))
            except Exception as e:
                print(f"Error generating embedding for chunk: {e}")
                continue
        
        if data_to_insert:
            async with get_db() as conn:
                async with conn.cursor() as cur:
                    try:
                        await cur.executemany(
                            "INSERT INTO documents (session_id, file_name, content, embedding) VALUES (%s, %s, %s, %s)",
                            data_to_insert
                        )
                        await conn.commit()
                        print(f"Successfully indexed {len(data_to_insert)} chunks for file {file_name}.")
                    except Exception as e:
                        await conn.rollback()
                        print(f"Transaction failed during adding documents: {e}")
                        raise e

    async def search(self, query: str, session_id: str, top_k: int = 3) -> list[dict]:
        query_emb = self.get_embedding(query)
        
        async with get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT content, file_name FROM documents 
                    WHERE session_id = %s
                    ORDER BY embedding <=> %s::vector 
                    LIMIT %s;
                    """,
                    (session_id, query_emb, top_k)
                )
                rows = await cur.fetchall()
        return [{"content": row[0], "file_name": row[1]} for row in rows]
    
    async def has_uploaded_documents(self, session_id: str) -> bool:
        async with get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM documents WHERE session_id = %s);",
                    (session_id,)
                )
                res = await cur.fetchone()
                return res[0]

    async def save_message(self, session_id: str, username: str, role: str, content: str):
        async with get_db() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO chat_messages (session_id, username, role, content)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (session_id, username, role, content)
                    )
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    print(f"Failed to save chat message: {e}")
                    raise e
            
    async def get_chat_history(self, session_id: str, username: str):
        async with get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT role, content, created_at 
                    FROM chat_messages 
                    WHERE session_id = %s AND username = %s 
                    ORDER BY created_at ASC;
                    """,
                    (session_id, username)
                )
                rows = await cur.fetchall()
        return [{"role": row[0], "content": row[1], "created_at": row[2].isoformat()} for row in rows]

    async def get_user_sessions(self, username: str):
        async with get_db() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        WITH session_latest AS (
                            SELECT session_id, MAX(created_at) as last_activity
                            FROM chat_messages
                            WHERE username = %s
                            GROUP BY session_id
                        ),
                        session_first_msg AS (
                            SELECT DISTINCT ON (session_id) session_id, content as original_msg
                            FROM chat_messages
                            WHERE username = %s AND role = 'user'
                            ORDER BY session_id, created_at ASC
                        )
                        SELECT 
                            sl.session_id, 
                            sf.original_msg as title
                        FROM session_latest sl
                        LEFT JOIN session_first_msg sf ON sl.session_id = sf.session_id
                        ORDER BY sl.last_activity DESC;  -- اصلاح شد
                        """,
                        (username, username)
                    )
                    rows = await cur.fetchall()
                    return [{"session_id": str(row[0]), "title": row[1] if row[1] else "چت بدون پیام"} for row in rows]
                except Exception as e:
                    print(f"Error fetching sessions: {e}")
                    return []
    
    async def delete_chat_session(self, session_id: str, username: str) -> list[str]:
        file_names_to_delete = []
        async with get_db() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "SELECT 1 FROM chat_messages WHERE session_id = %s AND username = %s LIMIT 1;",
                        (session_id, username)
                    )
                    res = await cur.fetchone()
                    if not res:
                        return []

                    await cur.execute(
                        "SELECT DISTINCT file_name FROM documents WHERE session_id = %s AND file_name IS NOT NULL;",
                        (session_id,)
                    )
                    rows = await cur.fetchall()
                    file_names_to_delete = [row[0] for row in rows]

                    await cur.execute(
                        "DELETE FROM documents WHERE session_id = %s;",
                        (session_id,)
                    )

                    await cur.execute(
                        "DELETE FROM chat_messages WHERE session_id = %s AND username = %s;",
                        (session_id, username)
                    )
                    
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    print(f"Transaction failed during chat session deletion: {e}")
                    raise e
                    
        return file_names_to_delete