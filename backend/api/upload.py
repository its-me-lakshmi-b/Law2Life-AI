import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.document_processing.pdf_extractor import extract_pdf_text
from backend.document_processing.docx_extractor import extract_docx_text
from backend.document_processing.ocr import extract_image_text
from backend.nlp.legal_classifier import classify_document

router = APIRouter()


UPLOAD_DIR = "uploaded_documents"

os.makedirs(UPLOAD_DIR, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg"
}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload PDF, DOCX, PNG, JPG or JPEG."
            )
        )

    unique_name = str(uuid.uuid4()) + extension

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )

    contents = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    try:

        if extension == ".pdf":

            extracted_text = extract_pdf_text(
                file_path
            )

        elif extension == ".docx":

            extracted_text = extract_docx_text(
                file_path
            )

        elif extension in {".png", ".jpg", ".jpeg"}:

            extracted_text = extract_image_text(
                file_path
            )

        else:

            extracted_text = ""

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    if not extracted_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "The document was uploaded, "
                "but no text could be extracted."
            )
        )

    classification = classify_document(
        extracted_text
    )

    return {
        "status": "success",
        "message": "Document uploaded and analyzed successfully.",
        "document_name": file.filename,
        "stored_file": file_path,
        "file_type": extension,
        "extracted_text": extracted_text,
        "document_type": classification["document_type"],
        "classification": classification
    }