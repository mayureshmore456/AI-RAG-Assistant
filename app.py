import os
from dotenv import load_dotenv
from google import genai

from utils.pdf_loader import load_pdf
from utils.chunker import create_chunks
from utils.document_factory import create_documents
from utils.embeddings import generate_embeddings
from utils.vector_store import VectorStore

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

print("\n🧠 Generating Question Embedding...")

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)

query_embedding = response.embeddings[0].values

print("✅ Question Embedded!")

# ==========================================================
# SEARCH
# ==========================================================

results = vector_store.search(
    query_embedding=query_embedding,
    top_k=3
)

# ==========================================================
# DISPLAY RESULTS
# ==========================================================

print("\n" + "=" * 80)
print("TOP MATCHING DOCUMENTS")
print("=" * 80)

for index, result in enumerate(results, start=1):

    document = result["document"]
    score = result["score"]

    print(f"\nResult #{index}")
    print(f"Similarity Score : {score:.4f}")
    print(f"Source           : {document.metadata['source']}")

    print("\nText Preview:\n")
    print(document.text[:300])
    print("-" * 80)