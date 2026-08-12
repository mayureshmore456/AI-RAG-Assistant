from server.utils.pdf_loader import load_pdf
from server.utils.chunker import create_chunks
from server.utils.document_factory import create_documents
from server.utils.embeddings import generate_embeddings

from server.services.pgvector_service import PGVectorService

from server.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL
)


class RAGService:
    """
    Handles document ingestion and retrieval
    using PostgreSQL + pgvector.
    """

    def __init__(self, client):
        self.client = client

        # PostgreSQL + pgvector
        self.vector_store = PGVectorService()

    # --------------------------------
    # Process PDF
    # --------------------------------

    def process_pdf(self, file_path, user_id):

        print("\nProcessing PDF...")

        # 1. Load PDF
        text, total_pages = load_pdf(file_path)

        # 2. Create chunks
        chunks = create_chunks(
            text=text,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP
        )

        print(f"Created {len(chunks)} chunks.")

        # 3. Convert chunks into Document objects
        documents = create_documents(
            chunks=chunks,
            source=file_path
        )

        # 4. Generate embeddings
        print("Generating document embeddings...")

        documents = generate_embeddings(
            client=self.client,
            documents=documents
        )

        # 5. Store embeddings for this user
        print("Storing embeddings in PostgreSQL...")

        self.vector_store.add_documents(
            documents=documents,
            source=file_path,
            user_id=user_id
        )

        print("Document embeddings stored.")

        return {
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "total_documents": len(documents)
        }

    # --------------------------------
    # Retrieve Relevant Documents
    # --------------------------------

    def retrieve(self, question, top_k, user_id):

        # Check whether THIS USER has documents
        if self.vector_store.count(user_id) == 0:

            raise ValueError(
                "No documents are available. "
                "Please upload a PDF first."
            )

        print("\nGenerating question embedding...")

        # Generate embedding for user's question
        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=question
        )

        query_embedding = response.embeddings[0].values

        # Search only this user's documents
        print("Searching user's documents...")

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            user_id=user_id
        )