from backend.document_processing.pdf_extractor import extract_pdf_text
from backend.nlp.preprocessing import preprocess_legal_text
from backend.nlp.ner import extract_entities, extract_legal_facts


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

cleaned_text = preprocess_legal_text(raw_text)

print("Text preprocessing completed.")


# --------------------------------------------------
# GENERAL NER
# --------------------------------------------------

print("\n========== GENERAL NER ==========\n")

entities = extract_entities(cleaned_text)

for entity in entities:
    print(
        f"Entity: {entity['text']} "
        f"| Type: {entity['label']}"
    )


# --------------------------------------------------
# LEGAL FACT EXTRACTION
# --------------------------------------------------

print("\n========== LEGAL FACTS ==========\n")

legal_facts = extract_legal_facts(cleaned_text)

for key, value in legal_facts.items():

    print(
        f"{key}: {value}"
    )


# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n========== NER TEST COMPLETE ==========\n")