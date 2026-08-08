import os

from dotenv import load_dotenv
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
# Process PDF
# -----------------------------

print("📄 Processing PDF...")

result = rag_service.process_pdf("sample.pdf")

print("✅ PDF Processed Successfully!")
print(f"📄 Pages: {result['total_pages']}")
print(f"📦 Chunks: {result['total_chunks']}")
print(f"📚 Documents: {result['total_documents']}")


# -----------------------------
# Ask Question
# -----------------------------

question = input("\n💬 Ask a question: ")


# -----------------------------
# Retrieve Relevant Documents
# -----------------------------

print("\n🔍 Searching documents...")

search_results = rag_service.retrieve(
    question=question,
    top_k=TOP_K
)

print(f"✅ Retrieved {len(search_results)} relevant chunks.")


# -----------------------------
# Build Prompt
# -----------------------------

prompt = build_prompt(
    question=question,
    search_results=search_results
)


# -----------------------------
# Generate Answer
# -----------------------------

print("\n🤖 Gemini is thinking...\n")

answer = llm_service.generate_answer(prompt)


# -----------------------------
# Display Answer
# -----------------------------

print("=" * 80)
print("🤖 AI ANSWER")
print("=" * 80)

print(answer)