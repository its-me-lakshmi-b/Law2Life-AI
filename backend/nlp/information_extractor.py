import re


def extract_information(text):
    """
    Extract structured legal information from a document.

    This module combines document text patterns with
    context-specific legal information.

    Returns:
        dict containing structured information.
    """

    information = {
        "parties": {
            "employee": None,
            "employer": None
        },
        "role": None,
        "dates": {
            "start_date": None
        },
        "financial": {
            "salary": None
        },
        "location": None,
        "notice_period": None,
        "leave_notice": None,
        "working_hours": None
    }

    if not text:
        return information

    # ---------------------------------------------------------
    # Normalize whitespace
    # ---------------------------------------------------------

    normalized_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # ---------------------------------------------------------
    # Employee
    # ---------------------------------------------------------

    match = re.search(
        r"\bEmployee\s+([A-Z][A-Za-z. ]+?)\s+Employer\b",
        normalized_text
    )

    if match:
        information["parties"]["employee"] = (
            match.group(1).strip()
        )

    # ---------------------------------------------------------
    # Employer
    # ---------------------------------------------------------

    match = re.search(
        r"\bEmployer\s+(.+?)\s+Position\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["parties"]["employer"] = (
            match.group(1).strip()
        )

    # ---------------------------------------------------------
    # Position
    # ---------------------------------------------------------

    match = re.search(
        r"\bPosition\s+(.+?)\s+Start Date\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["role"] = (
            match.group(1).strip()
        )

    # ---------------------------------------------------------
    # Start Date
    # ---------------------------------------------------------

    match = re.search(
        r"\bStart Date\s+(.+?)\s+Monthly Salary\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["dates"]["start_date"] = (
            match.group(1).strip()
        )

    # ---------------------------------------------------------
    # Salary
    # ---------------------------------------------------------

    match = re.search(
        r"\bMonthly Salary\s+(.+?)\s+Work Location\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["financial"]["salary"] = (
            match.group(1).strip()
        )

    # ---------------------------------------------------------
    # Work Location
    # ---------------------------------------------------------

    match = re.search(
        r"\bWork Location\s+(.+?)\s+1\.\s+Employment\b",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["location"] = (
            match.group(1).strip()
        )

    # ---------------------------------------------------------
    # Notice Period
    # ---------------------------------------------------------

    match = re.search(
        r"\bproviding\s+(\d+)\s+days['’]?\s+written\s+notice",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["notice_period"] = (
            match.group(1) + " days"
        )

    # ---------------------------------------------------------
    # Leave Notice
    # ---------------------------------------------------------

    match = re.search(
        r"\bat least\s+(\w+)\s+days\s+before\s+the intended leave",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["leave_notice"] = (
            match.group(1) + " days"
        )

    # ---------------------------------------------------------
    # Working Hours
    # ---------------------------------------------------------

    match = re.search(
        r"\bMonday\s+to\s+Friday,\s*"
        r"(\d{1,2}:\d{2}\s*[AP]M)\s+to\s+"
        r"(\d{1,2}:\d{2}\s*[AP]M)",
        normalized_text,
        re.IGNORECASE
    )

    if match:
        information["working_hours"] = (
            f"Monday to Friday, "
            f"{match.group(1)} to {match.group(2)}"
        )

    return information