import os
from dotenv import load_dotenv
from google import genai

from utils.pdf_loader import load_pdf
from utils.chunker import create_chunks
from utils.document_factory import create_documents
from utils.embeddings import generate_embeddings
from utils.vector_store import VectorStore
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
# Load PDF
# -----------------------------
text, total_pages = load_pdf("sample.pdf")

print("✅ PDF Loaded Successfully!")
print(f"📄 Total Pages: {total_pages}")

# -----------------------------
# Chunk Text
# -----------------------------
chunks = create_chunks(
    text=text,
    chunk_size=500,
    overlap=100
)

print(f"\n📦 Total Chunks: {len(chunks)}")

# -----------------------------
# Create Documents
# -----------------------------
documents = create_documents(
    chunks=chunks,
    source="sample.pdf"
)

# -----------------------------
# Generate Document Embeddings
# -----------------------------
documents = generate_embeddings(
    client=client,
    documents=documents
)

print("\n✅ Document Embeddings Generated!")

# -----------------------------
# Create Vector Store
# -----------------------------
vector_store = VectorStore()
vector_store.add_documents(documents)

print(f"📚 Vector Store contains {vector_store.count()} documents.")

# ==========================================================
# USER QUESTION
# ==========================================================

question = input("\n💬 Ask a question: ")

# -----------------------------
# Generate Question Embedding
# -----------------------------
print("\n🧠 Generating Question Embedding...")

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)

query_embedding = response.embeddings[0].values

print("✅ Question Embedding Generated!")

# -----------------------------
# Retrieve Relevant Documents
# -----------------------------
search_results = vector_store.search(
    query_embedding=query_embedding,
    top_k=3
)

print("✅ Retrieved Top 3 Relevant Chunks!")

# -----------------------------
# Build Prompt
# -----------------------------
prompt = build_prompt(
    question=question,
    search_results=search_results
)

# -----------------------------
# Generate AI Answer
# -----------------------------
print("\n🤖 Gemini is thinking...\n")

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)

print("=" * 80)
print("🤖 AI ANSWER")
print("=" * 80)

print(response.text)