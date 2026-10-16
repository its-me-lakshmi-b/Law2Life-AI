from backend.document_processing.pdf_extractor import extract_pdf_text


pdf_path = "uploaded_documents/b24aa6ef-e521-44a1-a65c-914c9d89ab82.pdf"

text = extract_pdf_text(pdf_path)

print("\n========== EXTRACTED TEXT ==========\n")
print(text)
print("\n========== END OF TEXT ==========\n")