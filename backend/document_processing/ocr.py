import os
import pytesseract
from PIL import Image

# Common Windows install path fallback
DEFAULT_TESSERACT_WINDOWS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(DEFAULT_TESSERACT_WINDOWS_PATH):
    pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_WINDOWS_PATH


def is_ocr_available() -> bool:
    """Check if Tesseract binary is accessible."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_image_text(file_path: str) -> str:
    """
    Extract text from an image using OCR.

    Args:
        file_path (str): Path to the image.

    Returns:
        str: Text extracted from the image.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    try:
        with Image.open(file_path) as image:
            # Convert palette/RGBA if necessary
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            
            try:
                text = pytesseract.image_to_string(image)
                return text.strip()
            except pytesseract.TesseractNotFoundError:
                raise RuntimeError(
                    "Tesseract OCR engine is not installed or not configured in system PATH. "
                    "Install Tesseract-OCR to enable scanned document processing."
                )
    except RuntimeError:
        raise
    except Exception as e:
        raise Exception(f"Error performing OCR on image: {str(e)}")