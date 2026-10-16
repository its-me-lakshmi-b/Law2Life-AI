from backend.document_processing.pdf_extractor import extract_pdf_text
from backend.nlp.preprocessing import preprocess_legal_text


# --------------------------------------------------
# PDF FILE
# --------------------------------------------------

pdf_path = "uploaded_documents/b8f2481f-51e7-4c20-a51a-695202baa06b.pdf"


# --------------------------------------------------
# EXTRACT TEXT
# --------------------------------------------------

print("\n========== EXTRACTING PDF ==========\n")

raw_text = extract_pdf_text(pdf_path)

print("PDF text extracted successfully.")


# --------------------------------------------------
# PREPROCESS TEXT
# --------------------------------------------------

print("\n========== PREPROCESSING TEXT ==========\n")

cleaned_text = preprocess_legal_text(raw_text)


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

print("\n========== CLEANED TEXT ==========\n")

print(cleaned_text)

print("\n========== PREPROCESSING COMPLETE ==========\n")