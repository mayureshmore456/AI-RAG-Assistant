from models.document import Document


def create_documents(chunks, source):
    """
    Convert text chunks into Document objects.

    Args:
        chunks (list): List of text chunks.
        source (str): Source PDF name.

    Returns:
        list: List of Document objects.
    """

    documents = []

    for index, chunk in enumerate(chunks):

        document = Document(
            id=index + 1,
            text=chunk,
            metadata={
                "source": source
            }
        )

        documents.append(document)

    return documents