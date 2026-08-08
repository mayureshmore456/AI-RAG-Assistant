from utils.pdf_loader import load_pdf
from utils.chunker import create_chunks
from utils.document_factory import create_documents
from utils.embeddings import generate_embeddings
from utils.vector_store import VectorStore

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL
)


class RAGService:
    """
    Coordinates the document processing and retrieval pipeline.
    """

    def __init__(self, client):
        self.client = client
        self.vector_store = VectorStore()

    def process_pdf(self, file_path):
        """
        Load a PDF, split it into chunks, create documents,
        generate embeddings, and store them.
        """

        text, total_pages = load_pdf(file_path)

        chunks = create_chunks(
            text=text,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP
        )

        documents = create_documents(
            chunks=chunks,
            source=file_path
        )

        documents = generate_embeddings(
            client=self.client,
            documents=documents
        )

        self.vector_store.add_documents(documents)

        return {
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "total_documents": len(documents)
        }

    def retrieve(self, question, top_k):
        """
        Generate an embedding for the user's question
        and retrieve the most relevant documents.
        """

        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=question
        )

        query_embedding = response.embeddings[0].values

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )