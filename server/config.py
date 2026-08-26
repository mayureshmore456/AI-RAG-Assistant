import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required."
    )


# =========================================================
# GEMINI
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is required."
    )


# =========================================================
# MODELS
# =========================================================

LLM_MODEL = "gemini-3.6-flash"

EMBEDDING_MODEL = "models/gemini-embedding-001"


# =========================================================
# RAG
# =========================================================

TOP_K = 5

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200


# =========================================================
# JWT
# =========================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is required."
    )

if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must be at least 32 characters long."
    )