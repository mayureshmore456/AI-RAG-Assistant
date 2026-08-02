from dataclasses import dataclass, field


@dataclass
class Document:
    """
    Represents one chunk of text and its metadata.
    """

    id: int
    text: str
    embedding: list[float] = field(default_factory=list)
    source: str = ""
    page: int = 0

