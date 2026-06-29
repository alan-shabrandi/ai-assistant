import logging
from io import BytesIO
from pypdf import PdfReader
from fastapi.concurrency import run_in_threadpool
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import MINIO_CLIENT, MINIO_BUCKET_NAME
from vector_store import SimpleVectorStore

logger = logging.getLogger(__name__)


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


def _sync_upload_to_minio(file_content: bytes, unique_file_name: str):
    MINIO_CLIENT.upload_fileobj(
        Fileobj=BytesIO(file_content),
        Bucket=MINIO_BUCKET_NAME,
        Key=unique_file_name,
        ExtraArgs={"ContentType": "application/pdf"}
    )


def _sync_extract_pdf(file_content: bytes):
    return extract_and_chunk_pdf(BytesIO(file_content))


async def upload_to_storage(file_content: bytes, unique_file_name: str):
    await run_in_threadpool(_sync_upload_to_minio, file_content, unique_file_name)
    logger.info(f"File {unique_file_name} successfully uploaded to MinIO.")


async def process_pdf_background(file_content: bytes, unique_file_name: str, session_id: str, vector_store: SimpleVectorStore):
    try:
        chunks = await run_in_threadpool(_sync_extract_pdf, file_content)
        
        if chunks:
            await vector_store.add_documents(chunks=chunks, file_name=unique_file_name, session_id=session_id)
            logger.info(f"Successfully indexed chunks for {unique_file_name}")
        else:
            logger.warning(f"No readable text found in the PDF ({unique_file_name}). Not indexed.")
    except Exception as e:
        logger.error(f"Background indexing failed for {unique_file_name}: {e}", exc_info=True)