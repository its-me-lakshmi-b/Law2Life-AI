import re
import spacy


# --------------------------------------------------
# LOAD SPACY MODEL
# --------------------------------------------------

nlp = spacy.load("en_core_web_sm")


# --------------------------------------------------
# GENERIC ENTITY EXTRACTION
# --------------------------------------------------

def extract_entities(text):

    if not text:
        return []

    # Normalize whitespace so the NLP model receives
    # clean continuous text.
    normalized_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    doc = nlp(normalized_text)

    entities = []

    for entity in doc.ents:

        entities.append({
            "text": entity.text.strip(),
            "label": entity.label_
        })

    return entities


# --------------------------------------------------
# LEGAL FACT EXTRACTION
# --------------------------------------------------

def extract_legal_facts(text):

    facts = {
        "employee": None,
        "employer": None,
        "position": None,
        "start_date": None,
        "salary": None,
        "work_location": None,
        "notice_period": None,
        "leave_notice": None
    }

    if not text:
        return facts

    # Normalize whitespace
    normalized_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()


    # --------------------------------------------------
    # EMPLOYEE
    # --------------------------------------------------

    match = re.search(
        r"\bEmployee\s+(.+?)\s+Employer\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["employee"] = match.group(1).strip()


    # --------------------------------------------------
    # EMPLOYER
    # --------------------------------------------------

    match = re.search(
        r"\bEmployer\s+(.+?)\s+Position\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["employer"] = match.group(1).strip()


    # --------------------------------------------------
    # POSITION
    # --------------------------------------------------

    match = re.search(
        r"\bPosition\s+(.+?)\s+Start Date\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["position"] = match.group(1).strip()


    # --------------------------------------------------
    # START DATE
    # --------------------------------------------------

    match = re.search(
        r"\bStart Date\s+(.+?)\s+Monthly Salary\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["start_date"] = match.group(1).strip()


    # --------------------------------------------------
    # SALARY
    # --------------------------------------------------

    match = re.search(
        r"\bMonthly Salary\s+(.+?)\s+Work Location\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["salary"] = match.group(1).strip()


    # --------------------------------------------------
    # WORK LOCATION
    # --------------------------------------------------

    match = re.search(
        r"\bWork Location\s+(.+?)(?=\s+\d+\.\s+)",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["work_location"] = match.group(1).strip()

    # --------------------------------------------------
    # NOTICE PERIOD
    # --------------------------------------------------

    match = re.search(
        r"\bproviding\s+(\d+)\s+days['’]?\s+written\s+notice",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["notice_period"] = (
            match.group(1) + " days"
        )


    # --------------------------------------------------
    # LEAVE NOTICE
    # --------------------------------------------------

    match = re.search(
        r"\bat least\s+(\w+)\s+days\s+before\s+the intended leave",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        facts["leave_notice"] = (
            match.group(1) + " days"
        )


    return facts