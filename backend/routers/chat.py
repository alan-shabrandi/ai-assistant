from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from utils import limiter
from config import AI_CLIENT, AI_MODEL_NAME
from schemas import ChatRequest
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore

router = APIRouter(tags=["Chat"])

def get_vector_store():
    store = SimpleVectorStore()
    return store


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
        current_history = vector_store.get_chat_history(session_id=chat_data.session_id, username=current_user)
        if current_history and len(current_history) >= 30:
            raise HTTPException(
                status_code=403,
                detail="Demo limit reached for this chat session. Please start a new session."
            )
    except HTTPException as http_err:
        raise http_err
    except Exception as history_err:
        print(f"Error checking chat history limit: {history_err}")

    try:
        vector_store.save_message(
            session_id=chat_data.session_id, 
            username=current_user, 
            role="user", 
            content=chat_data.message
        )
    except Exception as e:
        print(f"Error saving user message: {e}")

    has_files = False
    try:
        has_files = vector_store.has_uploaded_documents(chat_data.session_id)
    except Exception as e:
        print(f"Error checking uploaded documents: {e}")

    context = ""
    if has_files:
        try:
            relevant_chunks = vector_store.search(query=chat_data.message, session_id=chat_data.session_id, top_k=3)
            context_items = []
            for chunk in relevant_chunks:
                clean_name = chunk['file_name'].split('_', 1)[-1] if chunk['file_name'] else "Unknown Source"
                context_items.append(f"[Source File: {clean_name}]\n{chunk['content']}")
                
            context = "\n---\n".join(context_items)
        except Exception as e:
            print(f"Error during vector search: {e}")

    if has_files and context.strip():
        system_prompt = (
            "شما یک دستیار هوشمند و حرفه‌ای هستید. با استفاده از اطلاعاتی که در بخش «متن زیر» آمده است، به سوال کاربر پاسخ دهید.\n\n"
            "قوانین مهم:\n"
            "۱. حتماً و بدون استثنا به زبان فارسی روان و کاملاً طبیعی پاسخ دهید.\n"
            "۲. پاسخ را خلاصه، مفید و مرتب بنویسید.\n"
            "۳. اگر پاسخ سوال در متن زیر وجود ندارد، به سادگی بگویید که اطلاعاتی در این باره ندارید و از خودتان پاسخ نسازید.\n"
            "۴. در انتهای پاسخ، حتماً نام فایل منبع را در یک خط جدید و دقیقاً به این فرمت بنویسید:\n"
            "[نام فایل] :منبع"
            f"\n\nمتن زیر:\n{context}"
        )
    else:
        system_prompt = (
            "شما یک دستیار هوشمند و مهربان هستید. به پیام کاربر به صورت روان و طبیعی پاسخ دهید.\n"
            "قاعده کلیدی: حتماً به همان زبانی که کاربر می‌نویسد (فارسی یا انگلیسی) پاسخ دهید.\n"
            "به هیچ وجه به مستندات، فایل‌ها یا نبود اطلاعات اشاره نکنید و یک مکالمه چت عادی داشته باشید."
        )

    messages = [{"role": "system", "content": system_prompt}]
    
    if current_history:
        for msg in current_history[-5:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
    messages.append({"role": "user", "content": chat_data.message})

    print(f"--- Calling AI Model (Stream): {AI_MODEL_NAME} ---")
    
    response = AI_CLIENT.chat.completions.create(
        model=AI_MODEL_NAME,
        messages=messages,
        stream=True
    )

    def generate():
        full_response = ""
        for chunk in response:
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
                vector_store.save_message(
                    session_id=chat_data.session_id, 
                    username=current_user, 
                    role="assistant", 
                    content=full_response
                )
            except Exception as save_assistant_err:
                print(f"Error saving assistant response: {save_assistant_err}")

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history")
async def get_history(
    session_id: str,
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    if not session_id or session_id == "undefined":
        raise HTTPException(status_code=400, detail="Invalid or missing session_id")
    
    history = vector_store.get_chat_history(session_id=session_id, username=current_user)
    
    has_files = False
    try:
        has_files = vector_store.has_uploaded_documents(session_id)
    except Exception as e:
        print(f"Error checking documents in history endpoint: {e}")

    return {
        "history": history,
        "has_files": has_files
    }


@router.get("/chat/sessions")
async def get_sessions(
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    sessions = vector_store.get_user_sessions(username=current_user)
    return {"sessions": sessions}