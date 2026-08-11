class Document:
    """
    Represents a document chunk and its embedding.
    """

    def __init__(
        self,
        text,
        metadata=None,
        embedding=None
    ):
        self.text = text
        self.metadata = metadata or {}
        self.embedding = embedding