import psycopg2
from psycopg2.extras import execute_values
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from io import BytesIO

from config import DATABASE_URL, AI_CLIENT, EMBEDDING_MODEL, DEFAULT_DIMENSION


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

    def _get_connection(self):
        return psycopg2.connect(DATABASE_URL)

    def init_db(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        file_name VARCHAR(255),
                        content TEXT,
                        embedding vector({self.dimension})
                    );
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL
                    );
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id SERIAL PRIMARY KEY,
                        session_id UUID NOT NULL,
                        username VARCHAR(50) NOT NULL,
                        role VARCHAR(10) NOT NULL, -- 'user' یا 'assistant'
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                    );
                """)
            conn.commit()

    def get_embedding(self, text: str) -> list[float]:
        response = AI_CLIENT.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, chunks: list[str], file_name: str):
        if not chunks:
            return
            
        with self._get_connection() as conn:
            data_to_insert = []
            for chunk in chunks:
                try:
                    emb = self.get_embedding(chunk)
                    data_to_insert.append((file_name, chunk, emb))
                except Exception as e:
                    print(f"Error generating embedding for chunk: {e}")
                    continue
            
            if data_to_insert:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        "INSERT INTO documents (file_name, content, embedding) VALUES %s",
                        data_to_insert
                    )
                conn.commit()
                print(f"Successfully indexed {len(data_to_insert)} chunks for file {file_name}.")

    def search(self, query: str, top_k: int = 3) -> list[str]:
        query_emb = self.get_embedding(query)
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT content, file_name FROM documents 
                    ORDER BY embedding <=> %s::vector 
                    LIMIT %s;
                    """,
                    (query_emb, top_k)
                )
                rows = cur.fetchall()
        return [{"content": row[0], "file_name": row[1]} for row in rows]
    
    def save_message(self, session_id: str, username: str, role: str, content: str):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chat_messages (session_id, username, role, content)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (session_id, username, role, content)
                )
            conn.commit()
            
    def get_chat_history(self, session_id: str, username: str):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT role, content, created_at 
                    FROM chat_messages 
                    WHERE session_id = %s AND username = %s 
                    ORDER BY created_at ASC;
                    """,
                    (session_id, username)
                )
                rows = cur.fetchall()
        return [{"role": row[0], "content": row[1], "created_at": row[2].isoformat()} for row in rows]

    def get_user_sessions(self, username: str):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT ON (session_id) session_id, content, created_at
                    FROM chat_messages
                    WHERE username = %s AND role = 'user'
                    ORDER BY session_id, created_at ASC;
                    """,
                    (username,)
                )
                rows = cur.fetchall()
        rows.sort(key=lambda x: x[2], reverse=True)
        return [{"session_id": str(row[0]), "title": row[1]} for row in rows]