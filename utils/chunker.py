def create_chunks(text, chunk_size=500, overlap=100):
    """
    Split text into overlapping chunks without cutting words.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        if end < len(text):

            while end < len(text) and text[end] != " ":
                end += 1

        chunk = text[start:end].strip()

        chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

    return chunks