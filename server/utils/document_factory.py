from server.models.document import Document


def create_documents(chunks, source):
    """
    Convert chunks into Document objects.
    """

    documents = []

    for index, chunk in enumerate(chunks):

        document = Document(
            text=chunk,
            metadata={
                "source": source,
                "chunk_id": index
            }
        )

        documents.append(document)

    return documents