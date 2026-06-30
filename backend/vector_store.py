import asyncio
import logging
from config import AI_CLIENT, EMBEDDING_MODEL, DEFAULT_DIMENSION
from database import get_db

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    def __init__(self, dimension: int = DEFAULT_DIMENSION):
        self.dimension = dimension

    async def init_vector_table(self):
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
                    await conn.commit()
                    logger.info("Vector store table initialized successfully.")
                except Exception as e:
                    await conn.rollback()
                    logger.error(f"Failed to initialize vector store table: {e}", exc_info=True)
                    raise e

    async def get_embedding(self, text: str) -> list[float]:
        response = await AI_CLIENT.embeddings.create(
            model=EMBEDDING_MODEL, 
            input=text
        )
        return response.data[0].embedding

    async def add_documents(self, chunks: list[str], file_name: str, session_id: str):
        if not chunks:
            return
            
        logger.info(f"Generating embeddings for {len(chunks)} chunks of file: {file_name}")
        
        tasks = [self.get_embedding(chunk) for chunk in chunks]
        embeddings = await asyncio.gather(*tasks, return_exceptions=True)
        
        data_to_insert = []
        for chunk, emb in zip(chunks, embeddings):
            if isinstance(emb, Exception):
                logger.error(f"Error generating embedding for a chunk in {file_name}: {emb}")
                continue
            data_to_insert.append((session_id, file_name, chunk, emb))
        
        if data_to_insert:
            async with get_db() as conn:
                async with conn.cursor() as cur:
                    try:
                        await cur.executemany(
                            "INSERT INTO documents (session_id, file_name, content, embedding) VALUES (%s, %s, %s, %s)",
                            data_to_insert
                        )
                        await conn.commit()
                        logger.info(f"Successfully indexed {len(data_to_insert)} chunks for file {file_name}.")
                    except Exception as e:
                        await conn.rollback()
                        logger.error(f"Transaction failed during adding documents: {e}", exc_info=True)
                        raise e

    async def search(self, query: str, session_id: str, top_k: int = 3) -> list[dict]:
        query_emb = await self.get_embedding(query)
        
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
                return res[0] if res else False
                
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
                    logger.error(f"Transaction failed during chat session deletion: {e}", exc_info=True)
                    raise e
                    
        return file_names_to_delete