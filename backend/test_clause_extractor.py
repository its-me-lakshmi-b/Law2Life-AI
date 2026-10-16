from backend.document_processing.pdf_extractor import extract_pdf_text
from backend.nlp.preprocessing import preprocess_legal_text
from backend.nlp.clause_extractor import extract_clauses


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
# PREPROCESS
# --------------------------------------------------

cleaned_text = preprocess_legal_text(raw_text)

print("Text preprocessing completed.")


# --------------------------------------------------
# CLAUSE EXTRACTION
# --------------------------------------------------

print("\n========== EXTRACTING LEGAL CLAUSES ==========\n")

clauses = extract_clauses(cleaned_text)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

for category, items in clauses.items():

    print(f"\n--- {category.upper()} ---")

    if items:

        for item in items:
            print(f"- {item}")

    else:

        print("No clauses detected.")


print("\n========== CLAUSE EXTRACTION COMPLETE ==========\n")