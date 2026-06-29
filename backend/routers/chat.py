import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from utils import limiter
from config import AI_CLIENT, AI_MODEL_NAME
from schemas import ChatRequest
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore
from config import MINIO_CLIENT, MINIO_BUCKET_NAME

router = APIRouter(tags=["Chat"])

def get_vector_store():
    return SimpleVectorStore()


@router.post("/chat")
@limiter.limit("5/minute")
async def chat(
    request: Request,
    chat_data: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    current_history = []
    try:
        current_history = await vector_store.get_chat_history(session_id=chat_data.session_id, username=current_user)
        if current_history and len(current_history) >= 30:
            raise HTTPException(
                status_code=403,
                detail="Demo limit reached for this chat session. Please start a new session."
            )
    except HTTPException as http_err:
        raise http_err
    except Exception as history_err:
        print(f"Error checking chat history limit: {history_err}")

    is_first_message = len(current_history) == 0

    # ۱. ذخیره پیام کامل کاربر بدون دستکاری
    try:
        await vector_store.save_message(
            session_id=chat_data.session_id, 
            username=current_user, 
            role="user", 
            content=chat_data.message
        )
    except Exception as e:
        print(f"Error saving user message: {e}")

    has_files = False
    try:
        has_files = await vector_store.has_uploaded_documents(chat_data.session_id)
    except Exception as e:
        print(f"Error checking uploaded documents: {e}")

    context = ""
    if has_files:
        try:
            relevant_chunks = await vector_store.search(query=chat_data.message, session_id=chat_data.session_id, top_k=3)
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
        stream=True,
        temperature=0.7,
        top_p=0.9,
        max_tokens=1024
    )

    async def generate():
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

        # ذخیره پاسخ بات پس از اتمام استریم
        if full_response.strip():
            try:
                await vector_store.save_message(
                    session_id=chat_data.session_id, 
                    username=current_user, 
                    role="assistant", 
                    content=full_response
                )
            except Exception as save_assistant_err:
                print(f"Error saving assistant response: {save_assistant_err}")

        # ۲. تغییر کلیدی: تولید عنوان درست بعد از اتمام موفق استریم چت در اولین پیام سشن
        if is_first_message:
            try:
                print("--- Stream finished. Generating short title now... ---")
                title_prompt = (
                    "شما یک ابزار استخراج عنوان هستید. با توجه به پیام کاربر که در ادامه می‌آید، "
                    "یک عنوان بسیار کوتاه، خلاصه و جذاب بین ۲ تا ۴ کلمه به زبان فارسی (یا انگلیسی اگر پیام کاملا انگلیسی است) بفرستید. "
                    "قوانین: فقط و فقط خود عنوان را بفرستید و از هیچ نشانه، علامت، نقل‌قول یا توضیحی استفاده نکنید.\n\n"
                    f"پیام کاربر:\n{chat_data.message}"
                )
                
                # اجرای کاملاً ایمن فرآیند سنکرون ال‌ال‌ام در بدنه داخلی جنریتور آسنکرون
                loop = asyncio.get_event_loop()
                title_res = await loop.run_in_executor(
                    None,
                    lambda: AI_CLIENT.chat.completions.create(
                        model=AI_MODEL_NAME,
                        messages=[{"role": "user", "content": title_prompt}],
                        stream=False,
                        max_tokens=20,
                        temperature=0.5
                    )
                )
                title = title_res.choices[0].message.content.strip()
                title = title.replace('"', '').replace("'", "").replace("عنوان:", "").strip()
                
                if title:
                    # ذخیره مستقیم و بدون ارور در دیتابیس
                    await vector_store.set_session_title(chat_data.session_id, title)
                    print(f"--- Chat title successfully updated to DB: {title} ---")
            except Exception as title_err:
                print(f"Error generating title inside generator: {title_err}")

    return StreamingResponse(generate(), media_type="text/event-stream")