import os
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

reader = PdfReader("sample.pdf")

text = ""

for page in reader.pages:
    text += page.extract_text()

print("PDF Loaded Successfully!")
print("Total Pages:", len(reader.pages))
print("\n================ PDF TEXT ================\n")
print(text)