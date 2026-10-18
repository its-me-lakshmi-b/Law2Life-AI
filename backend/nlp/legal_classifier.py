import re


# ---------------------------------------------------------
# Document type keywords
# ---------------------------------------------------------

DOCUMENT_PATTERNS = {

    "employment_agreement": [
        "employment agreement",
        "employee",
        "employer",
        "salary",
        "working hours",
        "notice period",
        "termination",
        "leave",
        "joining date"
    ],

    "rental_agreement": [
        "rental agreement",
        "rent",
        "tenant",
        "landlord",
        "lease",
        "security deposit",
        "monthly rent",
        "premises"
    ],

    "loan_agreement": [
        "loan agreement",
        "borrower",
        "lender",
        "principal amount",
        "interest rate",
        "repayment",
        "installment",
        "emi"
    ],

    "insurance_document": [
        "insurance policy",
        "policyholder",
        "insured",
        "premium",
        "claim",
        "coverage",
        "sum insured",
        "policy number"
    ],

    "legal_notice": [
        "legal notice",
        "notice",
        "hereby called upon",
        "demand",
        "legal action",
        "compliance"
    ],

    "consumer_complaint": [
        "consumer complaint",
        "consumer",
        "complainant",
        "deficiency in service",
        "unfair trade practice",
        "refund",
        "compensation"
    ],

    "property_agreement": [
        "property agreement",
        "sale deed",
        "property",
        "buyer",
        "seller",
        "consideration",
        "possession",
        "transfer of property"
    ],

    "service_agreement": [
        "service agreement",
        "service provider",
        "client",
        "services",
        "scope of services",
        "service fee",
        "deliverables"
    ],

    "termination_letter": [
        "termination letter",
        "termination notice",
        "employment is terminated",
        "services are terminated",
        "effective date of termination"
    ],

    "court_summons_order": [
        "court summons",
        "summons",
        "court order",
        "case number",
        "hearing date",
        "respondent",
        "petitioner",
        "court"
    ]
}


def classify_document(text):
    """
    Classify a legal document based on contextual keywords.

    Returns:
        dict containing:
        - document_type
        - confidence
        - matched_keywords
        - scores
    """

    if not text:
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "matched_keywords": [],
            "scores": {}
        }

    # ---------------------------------------------------------
    # Normalize text
    # ---------------------------------------------------------

    normalized_text = text.lower()

    # Remove excessive whitespace
    normalized_text = re.sub(
        r"\s+",
        " ",
        normalized_text
    )

    # ---------------------------------------------------------
    # Calculate score for every document type
    # ---------------------------------------------------------

    scores = {}
    matched_keywords = {}

    for document_type, keywords in DOCUMENT_PATTERNS.items():

        score = 0
        matches = []

        for keyword in keywords:

            if keyword.lower() in normalized_text:

                score += 1
                matches.append(keyword)

        scores[document_type] = score
        matched_keywords[document_type] = matches

    # ---------------------------------------------------------
    # Find highest scoring document type
    # ---------------------------------------------------------

    best_type = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_type]

    # ---------------------------------------------------------
    # No meaningful match or insufficient evidence
    # ---------------------------------------------------------

    header_text = normalized_text[:300]
    has_explicit_title = any(kw in header_text for kw in DOCUMENT_PATTERNS[best_type][:2])

    if best_score < 2 and not has_explicit_title:
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "matched_keywords": matched_keywords[best_type],
            "scores": scores,
            "is_uncertain": True,
            "note": "Insufficient evidence to classify document type reliably."
        }

    # ---------------------------------------------------------
    # Calculate simple confidence
    # ---------------------------------------------------------

    total_keywords = len(
        DOCUMENT_PATTERNS[best_type]
    )

    base_confidence = best_score / total_keywords
    if has_explicit_title:
        base_confidence = max(base_confidence, 0.75)

    confidence = min(round(base_confidence, 2), 0.99)

    return {
        "document_type": best_type,
        "confidence": confidence,
        "matched_keywords": matched_keywords[best_type],
        "scores": scores,
        "is_uncertain": False
    }