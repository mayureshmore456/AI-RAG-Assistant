from dataclasses import dataclass, field


@dataclass
class Document:
    """
    Represents one document chunk and its metadata.
    """

    id: int
    text: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)