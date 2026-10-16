import pytesseract
from PIL import Image


def extract_image_text(file_path):
    """
    Extract text from an image using OCR.

    Args:
        file_path (str): Path to the image.

    Returns:
        str: Text extracted from the image.
    """

    try:
        image = Image.open(file_path)

        text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        raise Exception(f"Error performing OCR: {str(e)}")