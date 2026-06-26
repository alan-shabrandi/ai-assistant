from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from config import AI_CLIENT, AI_MODEL_NAME
from schemas import ChatRequest
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore

router = APIRouter(tags=["Chat"])

def get_vector_store():
    store = SimpleVectorStore()
    return store


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    try:
        vector_store.save_message(
            session_id=request.session_id, 
            username=current_user, 
            role="user", 
            content=request.message
        )
    except Exception as e:
        print(f"Error saving user message: {e}")

    relevant_chunks = vector_store.search(request.message, top_k=3)
    context_items = []
    for chunk in relevant_chunks:
        clean_name = chunk['file_name'].split('_', 1)[-1] if chunk['file_name'] else "Unknown Source"
        context_items.append(f"[Source File: {clean_name}]\n{chunk['content']}")
        
    context = "\n---\n".join(context_items)
    
    system_prompt = (
        "You are an intelligent assistant. Use the following pieces of retrieved context to answer the user's question. "
        "If you don't know the answer or if it's not present in the context, just say that you don't know, "
        "do not try to make up an answer. Keep the answer concise. At the end of your response, "
        "always mention the name of the source file(s) you used to answer the question.\n\n"
        f"Context:\n{context}"
    )

    response = AI_CLIENT.chat.completions.create(
        model=AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ],
        stream=True
    )

    def generate():
        full_response = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        try:
            vector_store.save_message(
                session_id=request.session_id, 
                username=current_user, 
                role="assistant", 
                content=full_response
            )
        except Exception as e:
            print(f"Error saving assistant response: {e}")

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
    return {"history": history}

@router.get("/chat/sessions")
async def get_sessions(
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    sessions = vector_store.get_user_sessions(username=current_user)
    return {"sessions": sessions}