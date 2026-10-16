from backend.document_processing.pdf_extractor import extract_pdf_text
from backend.nlp.preprocessing import preprocess_legal_text
from backend.nlp.information_extractor import extract_information


pdf_path = "uploaded_documents/b8f2481f-51e7-4c20-a51a-695202baa06b.pdf"


print("\n========== EXTRACTING PDF ==========\n")

raw_text = extract_pdf_text(pdf_path)

print("PDF text extracted successfully.")


print("\n========== PREPROCESSING ==========\n")

cleaned_text = preprocess_legal_text(raw_text)

print("Text preprocessing completed.")


print("\n========== INFORMATION EXTRACTION ==========\n")

information = extract_information(cleaned_text)


print("PARTIES")
print("Employee:", information["parties"]["employee"])
print("Employer:", information["parties"]["employer"])


print("\nROLE")
print("Position:", information["role"])


print("\nDATES")
print(
    "Start Date:",
    information["dates"]["start_date"]
)


print("\nFINANCIAL")
print(
    "Salary:",
    information["financial"]["salary"]
)


print("\nLOCATION")
print(
    "Work Location:",
    information["location"]
)


print("\nNOTICE")
print(
    "Notice Period:",
    information["notice_period"]
)


print("\nLEAVE")
print(
    "Leave Notice:",
    information["leave_notice"]
)


print("\nWORKING HOURS")
print(
    "Working Hours:",
    information["working_hours"]
)


print("\n========== INFORMATION EXTRACTION COMPLETE ==========\n")