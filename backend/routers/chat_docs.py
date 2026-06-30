from fastapi import status

CHAT_DOCS = {
    "status_code": status.HTTP_200_OK,
    "summary": "Stream RAG chat response",
    "description": (
        "Accepts a user message and streams contextual responses from the AI. "
        "Performs semantic search on vector store if documents exist for the session. "
        "Enforces a limit of 30 messages per session for demo stability."
    ),
    "responses": {
        200: {
            "description": "Server-Sent Events (SSE) text stream successfully initiated.",
            "content": {"text/event-stream": {}}
        },
        401: {"description": "Missing or invalid session cookie."},
        403: {"description": "Demo limit reached (30 messages maximum for this session)."},
        429: {"description": "Rate limit exceeded (Maximum 5 requests per minute)."}
    }
}

GET_HISTORY_DOCS = {
    "status_code": status.HTTP_200_OK,
    "summary": "Get chat messages history",
    "description": "Retrieves all past messages and checks if documents are mapped to the given session.",
    "responses": {
        200: {
            "description": "History and file attachment state fetched.",
            "content": {
                "application/json": {
                    "example": {
                        "history": [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}],
                        "has_files": True
                    }
                }
            }
        },
        400: {"description": "Invalid or missing session_id."},
        500: {"description": "Internal database error."}
    }
}

GET_SESSIONS_DOCS = {
    "status_code": status.HTTP_200_OK,
    "summary": "Get all active user sessions",
    "description": "Fetches a list of all historical unique chat session IDs created by the authenticated user.",
    "responses": {
        200: {
            "description": "List of sessions retrieved.",
            "content": {"application/json": {"example": {"sessions": ["session_id_1", "session_id_2"]}}}
        }
    }
}

DELETE_SESSION_DOCS = {
    "status_code": status.HTTP_200_OK,
    "summary": "Delete chat session and assets",
    "description": "Cascades deletion of chat history, vectors from database, and raw files from MinIO/Storage.",
    "responses": {
        200: {"description": "Session, database records, and storage files deleted successfully."},
        400: {"description": "Invalid or missing session_id."},
        500: {"description": "Failed to clean up assets cleanly."}
    }
}