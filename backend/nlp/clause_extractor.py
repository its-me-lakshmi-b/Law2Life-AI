import re


def extract_clauses(text):
    """
    Extract important legal clauses from a preprocessed document.

    Sections are located using their known legal headings.
    This avoids treating numbers inside dates such as
    '1 October 2026' as section boundaries.
    """

    clauses = {
        "rights": [],
        "obligations": [],
        "deadlines": [],
        "termination": [],
        "confidentiality": [],
        "payment": [],
        "leave": [],
        "dispute_resolution": []
    }

    if not text:
        return clauses

    # ---------------------------------------------------------
    # Legal section headings
    # ---------------------------------------------------------

    headings = [
        "Employment",
        "Working Hours",
        "Salary",
        "Leave",
        "Confidentiality",
        "Notice and Termination",
        "Company Property",
        "Dispute Resolution",
        "Important Dates and Conditions",
        "Acknowledgement"
    ]

    # ---------------------------------------------------------
    # Find every numbered section heading.
    #
    # Example:
    #
    # 9. Important Dates and Conditions
    #
    # The number MUST be followed by one of our known headings.
    # ---------------------------------------------------------

    heading_pattern = "|".join(
        re.escape(h)
        for h in headings
    )

    pattern = re.compile(
        rf"(?<!\d)(?P<number>(?:[1-9]|10))\.\s+"
        rf"(?P<heading>{heading_pattern})\b",
        re.IGNORECASE
    )

    matches = list(pattern.finditer(text))

    # ---------------------------------------------------------
    # Extract each section using character positions.
    # ---------------------------------------------------------

    for index, match in enumerate(matches):

        section_number = match.group("number")
        heading = match.group("heading").strip()

        start = match.end()

        # End at the beginning of the next recognized section.
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        content = text[start:end].strip()

        if not content:
            continue

        # -----------------------------------------------------
        # Ignore acknowledgement
        # -----------------------------------------------------

        if heading.lower() == "acknowledgement":
            continue

        heading_lower = heading.lower()
        content_lower = content.lower()

        # -----------------------------------------------------
        # EMPLOYMENT
        # -----------------------------------------------------

        if heading_lower == "employment":

            clauses["obligations"].append(content)

        # -----------------------------------------------------
        # WORKING HOURS
        # -----------------------------------------------------

        elif heading_lower == "working hours":

            clauses["obligations"].append(content)

        # -----------------------------------------------------
        # SALARY
        # -----------------------------------------------------

        elif heading_lower == "salary":

            clauses["payment"].append(content)

            if (
                "payable" in content_lower
                or "on or before" in content_lower
            ):
                clauses["deadlines"].append(content)

        # -----------------------------------------------------
        # LEAVE
        # -----------------------------------------------------

        elif heading_lower == "leave":

            clauses["rights"].append(content)
            clauses["leave"].append(content)

            if (
                "days" in content_lower
                or "before" in content_lower
                or "in advance" in content_lower
            ):
                clauses["deadlines"].append(content)

        # -----------------------------------------------------
        # CONFIDENTIALITY
        # -----------------------------------------------------

        elif heading_lower == "confidentiality":

            clauses["obligations"].append(content)
            clauses["confidentiality"].append(content)

        # -----------------------------------------------------
        # NOTICE AND TERMINATION
        # -----------------------------------------------------

        elif heading_lower == "notice and termination":

            clauses["rights"].append(content)
            clauses["termination"].append(content)

            if (
                "days" in content_lower
                or "notice" in content_lower
            ):
                clauses["deadlines"].append(content)

        # -----------------------------------------------------
        # COMPANY PROPERTY
        # -----------------------------------------------------

        elif heading_lower == "company property":

            clauses["obligations"].append(content)

        # -----------------------------------------------------
        # DISPUTE RESOLUTION
        # -----------------------------------------------------

        elif heading_lower == "dispute resolution":

            clauses["dispute_resolution"].append(content)

        # -----------------------------------------------------
        # IMPORTANT DATES AND CONDITIONS
        # -----------------------------------------------------

        elif heading_lower == "important dates and conditions":

            clauses["deadlines"].append(content)

    return clauses