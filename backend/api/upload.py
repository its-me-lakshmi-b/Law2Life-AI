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

    # Sanitize filename to prevent directory traversal
    safe_original_name = os.path.basename(file.filename)
    
    extension = os.path.splitext(safe_original_name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload PDF, DOCX, PNG, JPG or JPEG."
            )
        )

    # Maximum file size 15 MB
    MAX_FILE_SIZE = 15 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of 15 MB."
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

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

    doc_id = str(uuid.uuid4())
    try:
        from backend.database.models import save_uploaded_document
        doc_id = save_uploaded_document(
            original_filename=safe_original_name,
            stored_filepath=file_path,
            file_type=extension,
            file_size_bytes=len(contents),
            document_type=classification.get("document_type", "unknown")
        )
    except Exception:
        pass

    return {
        "status": "success",
        "message": "Document uploaded and analyzed successfully.",
        "document_id": doc_id,
        "document_name": safe_original_name,
        "stored_file": file_path,
        "file_type": extension,
        "extracted_text": extracted_text,
        "document_type": classification["document_type"],
        "classification": classification
    }