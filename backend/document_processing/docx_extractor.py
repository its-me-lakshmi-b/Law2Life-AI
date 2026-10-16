from docx import Document


def extract_docx_text(file_path):
    """
    Extract text from a DOCX document.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        str: Extracted text from the DOCX document.
    """

    text = ""

    try:
        document = Document(file_path)

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"

        return text.strip()

    except Exception as e:
        raise Exception(f"Error extracting DOCX text: {str(e)}")