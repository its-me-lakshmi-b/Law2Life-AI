from backend.nlp.ner import (
    extract_entities,
    extract_legal_facts
)

print("NER module imported successfully.")


text = """
Employee Ananya Rao
Employer ABC Technologies Pvt. Ltd.
Position Data Analyst
Start Date 1 October 2026
Monthly Salary I45,000
Work Location Vellore, Tamil Nadu

6. Notice and Termination
Either party may terminate the employment by providing 30 days' written notice.

4. Leave
Leave requests should normally be submitted at least seven days before the intended leave date.
"""


print("\n========== ENTITIES ==========\n")

entities = extract_entities(text)

print(entities)


print("\n========== LEGAL FACTS ==========\n")

legal_facts = extract_legal_facts(text)

print(legal_facts)