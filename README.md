[![Swagger API Docs](https://img.shields.io/badge/Swagger-API_Docs-green?style=for-the-badge&logo=swagger)](https://api.shabrandi.ir/docs)

# 🚀 AI-Powered RAG Chat Assistant (Fullstack)

### FastAPI + Next.js + PostgreSQL (pgvector) + MinIO

A production-ready, fully asynchronous **Retrieval-Augmented Generation (RAG) fullstack system** for intelligent conversations over uploaded PDF documents.

🔗 **Live Demo (Production):** https://ai-assistant.shabrandi.ir

Users can upload PDF files, which are automatically:

- Parsed
- Chunked
- Embedded
- Indexed into a vector database

The AI model (via **OpenRouter** or **Local Ollama**) retrieves the most relevant context and streams accurate responses in real time through a modern **Next.js frontend**.

This project follows **Clean Architecture**, modular design principles, and production-grade async backend patterns.

---

# ✨ Features

- ⚡ **Fullstack Asynchronous System**
  - Backend: FastAPI
  - Frontend: Next.js
  - Async PostgreSQL (`psycopg` / `asyncpg`)
  - `AsyncOpenAI`

- 🔍 **Native Vector Search**
  - PostgreSQL + `pgvector`
  - Cosine similarity search (`<=>`)

- 🧵 **Non-blocking Heavy Tasks**
  - PDF extraction
  - Document chunking
  - Thread pool execution via `run_in_threadpool`

- ☁️ **Hybrid Object Storage**
  - MinIO for local development
  - Compatible with Supabase Storage

- 🔐 **Secure Authentication**
  - JWT Authentication
  - HTTP-only Cookies
  - Session isolation

- 🚦 **Rate Limiting**
  - Powered by `slowapi`
  - Prevents abuse and reduces LLM cost spikes

- 🐳 **Dockerized Infrastructure**
  - FastAPI backend
  - PostgreSQL + pgvector
  - MinIO
  - One-command deployment

---

# 🛠️ Tech Stack

| Category         | Technology                                   |
| ---------------- | -------------------------------------------- |
| Backend          | FastAPI (Python 3.11+)                       |
| Frontend         | Next.js                                      |
| Database         | PostgreSQL                                   |
| Vector Store     | pgvector                                     |
| Object Storage   | MinIO / Supabase Storage (`boto3`)           |
| LLM Provider     | AsyncOpenAI (OpenRouter / Ollama)            |
| Text Splitting   | LangChain (`RecursiveCharacterTextSplitter`) |
| Containerization | Docker & Docker Compose                      |

---

# 🏗️ Project Structure

The project follows the **Single Responsibility Principle (SRP)** and a modular service-oriented architecture.

```text
app/
├── config.py
├── database.py
├── main.py
├── schemas.py
├── security.py
├── utils.py
├── vector_store.py
│
├── routers/
│   ├── auth.py
│   ├── chat.py
│   └── document.py
│
└── services/
    ├── chat_service.py
    └── document_service.py

frontend/
├── app/
├── components/
├── lib/
└── pages/
```

### File Responsibilities

| File              | Responsibility                    |
| ----------------- | --------------------------------- |
| `config.py`       | Configuration & async clients     |
| `database.py`     | Database connection pool          |
| `main.py`         | FastAPI application entry         |
| `schemas.py`      | Pydantic models                   |
| `security.py`     | JWT & password hashing            |
| `utils.py`        | Utilities & middleware            |
| `vector_store.py` | Embedding storage & vector search |
| `routers/`        | API endpoints                     |
| `services/`       | Business logic                    |

---

## 4. Access the Services

| Service             | URL                               |
| ------------------- | --------------------------------- |
| Frontend (Full App) | https://ai-assistant.shabrandi.ir |
| API Docs (Swagger)  | https://api.shabrandi.ir/docs     |

---

# 🔒 Security

### Zero Hardcoded Secrets

All credentials, API keys, and secrets are loaded from environment variables.

The `.env` file should always be excluded from version control using `.gitignore`.

### Secure Authentication

- JWT Authentication
- HTTP-only Cookies
- Session Isolation

Using HTTP-only cookies significantly reduces the attack surface for XSS compared to storing tokens in local storage.

---

# 📄 License

This project is licensed under the **MIT License**.

Feel free to use, modify, and distribute it for personal or commercial projects.
