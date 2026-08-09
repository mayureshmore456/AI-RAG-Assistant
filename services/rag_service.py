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
    Handles document ingestion and retrieval.
    """

    def __init__(self, client):
        self.client = client
        self.vector_store = VectorStore()
        self.documents_loaded = False

    def process_pdf(self, file_path):
        """
        Process a PDF and store its embeddings.

        This should happen when a document is uploaded,
        not every time the user asks a question.
        """

        print("\n📄 Processing PDF...")

        text, total_pages = load_pdf(file_path)

        chunks = create_chunks(
            text=text,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP
        )

        print(f"📦 Created {len(chunks)} chunks.")

        documents = create_documents(
            chunks=chunks,
            source=file_path
        )

        print("🧠 Generating document embeddings...")

        documents = generate_embeddings(
            client=self.client,
            documents=documents
        )

        self.vector_store.add_documents(documents)

        self.documents_loaded = True

        print("✅ Document embeddings stored.")

        return {
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "total_documents": len(documents)
        }

    def retrieve(self, question, top_k):
        """
        Retrieve relevant documents for a question.

        Document embeddings already exist in the vector store.
        Only the question needs a new embedding.
        """

        if not self.documents_loaded:
            raise ValueError(
                "No documents have been loaded into the vector store."
            )

        print("\n🧠 Generating question embedding...")

        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=question
        )

        query_embedding = response.embeddings[0].values

        print("🔍 Searching vector store...")

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        return results