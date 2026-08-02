from pypdf import PdfReader


def load_pdf(file_path):
    """
    Reads a PDF and returns all its text.

    Args:
        file_path (str): Path to the PDF.

    Returns:
        tuple:
            text (str): Complete extracted text.
            total_pages (int): Number of pages.
    """

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        extracted_text = page.extract_text()

        if extracted_text:
            text += extracted_text + "\n"

    return text, len(reader.pages)