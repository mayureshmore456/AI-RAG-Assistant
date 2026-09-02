import os
import uuid

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from google import genai

from server.config import TOP_K

from server.services.rag_service import RAGService
from server.services.llm_service import LLMService
from server.services.user_service import UserService
from server.services.auth_service import AuthService
from server.services.chat_service import ChatService
from server.services.document_service import DocumentService

from server.utils.auth import get_current_user
from server.utils.prompt_builder import build_prompt


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI RAG Assistant",
    description="A Retrieval-Augmented Generation API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-rag-assistant.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================================================
# SERVICES
# =========================================================

rag_service = RAGService(client)

llm_service = LLMService(client)

user_service = UserService()

auth_service = AuthService()

chat_service = ChatService()

document_service = DocumentService()


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateChatRequest(BaseModel):
    title: str = "New Chat"


class UpdateChatTitleRequest(BaseModel):
    title: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "AI RAG Assistant API is running!"
    }


# =========================================================
# REGISTER
# =========================================================

@app.post("/auth/register")
def register(request: RegisterRequest):

    existing_user = user_service.get_user_by_email(
        request.email
    )

    if existing_user is not None:

        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    user = user_service.create_user(
        name=request.name,
        email=request.email,
        password=request.password
    )

    return {
        "message": "Registration successful.",
        "user": user
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/auth/login")
def login(request: LoginRequest):

    user = user_service.authenticate_user(
        email=request.email,
        password=request.password
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    access_token = auth_service.create_access_token(
        user_id=user["id"]
    )

    return {
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get("/auth/me")
def get_me(
    user_id: str = Depends(get_current_user)
):

    return {
        "user_id": user_id
    }


# =========================================================
# CREATE CHAT
# =========================================================

@app.post("/chats")
def create_chat(
    request: CreateChatRequest,
    user_id: str = Depends(get_current_user)
):

    chat = chat_service.create_chat(
        user_id=user_id,
        title=request.title
    )

    return chat


# =========================================================
# GET USER CHATS
# =========================================================

@app.get("/chats")
def get_chats(
    user_id: str = Depends(get_current_user)
):

    chats = chat_service.get_chats(
        user_id=user_id
    )

    return {
        "chats": chats
    }


# =========================================================
# GET CHAT MESSAGES
# =========================================================

@app.get("/chats/{chat_id}")
def get_chat_messages(
    chat_id: str,
    user_id: str = Depends(get_current_user)
):

    chat = chat_service.get_chat(
        chat_id
    )

    if chat is None:

        raise HTTPException(
            status_code=404,
            detail="Chat not found."
        )

    if chat["user_id"] != user_id:

        raise HTTPException(
            status_code=403,
            detail="You do not have access to this chat."
        )

    messages = chat_service.get_messages(
        chat_id
    )

    return {
        "chat": chat,
        "messages": messages
    }


# =========================================================
# UPDATE CHAT TITLE
# =========================================================

@app.patch("/chats/{chat_id}/title")
def update_chat_title(
    chat_id: str,
    request: UpdateChatTitleRequest,
    user_id: str = Depends(get_current_user)
):

    chat = chat_service.get_chat(
        chat_id
    )

    if chat is None:

        raise HTTPException(
            status_code=404,
            detail="Chat not found."
        )

    if chat["user_id"] != user_id:

        raise HTTPException(
            status_code=403,
            detail="You do not have access to this chat."
        )

    title = request.title.strip()

    if not title:

        raise HTTPException(
            status_code=400,
            detail="Chat title cannot be empty."
        )

    if len(title) > 100:

        title = title[:100]

    updated_chat = chat_service.update_chat_title(
        chat_id=chat_id,
        title=title
    )

    return updated_chat


# =========================================================
# PDF UPLOAD
# =========================================================

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):

    # =====================================================
    # VALIDATE FILE TYPE
    # =====================================================

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # =====================================================
    # VALIDATE FILENAME
    # =====================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="A filename is required."
        )

    original_filename = os.path.basename(
        file.filename
    )

    if not original_filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # =====================================================
    # CREATE UPLOAD DIRECTORY
    # =====================================================

    upload_directory = "uploads"

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    # =====================================================
    # GENERATE SAFE SERVER-SIDE FILENAME
    # =====================================================

    stored_filename = (
        f"{uuid.uuid4()}.pdf"
    )

    file_path = os.path.join(
        upload_directory,
        stored_filename
    )

    # =====================================================
    # SAVE FILE WITH SIZE LIMIT
    # =====================================================

    total_size = 0

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "PDF file is too large. "
                            "Maximum size is 10 MB."
                        )
                    )

                buffer.write(chunk)

    except HTTPException:

        if os.path.exists(file_path):

            try:
                os.remove(file_path)

            except OSError:
                pass

        raise

    except Exception as error:

        if os.path.exists(file_path):

            try:
                os.remove(file_path)

            except OSError:
                pass

        print(
            f"File upload error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file."
        )

    finally:

        await file.close()

    # =====================================================
    # PROCESS PDF
    # =====================================================

    try:

        result = rag_service.process_pdf(
            file_path=file_path,
            user_id=user_id
        )

    except Exception as error:

        if os.path.exists(file_path):

            try:
                os.remove(file_path)

            except OSError:
                pass

        print(
            f"PDF processing error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process PDF."
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "message": (
            "PDF uploaded and processed successfully."
        ),
        "filename": original_filename,
        "pages": result["total_pages"],
        "chunks": result["total_chunks"],
        "documents": result["total_documents"]
    }


