# ============================================================
# LAW2LIFE AI - RISK ENGINE
# ============================================================

def calculate_risk(
    conflicts=None,
    clauses=None,
    legal_evidence=None
):
    """
    Calculate an overall document risk level using the
    results produced by the legal analysis pipeline.

    This is an analytical risk indicator only.
    It does not determine whether a document is legally
    valid or invalid.
    """

    conflicts = conflicts if conflicts is not None else []
    legal_evidence = legal_evidence if legal_evidence is not None else []

    # Handle clauses whether passed as dict or list of dicts/strings
    if clauses is None:
        clauses = {}
    elif isinstance(clauses, list):
        clause_dict = {}
        for item in clauses:
            if isinstance(item, dict):
                cat = item.get("category", "general")
                txt = item.get("text", "")
                clause_dict.setdefault(cat, []).append(txt)
            elif isinstance(item, str):
                clause_dict.setdefault("general", []).append(item)
        clauses = clause_dict
    elif not isinstance(clauses, dict):
        clauses = {}

    risk_score = 0
    risk_factors = []



    # ========================================================
    # 1. POTENTIAL ISSUES
    # ========================================================

    if conflicts:

        high_confidence_conflicts = [
            conflict
            for conflict in conflicts
            if conflict.get("confidence", 0) >= 0.80
        ]

        medium_confidence_conflicts = [
            conflict
            for conflict in conflicts
            if 0.60 <= conflict.get("confidence", 0) < 0.80
        ]

        low_confidence_conflicts = [
            conflict
            for conflict in conflicts
            if conflict.get("confidence", 0) < 0.60
        ]

        # High-confidence potential issues
        if high_confidence_conflicts:

            risk_score += min(
                len(high_confidence_conflicts) * 25,
                50
            )

            risk_factors.append(
                f"{len(high_confidence_conflicts)} "
                "high-confidence potential issue(s) "
                "were identified."
            )

        # Medium-confidence issues
        if medium_confidence_conflicts:

            risk_score += min(
                len(medium_confidence_conflicts) * 15,
                30
            )

            risk_factors.append(
                f"{len(medium_confidence_conflicts)} "
                "potential issue(s) require further "
                "contextual review."
            )

        # Low-confidence findings
        if low_confidence_conflicts:

            risk_score += min(
                len(low_confidence_conflicts) * 5,
                10
            )

            risk_factors.append(
                f"{len(low_confidence_conflicts)} "
                "lower-confidence finding(s) were identified."
            )

    else:

        risk_factors.append(
            "No potential conflicts were detected "
            "from the available legal evidence."
        )


    # ========================================================
    # 2. IMPORTANT DEADLINES
    # ========================================================

    deadlines = clauses.get(
        "deadlines",
        []
    )

    if deadlines:

        risk_score += min(
            len(deadlines) * 5,
            15
        )

        risk_factors.append(
            f"{len(deadlines)} important deadline(s) "
            "or time-related condition(s) were identified."
        )


    # ========================================================
    # 3. TERMINATION CONDITIONS
    # ========================================================

    termination = clauses.get(
        "termination",
        []
    )

    if termination:

        risk_score += 10

        risk_factors.append(
            "The document contains termination-related "
            "conditions that may require careful review."
        )


    # ========================================================
    # 4. CONFIDENTIALITY OBLIGATIONS
    # ========================================================

    confidentiality = clauses.get(
        "confidentiality",
        []
    )

    if confidentiality:

        risk_score += 5

        risk_factors.append(
            "The document contains confidentiality "
            "obligations."
        )


    # ========================================================
    # 5. LEAVE CONDITIONS
    # ========================================================

    leave = clauses.get(
        "leave",
        []
    )

    if leave:

        risk_score += 5

        risk_factors.append(
            "The document contains leave-related "
            "conditions or requirements."
        )


    # ========================================================
    # 6. LEGAL EVIDENCE AVAILABILITY
    # ========================================================

    if legal_evidence:

        risk_factors.append(
            f"{len(legal_evidence)} clause-level legal "
            "evidence match(es) were available for analysis."
        )

    else:

        risk_score += 10

        risk_factors.append(
            "Limited relevant legal evidence was available "
            "for comparison."
        )


    # ========================================================
    # 7. LIMIT SCORE
    # ========================================================

    risk_score = min(
        risk_score,
        100
    )


    # ========================================================
    # 8. DETERMINE RISK LEVEL
    # ========================================================

    if risk_score >= 60:

        risk_level = "High"

    elif risk_score >= 30:

        risk_level = "Moderate"

    else:

        risk_level = "Low"


    # ========================================================
    # 9. OVERALL EXPLANATION
    # ========================================================

    if risk_level == "High":

        explanation = (
            "Several factors require careful review. "
            "The document contains potential issues or "
            "conditions that may have greater significance "
            "based on the available analysis."
        )

    elif risk_level == "Moderate":

        explanation = (
            "The document contains some conditions, "
            "obligations, deadlines, or potential issues "
            "that should be reviewed carefully."
        )

    else:

        explanation = (
            "The available analysis did not identify "
            "major potential issues. However, the document "
            "should still be reviewed in its full legal context."
        )


    # ========================================================
    # 10. RETURN RISK RESULT
    # ========================================================

    # Build structured factor objects for the dashboard UI
    factors = []
    for factor_str in risk_factors:
        pts = 0
        if "high-confidence" in factor_str:
            pts = 25
        elif "potential issue" in factor_str:
            pts = 15
        elif "deadline" in factor_str:
            pts = 5
        elif "termination" in factor_str:
            pts = 10
        elif "confidentiality" in factor_str or "leave" in factor_str:
            pts = 5
        factors.append({
            "factor": factor_str.split(".")[0],
            "reason": factor_str,
            "points": pts
        })

    return {
        "risk_score": risk_score,
        "score": risk_score,
        "risk_level": risk_level,
        "level": risk_level,
        "risk_factors": risk_factors,
        "factors": factors,
        "explanation": explanation
    }



# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("LAW2LIFE AI - RISK ENGINE TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # TEST 1 - NO POTENTIAL ISSUES
    # --------------------------------------------------------

    test_clauses_1 = {
        "deadlines": [
            "Salary is payable on or before the 5th day."
        ],
        "termination": [
            "Either party may terminate with notice."
        ],
        "confidentiality": [
            "The employee must maintain confidentiality."
        ],
        "leave": [
            "The employee is entitled to paid leave."
        ]
    }

    test_conflicts_1 = []

    test_evidence_1 = [
        {
            "clause": "Salary clause",
            "provisions": []
        }
    ]

    result_1 = calculate_risk(
        conflicts=test_conflicts_1,
        clauses=test_clauses_1,
        legal_evidence=test_evidence_1
    )

    print("\nTEST 1 - NORMAL DOCUMENT")
    print("Risk Score:", result_1["risk_score"])
    print("Risk Level:", result_1["risk_level"])
    print("Explanation:", result_1["explanation"])

    print("\nRisk Factors:")

    for factor in result_1["risk_factors"]:
        print("-", factor)


    # --------------------------------------------------------
    # TEST 2 - POTENTIAL ISSUE
    # --------------------------------------------------------

    test_conflicts_2 = [
        {
            "conflict_type": "direct_numeric_conflict",
            "confidence": 0.95,
            "reason": (
                "The document specifies 30 days while "
                "the retrieved legal information specifies "
                "60 days."
            )
        }
    ]

    test_clauses_2 = {
        "deadlines": [
            "30 days written notice."
        ],
        "termination": [
            "Either party may terminate the agreement."
        ],
        "confidentiality": [],
        "leave": []
    }

    test_evidence_2 = [
        {
            "clause": "Termination clause",
            "provisions": [
                {
                    "title": "Termination and Notice"
                }
            ]
        }
    ]

    result_2 = calculate_risk(
        conflicts=test_conflicts_2,
        clauses=test_clauses_2,
        legal_evidence=test_evidence_2
    )

    print()
    print("-" * 60)
    print("TEST 2 - POTENTIAL ISSUE")
    print("Risk Score:", result_2["risk_score"])
    print("Risk Level:", result_2["risk_level"])
    print("Explanation:", result_2["explanation"])

    print("\nRisk Factors:")

    for factor in result_2["risk_factors"]:
        print("-", factor)


    # --------------------------------------------------------
    # TEST 3 - NO LEGAL EVIDENCE
    # --------------------------------------------------------

    result_3 = calculate_risk(
        conflicts=[],
        clauses={},
        legal_evidence=[]
    )

    print()
    print("-" * 60)
    print("TEST 3 - LIMITED LEGAL EVIDENCE")
    print("Risk Score:", result_3["risk_score"])
    print("Risk Level:", result_3["risk_level"])
    print("Explanation:", result_3["explanation"])

    print("\nRisk Factors:")

    for factor in result_3["risk_factors"]:
        print("-", factor)


    print()
    print("=" * 60)
    print("RISK ENGINE TESTING COMPLETE")
    print("=" * 60)