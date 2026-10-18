import io
import os
import pymupdf
from PIL import Image

try:
    from backend.document_processing.ocr import is_ocr_available
    import pytesseract
except ImportError:
    is_ocr_available = lambda: False
    pytesseract = None


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from a PDF document, falling back to OCR for scanned pages if needed.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    text_parts = []

    try:
        document = pymupdf.open(file_path)

        if document.is_encrypted:
            # Try empty password
            if not document.authenticate(""):
                raise ValueError("PDF is encrypted and password-protected.")

        ocr_usable = is_ocr_available() if callable(is_ocr_available) else False

        for page_idx, page in enumerate(document):
            page_text = page.get_text() or ""
            
            # If page text is very sparse (< 25 chars) and page has images, try OCR fallback
            if len(page_text.strip()) < 25 and ocr_usable and pytesseract is not None:
                try:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text and len(ocr_text.strip()) > len(page_text.strip()):
                        page_text = ocr_text
                except Exception:
                    # Keep regular page text on OCR error
                    pass

            if page_text.strip():
                text_parts.append(page_text.strip())

        document.close()
        return "\n\n".join(text_parts).strip()

    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")