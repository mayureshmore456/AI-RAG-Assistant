import math

from server.models.document import Document


class VectorStore:
    """
    In-memory vector store for semantic search.
    """

    def __init__(self):
        self.documents = []

    # -----------------------------
    # Add Documents
    # -----------------------------

    def add_documents(self, documents):
        self.documents.extend(documents)

    # -----------------------------
    # Count Documents
    # -----------------------------

    def count(self):
        return len(self.documents)

    # -----------------------------
    # Cosine Similarity
    # -----------------------------

    def cosine_similarity(self, vector_a, vector_b):

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(
            sum(a * a for a in vector_a)
        )

        magnitude_b = math.sqrt(
            sum(b * b for b in vector_b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0

        return dot_product / (
            magnitude_a * magnitude_b
        )

    # -----------------------------
    # Search
    # -----------------------------

    def search(self, query_embedding, top_k=3):

        results = []

        for document in self.documents:

            score = self.cosine_similarity(
                query_embedding,
                document.embedding
            )

            results.append({
                "document": document,
                "score": score
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]