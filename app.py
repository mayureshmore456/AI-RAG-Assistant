import os
from dotenv import load_dotenv
from google import genai

from utils.pdf_loader import load_pdf
from utils.chunker import create_chunks
from utils.document_factory import create_documents
from utils.embeddings import generate_embeddings

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

print("✅ Documents Created Successfully!")

# -----------------------------
# Generate Embeddings
# -----------------------------
documents = generate_embeddings(
    client=client,
    documents=documents
)

print("\n🎉 Embeddings Generated Successfully!")

# -----------------------------
# Display First Document
# -----------------------------
first_document = documents[0]

print("\n" + "=" * 70)
print("FIRST DOCUMENT")
print("=" * 70)

print(f"\nID : {first_document.id}")

print("\nMetadata:")
print(first_document.metadata)

print("\nText:")
print(first_document.text[:250], "...")

print("\nEmbedding Length:")
print(len(first_document.embedding))

print("\nFirst 10 Values:")
print(first_document.embedding[:10])