from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, BackgroundTasks
from io import BytesIO
import uuid
from utils import limiter
from config import MINIO_CLIENT, MINIO_BUCKET_NAME
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore, extract_and_chunk_pdf

router = APIRouter(tags=["Documents"])

def get_vector_store():
    return SimpleVectorStore()

MAX_FILE_SIZE = 5 * 1024 * 1024

async def process_pdf_background(file_content: bytes, unique_file_name: str, session_id: str, vector_store: SimpleVectorStore):
    try:
        chunks = extract_and_chunk_pdf(BytesIO(file_content))
        if chunks:
            await vector_store.add_documents(chunks=chunks, file_name=unique_file_name, session_id=session_id)
        else:
            print(f"No readable text found in the PDF ({unique_file_name}). Not indexed.")
    except Exception as e:
        print(f"Background indexing failed for {unique_file_name}: {e}")


@router.post("/documents/upload")
@limiter.limit("3/minute")
async def upload_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form(...),
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail="File is too large. Maximum allowed size is 5MB."
            )
        
        unique_file_name = f"{uuid.uuid4()}_{file.filename}"
        
        try:
            MINIO_CLIENT.upload_fileobj(
                Fileobj=BytesIO(file_content),
                Bucket=MINIO_BUCKET_NAME,
                Key=unique_file_name,
                ExtraArgs={"ContentType": "application/pdf"}
            )
            print(f"File {unique_file_name} successfully uploaded to MinIO.")
        except Exception as storage_err:
            print(f"Storage Upload Error: {storage_err}")
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to upload file to storage server: {str(storage_err)}"
            )
        
        background_tasks.add_task(
            process_pdf_background, 
            file_content, 
            unique_file_name, 
            session_id, 
            vector_store
        )
            
        return {
            "message": "File uploaded successfully. Processing and indexing started in background.",
            "file_name": unique_file_name
        }
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Error during file upload: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")