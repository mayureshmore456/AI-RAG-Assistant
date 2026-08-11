import fitz


def load_pdf(file_path):
    """
    Extract text from a PDF.

    Returns:
        text: Complete extracted text
        total_pages: Number of pages
    """

    document = fitz.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    total_pages = len(document)

    document.close()

    return text, total_pages