import os

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

    # Make sure the chat belongs to
    # the logged-in user

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
# PDF UPLOAD
# =========================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):

    # --------------------------------
    # Validate file type
    # --------------------------------

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # --------------------------------
    # Create uploads directory
    # --------------------------------

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    # --------------------------------
    # Create file path
    # --------------------------------

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    # --------------------------------
    # Save uploaded PDF
    # --------------------------------

    with open(
        file_path,
        "wb"
    ) as buffer:

        content = await file.read()

        buffer.write(content)

    # --------------------------------
    # Process PDF
    #
    # IMPORTANT:
    # Pass logged-in user's ID
    # --------------------------------

    result = rag_service.process_pdf(
        file_path=file_path,
        user_id=user_id
    )

    return {
        "message": "PDF uploaded and processed successfully.",
        "filename": file.filename,
        "pages": result["total_pages"],
        "chunks": result["total_chunks"],
        "documents": result["total_documents"]
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
    # RETRIEVE USER'S DOCUMENT CHUNKS
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

    answer = llm_service.generate_answer(
        prompt
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
    # RESPONSE
    # =====================================================

    return {
        "question": question,
        "answer": answer,
        "chat_id": chat_id,
        "user_message": saved_user_message,
        "assistant_message": saved_assistant_message
    }