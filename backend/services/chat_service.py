import logging
from typing import AsyncGenerator, List, Dict, Any
from config import AI_CLIENT, AI_MODEL_NAME
from schemas import ChatRequest
from vector_store import SimpleVectorStore
from database import get_db

logger = logging.getLogger(__name__)

def build_system_prompt(has_files: bool, context: str) -> str:
    if has_files and context.strip():
        return (
            "شما یک دستیار هوشمند و حرفه‌ای هستید. با استفاده از اطلاعاتی که در بخش «متن زیر» آمده است، به سوال کاربر پاسخ دهید.\n\n"
            "قوانین مهم:\n"
            "۱. حتماً و بدون استثنا به زبان فارسی روان و کاملاً طبیعی پاسخ دهید.\n"
            "۲. پاسخ را خلاصه، مفید و مرتب بنویسید.\n"
            "۳. اگر پاسخ سوال در متن زیر وجود ندارد، به سادگی بگویید که اطلاعاتی در این باره ندارید و از خودتان پاسخ نسازید.\n"
            "۴. در انتهای پاسخ، حتماً نام فایل منبع را در یک خط جدید و دقیقاً به این فرمت بنویسید:\n"
            "[نام فایل] :منبع"
            f"\n\nمتن زیر:\n{context}"
        )
    
    return (
        "شما یک دستیار هوشمند و مهربان هستید. به پیام کاربر به صورت روان و طبیعی پاسخ دهید.\n"
        "قاعده کلیدی: حتماً به همان زبانی که کاربر می‌نویسد (فارسی یا انگلیسی) پاسخ دهید.\n"
        "به هیچ وجه به مستندات، فایل‌ها یا نبود اطلاعات اشاره نکنید و یک مکالمه چت عادی داشته باشید."
    )


async def get_context_from_vector(vector_store: SimpleVectorStore, chat_data: ChatRequest) -> str:
    try:
        relevant_chunks = await vector_store.search(
            query=chat_data.message, 
            session_id=chat_data.session_id, 
            top_k=3
        )
        context_items = []
        for chunk in relevant_chunks:
            clean_name = chunk['file_name'].split('_', 1)[-1] if chunk['file_name'] else "Unknown Source"
            context_items.append(f"[Source File: {clean_name}]\n{chunk['content']}")
        
        return "\n---\n".join(context_items)
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        return ""


def prepare_messages_payload(system_prompt: str, current_history: List[Dict[str, Any]], user_message: str) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": system_prompt}]
    
    if current_history:
        for msg in current_history[-5:]:
            messages.append({
                "role": msg.get("role", "user"), 
                "content": msg.get("content", "")
            })
            
    messages.append({"role": "user", "content": user_message})
    return messages


async def generate_ai_stream(
    messages: List[Dict[str, str]], 
    vector_store: SimpleVectorStore, 
    chat_data: ChatRequest, 
    current_user: str
) -> AsyncGenerator[str, None]:
    logger.info(f"Calling AI Model (Stream): {AI_MODEL_NAME}")
    try:
        response = await AI_CLIENT.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=messages,
            stream=True,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1024
        )
    except Exception as ai_err:
        logger.error(f"AI Generation failed to initialize: {ai_err}")
        yield "data: Error generating response from AI. Please try again.\n\n"
        return

    full_response = ""
    
    async for chunk in response: 
        if chunk and chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", "")
            if content is not None and content != "":
                if content.lower() == "null":
                    continue
                full_response += content
                yield f"data: {content}\n\n"

    if full_response.strip():
        try:
            await save_chat_message(
                session_id=chat_data.session_id, 
                username=current_user, 
                role="assistant", 
                content=full_response
            )
        except Exception as save_assistant_err:
            logger.error(f"Error saving assistant response to database: {save_assistant_err}")
            
async def save_chat_message(session_id: str, username: str, role: str, content: str):
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
                logger.error(f"Failed to save chat message: {e}", exc_info=True)
                raise e


async def get_chat_history(session_id: str, username: str) -> List[Dict[str, Any]]:
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


async def get_user_sessions(username: str) -> List[Dict[str, Any]]:
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
                    ORDER BY sl.last_activity DESC;
                    """,
                    (username, username)
                )
                rows = await cur.fetchall()
                return [{"session_id": str(row[0]), "title": row[1] if row[1] else "چت بدون پیام"} for row in rows]
            except Exception as e:
                logger.error(f"Error fetching sessions: {e}", exc_info=True)
                return []