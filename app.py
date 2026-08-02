import os
from dotenv import load_dotenv
from google import genai

from utils.pdf_reader import load_pdf
from utils.chunker import create_chunks

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

print("\n✅ Text Extracted Successfully!")

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
# Display Chunks
# -----------------------------
for index, chunk in enumerate(chunks):

    print(f"\n{'=' * 60}")
    print(f"Chunk {index + 1}")
    print(f"{'=' * 60}")

    print(chunk)