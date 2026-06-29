from fastapi import status

UPLOAD_PDF_DOCS = {
    "status_code": status.HTTP_202_ACCEPTED,
    "summary": "Upload and process PDF document",
    "description": (
        "Accepts a PDF file via multipart/form-data, stores it in the Object Storage, "
        "and initiates an asynchronous background task to extract text, chunk, and index "
        "the document embeddings into the vector store."
    ),
    "responses": {
        202: {
            "description": "File successfully uploaded and queued for background indexing.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "File uploaded successfully. Processing and indexing started in background.",
                        "file_name": "4f9e1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b_sample.pdf"
                    }
                }
            }
        },
        400: {"description": "Invalid file type. Only PDF files are accepted."},
        401: {"description": "Missing or invalid session cookie."},
        413: {"description": "File size exceeds the maximum allowed limit of 5MB."},
        429: {"description": "Rate limit exceeded (Maximum 3 requests per minute)."},
        502: {"description": "External storage server error. Failed to save the file."}
    }
}