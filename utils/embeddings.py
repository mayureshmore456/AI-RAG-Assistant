from google import genai


def generate_embeddings(client, chunks, model="gemini-embedding-001"):
    """
    Generate embeddings for a list of text chunks.

    Args:
        client: Gemini client.
        chunks (list): List of text chunks.
        model (str): Embedding model.

    Returns:
        list: List of embeddings.
    """

    embeddings = []

    print("\nGenerating embeddings...\n")

    for index, chunk in enumerate(chunks):

        response = client.models.embed_content(
            model=model,
            contents=chunk
        )

        embeddings.append(response.embeddings[0].values)

        print(f"Processed Chunk {index + 1}/{len(chunks)}")

    return embeddings