import math


class VectorStore:
    """
    Stores Document objects and provides retrieval functionality.
    """

    def __init__(self):
        self.documents = []

    def add_documents(self, documents):
        self.documents.extend(documents)

    def get_documents(self):
        return self.documents

    def count(self):
        return len(self.documents)

    def cosine_similarity(self, vector1, vector2):
        """
        Calculate cosine similarity between two vectors.
        """

        dot_product = 0

        for a, b in zip(vector1, vector2):
            dot_product += a * b

        magnitude1 = 0

        for value in vector1:
            magnitude1 += value ** 2

        magnitude1 = math.sqrt(magnitude1)

        magnitude2 = 0

        for value in vector2:
            magnitude2 += value ** 2

        magnitude2 = math.sqrt(magnitude2)

        if magnitude1 == 0 or magnitude2 == 0:
            return 0

        return dot_product / (magnitude1 * magnitude2)

    def search(self, query_embedding, top_k=3):
        """
        Search for the most similar documents.

        Args:
            query_embedding (list)
            top_k (int)

        Returns:
            list
        """

        results = []

        # Compare query with every document
        for document in self.documents:

            similarity = self.cosine_similarity(
                query_embedding,
                document.embedding
            )

            results.append({
                "document": document,
                "score": similarity
            })

        # Sort from highest similarity to lowest
        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # Return only top K
        return results[:top_k]