from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from io import BytesIO
import uuid

from config import MINIO_CLIENT, MINIO_BUCKET_NAME
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore, extract_and_chunk_pdf

router = APIRouter(tags=["Documents"])

def get_vector_store():
    return SimpleVectorStore()

@router.post("/documents/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        unique_file_name = f"{uuid.uuid4()}_{file.filename}"
        
        MINIO_CLIENT.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=unique_file_name,
            data=BytesIO(file_content),
            length=file_size,
            content_type="application/pdf"
        )
        print(f"File {unique_file_name} successfully uploaded to MinIO.")
        
        chunks = extract_and_chunk_pdf(BytesIO(file_content))
        
        if chunks:
            vector_store.add_documents(chunks=chunks, file_name=unique_file_name)
        else:
            print("No readable text found in the PDF.")
            
        return {
            "message": "File uploaded and indexed successfully",
            "file_name": unique_file_name,
            "chunks_count": len(chunks)
        }
        
    except Exception as e:
        print(f"Error during file upload or indexing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")