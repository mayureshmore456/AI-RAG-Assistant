from server.config import EMBEDDING_MODEL


def generate_embeddings(client, documents):
    """
    Generate embeddings for all documents.
    """

    for document in documents:

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=document.text
        )

        document.embedding = response.embeddings[0].values

    return documents