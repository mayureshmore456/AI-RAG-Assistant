import os
import shutil

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File

from google import genai

from config import TOP_K
from services.rag_service import RAGService
from services.llm_service import LLMService
from utils.prompt_builder import build_prompt


# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()


# -----------------------------
# Create FastAPI Application
# -----------------------------

app = FastAPI(
    title="AI RAG Assistant",
    description="A Retrieval-Augmented Generation API",
    version="1.0.0"
)


# -----------------------------
# Create Gemini Client
# -----------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------
# Create Services
# -----------------------------

rag_service = RAGService(client)
llm_service = LLMService(client)


# -----------------------------
# Root Endpoint
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "AI RAG Assistant API is running!"
    }


# -----------------------------
# PDF Upload Endpoint
# -----------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Only allow PDF files
    if file.content_type != "application/pdf":
        return {
            "error": "Only PDF files are allowed."
        }

    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    # Save uploaded PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process PDF
    result = rag_service.process_pdf(file_path)

    return {
        "message": "PDF uploaded and processed successfully.",
        "filename": file.filename,
        "pages": result["total_pages"],
        "chunks": result["total_chunks"],
        "documents": result["total_documents"]
    }


# -----------------------------
# Chat Endpoint
# -----------------------------

@app.post("/chat")
def chat(question: str):

    search_results = rag_service.retrieve(
        question=question,
        top_k=TOP_K
    )

    prompt = build_prompt(
        question=question,
        search_results=search_results
    )

    answer = llm_service.generate_answer(prompt)

    return {
        "question": question,
        "answer": answer
    }