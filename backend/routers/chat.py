import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from utils import limiter
from schemas import ChatRequest
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore
from config import MINIO_CLIENT, MINIO_BUCKET_NAME

from services.chat_service import (
    build_system_prompt,
    get_context_from_vector,
    prepare_messages_payload,
    generate_ai_stream,
    save_chat_message,
    get_chat_history, 
    get_user_sessions 
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

def get_vector_store() -> SimpleVectorStore:
    return SimpleVectorStore()


@router.post("/chat")
@limiter.limit("5/minute")
async def chat(
    request: Request,
    chat_data: ChatRequest,
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    current_history = []
    try:
        current_history = await get_chat_history(session_id=chat_data.session_id, username=current_user)
        if current_history and len(current_history) >= 30:
            raise HTTPException(
                status_code=403,
                detail="Demo limit reached for this chat session. Please start a new session."
            )
    except HTTPException:
        raise
    except Exception as history_err:
        logger.error(f"Error checking chat history limit: {history_err}")

    try:
        await save_chat_message(
            session_id=chat_data.session_id, 
            username=current_user, 
            role="user", 
            content=chat_data.message
        )
    except Exception as e:
        logger.error(f"Error saving user message: {e}")

    has_files = False
    context = ""
    try:
        has_files = await vector_store.has_uploaded_documents(chat_data.session_id)
        if has_files:
            context = await get_context_from_vector(vector_store, chat_data)
    except Exception as e:
        logger.error(f"Error checking uploaded documents: {e}")

    system_prompt = build_system_prompt(has_files, context)
    messages = prepare_messages_payload(system_prompt, current_history, chat_data.message)

    return StreamingResponse(
        generate_ai_stream(messages, vector_store, chat_data, current_user),
        media_type="text/event-stream"
    )


@router.get("/chat/history")
async def get_history(
    session_id: str,
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    if not session_id or session_id == "undefined":
        raise HTTPException(status_code=400, detail="Invalid or missing session_id")
    
    try:
        history = await get_chat_history(session_id=session_id, username=current_user)
        has_files = await vector_store.has_uploaded_documents(session_id)
        return {
            "history": history,
            "has_files": has_files
        }
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error fetching history")


@router.get("/chat/sessions")
async def get_sessions(
    current_user: str = Depends(get_current_user_from_cookie)
):
    try:
        sessions = await get_user_sessions(username=current_user)
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error fetching user sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error fetching sessions")


@router.delete("/chat/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    if not session_id or session_id == "undefined":
        raise HTTPException(status_code=400, detail="Invalid or missing session_id")
        
    try:
        files_to_delete = await vector_store.delete_chat_session(session_id=session_id, username=current_user)
        
        for file_name in files_to_delete:
            try:
                MINIO_CLIENT.delete_object(
                    Bucket=MINIO_BUCKET_NAME,
                    Key=file_name
                )
                logger.info(f"File {file_name} successfully deleted from Minio.")
            except Exception as minio_err:
                logger.warning(f"Failed to delete object {file_name} from MinIO: {minio_err}")
                
        return {"message": "Chat session, database records, and storage files deleted successfully."}
        
    except Exception as e:
        logger.error(f"Error during complete chat session deletion: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during session deletion.")