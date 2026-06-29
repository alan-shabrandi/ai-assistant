[![Swagger API Docs](https://img.shields.io/badge/Swagger-API_Docs-green?style=for-the-badge&logo=swagger)](https://ai-assistant-0tto.onrender.com/docs)

# 🚀 AI-Powered RAG Chat Assistant

### FastAPI + PostgreSQL (pgvector) + MinIO

A production-ready, fully asynchronous **Retrieval-Augmented Generation (RAG)** system that enables intelligent conversations over uploaded PDF documents.

Users can upload PDF files, which are automatically:

- Parsed
- Chunked
- Embedded
- Indexed into a vector database

The AI model (via **OpenRouter** or **Local Ollama**) then retrieves the most relevant context and streams accurate responses in real time.

This project emphasizes **Clean Architecture**, modularity, scalability, and high concurrency to demonstrate modern backend development best practices.

---

# ✨ Features

- ⚡ **Fully Asynchronous Architecture**
  - FastAPI
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
  - Protects against abuse and excessive LLM costs

- 🐳 **Dockerized Infrastructure**
  - FastAPI
  - PostgreSQL + pgvector
  - MinIO
  - One-command deployment

---

# 🛠️ Tech Stack

| Category         | Technology                                   |
| ---------------- | -------------------------------------------- |
| Backend          | FastAPI (Python 3.11+)                       |
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

# 🚀 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/alan-shabrandi/ai-assistant

cd ai-assistant
```

---

## 2. Configure Environment Variables

Create a `.env` file in the project root.

```env
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# PostgreSQL

POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb

DATABASE_URL=postgresql+psycopg://myuser:mypassword@db:5432/mydb

# OpenRouter

OPENROUTER_API_KEY=your_openrouter_api_key_here

# Ollama

OLLAMA_BASE_URL=http://host.docker.internal:11434

# MinIO

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

MINIO_BUCKET_NAME=pdf-bucket
```

---

## 3. Start the Infrastructure

```bash
docker-compose up --build
```

---

## 4. Access the Services

| Service       | URL                        |
| ------------- | -------------------------- |
| FastAPI       | http://localhost:8000      |
| Swagger UI    | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001      |

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
