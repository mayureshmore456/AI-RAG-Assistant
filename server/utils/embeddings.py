from google import genai
from server.config import EMBEDDING_MODEL


client = genai.Client()


def generate_embedding(document):
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=document.text,
        config={
            "output_dimensionality": 1536
        }
    )

    document.embedding = response.embeddings[0].values
    return document