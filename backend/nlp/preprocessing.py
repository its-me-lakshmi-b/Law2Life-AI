import re


def preprocess_legal_text(text):
    """
    Clean and normalize extracted legal document text.

    The preprocessing:
    - Normalizes PDF line breaks
    - Joins lines belonging to the same sentence
    - Restores numbered legal section boundaries
    - Preserves dates, amounts and deadlines
    - Preserves important legal headings
    """

    if not text:
        return ""

    # ---------------------------------------------------------
    # 1. Normalize line endings
    # ---------------------------------------------------------
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # ---------------------------------------------------------
    # 2. Normalize spaces and tabs
    # ---------------------------------------------------------
    text = re.sub(r"[ \t]+", " ", text)

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    # ---------------------------------------------------------
    # 3. Join PDF-wrapped lines
    # ---------------------------------------------------------

    joined_lines = []

    for line in lines:

        if not joined_lines:
            joined_lines.append(line)
            continue

        previous = joined_lines[-1]

        # Keep existing numbered sections separate
        if re.match(r"^(?:[1-9]|10)\.\s+", line):
            joined_lines.append(line)
            continue

        # Keep common headings separate
        headings = {
            "employment agreement",
            "employee details",
            "employer details",
            "salary",
            "working hours",
            "leave",
            "confidentiality",
            "notice and termination",
            "company property",
            "dispute resolution",
            "important dates and conditions",
            "acknowledgement"
        }

        if line.lower().strip(":") in headings:
            joined_lines.append(line)
            continue

        # If previous line already ends a sentence,
        # keep the new line separate.
        if re.search(r"[.!?:;]$", previous):
            joined_lines.append(line)
            continue

        # Bullets remain separate
        if re.match(r"^[-•*]\s+", line):
            joined_lines.append(line)
            continue

        # Otherwise join the PDF-wrapped line.
        joined_lines[-1] = previous + " " + line

    text = "\n".join(joined_lines)

    # ---------------------------------------------------------
    # 4. Restore numbered legal section boundaries
    #
    # Prevents years like '2026. Salary' from being treated
    # as section numbers, while supporting clauses across
    # employment, rental, service, and commercial agreements.
    # ---------------------------------------------------------

    legal_headings = (
        r"Employment|"
        r"Working Hours|"
        r"Salary|"
        r"Leave|"
        r"Confidentiality|"
        r"Notice and Termination|"
        r"Termination|"
        r"Notice Period|"
        r"Company Property|"
        r"Dispute Resolution|"
        r"Important Dates and Conditions|"
        r"Acknowledgement|"
        r"Rent|"
        r"Monthly Rent|"
        r"Security Deposit|"
        r"Deposit|"
        r"Lease Period|"
        r"Term of Lease|"
        r"Premises|"
        r"Maintenance and Repairs|"
        r"Utilities|"
        r"Scope of Services|"
        r"Payment Terms|"
        r"Governing Law|"
        r"Indemnification|"
        r"Indemnity|"
        r"Severability"
    )

    section_boundary_pattern = (
        rf"\s+(?=(?:[1-9]|[1-4][0-9]|50)\.\s+(?:{legal_headings})\b)"
    )

    text = re.sub(
        section_boundary_pattern,
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # ---------------------------------------------------------
    # 5. Normalize excessive spaces
    # ---------------------------------------------------------

    text = re.sub(r" {2,}", " ", text)

    # ---------------------------------------------------------
    # 6. Normalize spaces before punctuation
    # ---------------------------------------------------------

    text = re.sub(
        r"\s+([,.;:!?])",
        r"\1",
        text
    )

    # ---------------------------------------------------------
    # 7. Remove excessive blank lines
    # ---------------------------------------------------------

    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()