from backend.document_processing.pdf_extractor import extract_pdf_text
from backend.nlp.preprocessing import preprocess_legal_text
from backend.nlp.legal_classifier import classify_document


pdf_path = "uploaded_documents/b8f2481f-51e7-4c20-a51a-695202baa06b.pdf"


print("\n========== EXTRACTING PDF ==========\n")

raw_text = extract_pdf_text(pdf_path)

print("PDF text extracted successfully.")


print("\n========== PREPROCESSING ==========\n")

cleaned_text = preprocess_legal_text(raw_text)

print("Text preprocessing completed.")


print("\n========== DOCUMENT CLASSIFICATION ==========\n")

result = classify_document(cleaned_text)


print("Document Type:")
print(result["document_type"])


print("\nConfidence:")
print(result["confidence"])


print("\nMatched Keywords:")

for keyword in result["matched_keywords"]:
    print(f"- {keyword}")


print("\nAll Scores:")

for document_type, score in result["scores"].items():
    print(
        f"- {document_type}: {score}"
    )


print("\n========== CLASSIFICATION COMPLETE ==========\n")