# =========================================================
# GET USER DOCUMENTS
# =========================================================

@app.get("/documents")
def get_documents(
    user_id: str = Depends(get_current_user)
):

    documents = document_service.get_user_documents(
        user_id=user_id
    )

    return {
        "documents": documents
    }


# =========================================================
# GET SINGLE DOCUMENT
# =========================================================

@app.get("/documents/{document_id}")
def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user)
):

    document = document_service.get_document(
        document_id=document_id,
        user_id=user_id
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "document": document
    }


# =========================================================
# DELETE DOCUMENT
# =========================================================

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user)
):

    document = document_service.delete_document(
        document_id=document_id,
        user_id=user_id
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully.",
        "document": document
    }


# =========================================================
# CHAT / RAG
# =========================================================

@app.post("/chat")
def chat(
    question: str,
    chat_id: str = None,
    user_id: str = Depends(get_current_user)
):

    # =====================================================
    # VERIFY CHAT OWNERSHIP
    # =====================================================

    if chat_id is not None:

        existing_chat = chat_service.get_chat(
            chat_id
        )

        if existing_chat is None:

            raise HTTPException(
                status_code=404,
                detail="Chat not found."
            )

        if existing_chat["user_id"] != user_id:

            raise HTTPException(
                status_code=403,
                detail="You do not have access to this chat."
            )

    # =====================================================
    # RETRIEVE USER DOCUMENTS
    # =====================================================

    try:

        search_results = rag_service.retrieve(
            question=question,
            top_k=TOP_K,
            user_id=user_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            f"RAG retrieval error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve relevant documents."
        )

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = build_prompt(
        question=question,
        search_results=search_results
    )

    # =====================================================
    # GENERATE AI ANSWER
    # =====================================================

    try:

        answer = llm_service.generate_answer(
            prompt
        )

    except Exception as error:

        print(
            f"LLM generation error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI response."
        )

    # =====================================================
    # SAVE MESSAGES
    # =====================================================

    saved_user_message = None

    saved_assistant_message = None

    if chat_id is not None:

        saved_user_message = chat_service.save_message(
            chat_id=chat_id,
            role="user",
            content=question
        )

        saved_assistant_message = chat_service.save_message(
            chat_id=chat_id,
            role="assistant",
            content=answer
        )

    # =====================================================
    # BUILD SOURCE INFORMATION
    # =====================================================

    sources = []

    for result in search_results:

        document = result["document"]

        metadata = document.metadata or {}

        sources.append(
            {
                "document_id": metadata.get(
                    "document_id"
                ),
                "filename": metadata.get(
                    "filename",
                    "Uploaded document"
                ),
                "chunk_id": metadata.get(
                    "chunk_id"
                ),
                "chunk_index": metadata.get(
                    "chunk_index"
                ),
                "score": round(
                    result.get("score", 0),
                    3
                )
            }
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "question": question,
        "answer": answer,
        "chat_id": chat_id,
        "user_message": saved_user_message,
        "assistant_message": saved_assistant_message,
        "sources": sources
    }