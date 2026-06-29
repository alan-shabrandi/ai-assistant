import logging
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request, BackgroundTasks, status
from utils import limiter
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore

from services.document_service import upload_to_storage, process_pdf_background
from routers.document_docs import UPLOAD_PDF_DOCS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Documents"])

MAX_FILE_SIZE = 5 * 1024 * 1024

def get_vector_store() -> SimpleVectorStore:
    return SimpleVectorStore()


@router.post("/documents/upload", **UPLOAD_PDF_DOCS)
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
            await upload_to_storage(file_content, unique_file_name)
        except Exception as storage_err:
            logger.error(f"Storage Upload Error for {unique_file_name}: {storage_err}")
            raise HTTPException(
                status_code=502, 
                detail="Failed to upload file to storage server."
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during upload.")