import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Database
# ----------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/ai_rag_assistant"
)

# ----------------------------
# Gemini
# ----------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ----------------------------
# Models
# ----------------------------

LLM_MODEL = "gemini-3.6-flash"

EMBEDDING_MODEL = "models/gemini-embedding-001"

# ----------------------------
# RAG
# ----------------------------

TOP_K = 5

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

# ----------------------------
# JWT
# ----------------------------

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-secret-change-this"
)