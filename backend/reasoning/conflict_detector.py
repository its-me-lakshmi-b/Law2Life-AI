import re


# ============================================================
# CONFLICT DETECTOR
# ============================================================
# Purpose:
# Compare document clauses with retrieved legal information
# and identify potential inconsistencies.
#
# IMPORTANT:
# The module does not declare a clause "illegal".
# It produces potential conflicts or contextual review signals.
# ============================================================


def extract_day_values(text):
    """Extract numeric day values from text."""

    if not text:
        return []

    matches = re.findall(
        r"\b(\d+)\s*(?:day|days)\b",
        text,
        re.IGNORECASE
    )

    return [int(value) for value in matches]


def contains_conditional_language(text):
    """Detect meaningful conditions or exceptions."""

    if not text:
        return False

    conditional_terms = [
        "subject to",
        "provided that",
        "unless",
        "except",
        "exception",
        "where applicable",
        "as applicable"
    ]

    text_lower = text.lower()

    return any(
        term in text_lower
        for term in conditional_terms
    )


def contains_unconditional_language(text):
    """Detect strong unconditional language in a document clause."""

    if not text:
        return False

    unconditional_terms = [
        "must",
        "shall",
        "required to",
        "will",
        "always"
    ]

    text_lower = text.lower()

    return any(
        term in text_lower
        for term in unconditional_terms
    )


def normalize_legal_field(value):
    """
    Convert a legal dataset field into clean text.

    The field may be:
    - a string
    - a list of strings
    - None
    """

    if not value:
        return ""

    if isinstance(value, list):
        return " ".join(
            str(item).strip()
            for item in value
            if item
        )

    return str(value).strip()


def calculate_confidence(
    conflict_type,
    clause,
    provision
):
    """
    Calculate a transparent signal-strength value.

    This is NOT a probability of legal invalidity.
    """

    if conflict_type == "direct_numeric_conflict":
        confidence = 0.90

    elif conflict_type == "conditional_context_review":
        confidence = 0.60

    else:
        confidence = 0.50

    clause_days = extract_day_values(clause)
    provision_days = extract_day_values(provision)

    if clause_days and provision_days:
        confidence += 0.05

    return min(
        round(confidence, 2),
        0.95
    )


def analyze_clause_against_provision(
    clause,
    provision
):
    """
    Compare one document clause against one
    retrieved legal provision.

    Returns a finding dictionary or None.
    """

    if not clause or not provision:
        return None

    clause_text = clause.strip()
    provision_text = provision.strip()

    # ========================================================
    # CASE 1: DIRECT NUMERIC DIFFERENCE
    # ========================================================

    clause_days = extract_day_values(
        clause_text
    )

    provision_days = extract_day_values(
        provision_text
    )

    if clause_days and provision_days:

        if clause_days[0] != provision_days[0]:

            confidence = calculate_confidence(
                "direct_numeric_conflict",
                clause_text,
                provision_text
            )

            return {
                "conflict_type":
                    "direct_numeric_conflict",

                "document_clause":
                    clause_text,

                "legal_provision":
                    provision_text,

                "reason": (
                    f"The document specifies "
                    f"{clause_days[0]} days, while the "
                    f"retrieved legal information specifies "
                    f"{provision_days[0]} days. This difference "
                    f"should be verified against the applicable "
                    f"legal context."
                ),

                "confidence":
                    confidence
            }

    # ========================================================
    # CASE 2: CONDITIONAL CONTEXT
    # ========================================================
    # Only flag this when the legal provision contains
    # meaningful conditional language.
    #
    # Generic metadata such as:
    # "The document contains a leave-related clause"
    # should NOT create a conflict.
    # ========================================================

    if (
        contains_conditional_language(
            provision_text
        )
        and
        contains_unconditional_language(
            clause_text
        )
    ):

        confidence = calculate_confidence(
            "conditional_context_review",
            clause_text,
            provision_text
        )

        return {
            "conflict_type":
                "conditional_context_review",

            "document_clause":
                clause_text,

            "legal_provision":
                provision_text,

            "reason": (
                "The document clause uses unconditional "
                "language, while the retrieved legal "
                "information contains a condition or "
                "exception. This does not establish a "
                "conflict by itself, but the applicable "
                "condition should be reviewed."
            ),

            "confidence":
                confidence
        }

    return None


