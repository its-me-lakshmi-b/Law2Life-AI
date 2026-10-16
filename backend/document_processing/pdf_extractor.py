import pymupdf


def extract_pdf_text(file_path):
    """
    Extract text from a PDF document.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """

    text = ""

    try:
        document = pymupdf.open(file_path)

        for page in document:
            page_text = page.get_text()
            text += page_text + "\n"

        document.close()

        return text.strip()

    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")