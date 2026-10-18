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
        "Termination",
        "Notice Period",
        "Company Property",
        "Dispute Resolution",
        "Important Dates and Conditions",
        "Acknowledgement",
        "Rent",
        "Monthly Rent",
        "Security Deposit",
        "Lease Period",
        "Term of Lease",
        "Premises",
        "Maintenance and Repairs",
        "Scope of Services",
        "Payment Terms",
        "Governing Law",
        "Indemnification"
    ]

    heading_pattern = "|".join(
        re.escape(h)
        for h in headings
    )

    pattern = re.compile(
        rf"(?<!\d)(?P<number>(?:[1-9]|[1-4][0-9]|50))\.\s+"
        rf"(?P<heading>{heading_pattern})\b",
        re.IGNORECASE
    )

    matches = list(pattern.finditer(text))

    for index, match in enumerate(matches):
        section_number = match.group("number")
        heading = match.group("heading").strip()
        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        content = text[start:end].strip()
        if not content:
            continue

        if heading.lower() == "acknowledgement":
            continue

        heading_lower = heading.lower()
        content_lower = content.lower()

        if heading_lower in {"employment", "working hours", "company property", "scope of services"}:
            clauses["obligations"].append(content)

        elif heading_lower in {"salary", "rent", "monthly rent", "payment terms"}:
            clauses["payment"].append(content)
            if "payable" in content_lower or "on or before" in content_lower or "due date" in content_lower:
                clauses["deadlines"].append(content)

        elif heading_lower in {"security deposit"}:
            clauses["payment"].append(content)
            if "refund" in content_lower or "within" in content_lower:
                clauses["rights"].append(content)
                clauses["deadlines"].append(content)

        elif heading_lower == "leave":
            clauses["rights"].append(content)
            clauses["leave"].append(content)
            if "days" in content_lower or "before" in content_lower or "in advance" in content_lower:
                clauses["deadlines"].append(content)

        elif heading_lower == "confidentiality":
            clauses["obligations"].append(content)
            clauses["confidentiality"].append(content)

        elif heading_lower in {"notice and termination", "termination", "notice period"}:
            clauses["rights"].append(content)
            clauses["termination"].append(content)
            if "days" in content_lower or "notice" in content_lower:
                clauses["deadlines"].append(content)

        elif heading_lower in {"dispute resolution", "governing law"}:
            clauses["dispute_resolution"].append(content)

        elif heading_lower in {"important dates and conditions", "lease period", "term of lease"}:
            clauses["deadlines"].append(content)

        elif heading_lower in {"maintenance and repairs", "premises", "indemnification"}:
            clauses["obligations"].append(content)

    # ---------------------------------------------------------
    # FALLBACK / SUPPLEMENTARY SENTENCE-LEVEL EXTRACTION
    #
    # If the document is not strictly divided into our standard
    # numbered headings, classify individual sentences so that
    # any valid legal document produces meaningful clauses.
    # ---------------------------------------------------------
    total_found = sum(len(items) for items in clauses.values())
    if total_found < 3:
        # Split text into candidate sentences
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
        for sentence in sentences:
            s_clean = sentence.strip()
            s_lower = s_clean.lower()
            if len(s_clean) < 20 or len(s_clean) > 500:
                continue

            # Rights
            if any(term in s_lower for term in [
                "is entitled to", "may request", "has the right", "entitled to receive",
                "shall have the option", "reserves the right", "may terminate", "eligible for"
            ]):
                if s_clean not in clauses["rights"]:
                    clauses["rights"].append(s_clean)

            # Obligations
            if any(term in s_lower for term in [
                "shall", "must", "is required to", "agrees to", "undertakes to",
                "will perform", "duty of", "responsible for", "obligated to"
            ]):
                if s_clean not in clauses["obligations"]:
                    clauses["obligations"].append(s_clean)

            # Deadlines
            if any(term in s_lower for term in [
                "on or before", "within", "prior to", "notice period", "days' notice",
                "days in advance", "due date", "deadline"
            ]) and any(w in s_lower for w in ["day", "days", "month", "date", "week"]):
                if s_clean not in clauses["deadlines"]:
                    clauses["deadlines"].append(s_clean)

            # Termination
            if any(term in s_lower for term in [
                "terminate", "termination", "cancellation of this", "discharge from", "end of employment"
            ]):
                if s_clean not in clauses["termination"]:
                    clauses["termination"].append(s_clean)

            # Confidentiality
            if any(term in s_lower for term in [
                "confidential", "non-public", "proprietary", "trade secret", "non-disclosure"
            ]):
                if s_clean not in clauses["confidentiality"]:
                    clauses["confidentiality"].append(s_clean)

            # Payment
            if any(term in s_lower for term in [
                "salary", "wages", "monthly rent", "security deposit", "payable", "compensation", "fee"
            ]):
                if s_clean not in clauses["payment"]:
                    clauses["payment"].append(s_clean)

            # Leave
            if any(term in s_lower for term in [
                "paid leave", "leave policy", "casual leave", "sick leave", "annual leave", "maternity"
            ]):
                if s_clean not in clauses["leave"]:
                    clauses["leave"].append(s_clean)

            # Dispute resolution
            if any(term in s_lower for term in [
                "dispute", "arbitration", "jurisdiction", "courts at", "amicable settlement"
            ]):
                if s_clean not in clauses["dispute_resolution"]:
                    clauses["dispute_resolution"].append(s_clean)

    return clauses