def detect_conflicts(
    clauses,
    legal_evidence
):
    """
    Compare document clauses with their associated
    retrieved legal evidence.
    """

    findings = []

    if not clauses or not legal_evidence:
        return findings

    for clause_item in clauses:

        if not isinstance(
            clause_item,
            dict
        ):
            continue

        clause_text = clause_item.get(
            "text",
            ""
        ).strip()

        if not clause_text:
            continue

        for evidence_item in legal_evidence:

            if not isinstance(
                evidence_item,
                dict
            ):
                continue

            evidence_clause = evidence_item.get(
                "clause",
                ""
            ).strip()

            # Only compare evidence associated
            # with the current clause.
            if (
                evidence_clause
                and
                evidence_clause != clause_text
            ):
                continue

            provisions = evidence_item.get(
                "provisions",
                []
            )

            for provision in provisions:

                if not isinstance(
                    provision,
                    dict
                ):
                    continue

                # ====================================================
                # Extract legal provision fields
                # ====================================================

                title = normalize_legal_field(
                    provision.get(
                        "title",
                        "Legal Provision"
                    )
                )

                description = normalize_legal_field(
                    provision.get(
                        "description",
                        ""
                    )
                )

                conditions = normalize_legal_field(
                    provision.get(
                        "conditions",
                        ""
                    )
                )

                exceptions = normalize_legal_field(
                    provision.get(
                        "exceptions",
                        ""
                    )
                )

                # ====================================================
                # Combine legal information
                # ====================================================

                legal_context = " ".join(
                    part
                    for part in [
                        title,
                        description,
                        conditions,
                        exceptions
                    ]
                    if part
                )

                # ====================================================
                # Compare clause with legal information
                # ====================================================

                finding = (
                    analyze_clause_against_provision(
                        clause_text,
                        legal_context
                    )
                )

                if finding:

                    finding["category"] = (
                        clause_item.get(
                            "category",
                            "unknown"
                        )
                    )

                    # Your JSON uses "provision_id",
                    # not "id".
                    finding["provision_id"] = (
                        provision.get(
                            "provision_id",
                            provision.get(
                                "id",
                                ""
                            )
                        )
                    )

                    findings.append(
                        finding
                    )

    return findings


# ============================================================
# TESTS
# ============================================================

if __name__ == "__main__":

    print(
        "\n===== CONFLICT DETECTOR TESTS =====\n"
    )

    # --------------------------------------------------------
    # TEST 1: Direct numeric conflict
    # --------------------------------------------------------

    clause_1 = (
        "Either party may terminate the employment "
        "by providing 30 days written notice."
    )

    provision_1 = (
        "Termination Notice Requirement. "
        "Applicable termination provisions require "
        "60 days written notice."
    )

    result_1 = (
        analyze_clause_against_provision(
            clause_1,
            provision_1
        )
    )

    print(
        "TEST 1 - DIRECT NUMERIC DIFFERENCE"
    )

    if result_1:

        print(
            "Detected:",
            result_1["conflict_type"]
        )

        print(
            "Reason:",
            result_1["reason"]
        )

        print(
            "Confidence:",
            result_1["confidence"]
        )

    else:

        print(
            "No issue detected."
        )

    print("-" * 70)

    # --------------------------------------------------------
    # TEST 2: Conditional context
    # --------------------------------------------------------

    clause_2 = (
        "The employee must provide written notice "
        "before termination."
    )

    provision_2 = (
        "Termination may be subject to applicable "
        "conditions and exceptions."
    )

    result_2 = (
        analyze_clause_against_provision(
            clause_2,
            provision_2
        )
    )

    print(
        "TEST 2 - CONDITIONAL CONTEXT"
    )

    if result_2:

        print(
            "Detected:",
            result_2["conflict_type"]
        )

        print(
            "Reason:",
            result_2["reason"]
        )

        print(
            "Confidence:",
            result_2["confidence"]
        )

    else:

        print(
            "No issue detected."
        )

    print("-" * 70)

    # --------------------------------------------------------
    # TEST 3: No conflict
    # --------------------------------------------------------

    clause_3 = (
        "Salary will be paid monthly."
    )

    provision_3 = (
        "Salary provisions relate to employee payment."
    )

    result_3 = (
        analyze_clause_against_provision(
            clause_3,
            provision_3
        )
    )

    print(
        "TEST 3 - NO CONFLICT"
    )

    if result_3:

        print(
            "Detected:",
            result_3["conflict_type"]
        )

    else:

        print(
            "No conflict detected."
        )

    print(
        "\n===== TESTING COMPLETE ====="
    )