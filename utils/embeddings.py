def generate_embeddings(client, documents, model="gemini-embedding-001"):
    """
    Generate embeddings for every document.

    Args:
        client: Gemini client.
        documents (list): List of Document objects.
        model (str): Embedding model.

    Returns:
        list: Updated Document objects.
    """

    print("\n🧠 Generating Embeddings...\n")

    for index, document in enumerate(documents):

        response = client.models.embed_content(
            model=model,
            contents=document.text
        )

        document.embedding = response.embeddings[0].values

        print(
            f"✅ Document {index + 1}/{len(documents)} embedded."
        )

    return documents