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


def extract_legal_quantities(text: str) -> dict:
    """
    Extract structured legal quantities distinguished by concept:
    - notice_days: Days required for notice of termination, quitting, or leave
    - continuous_service_days: Days of prior continuous service required for statutory eligibility
    - wage_payment_day: Day of month or deadline after wage period for salary payment
    - working_hours_weekly: Max statutory weekly working hours
    - working_hours_daily: Max statutory daily working hours
    """
    if not text:
        return {}

    quantities = {}
    text_lower = text.lower()

    # 1. Continuous service eligibility days (e.g. 240 days under Section 25F IDA, 80 days under MBA)
    cs_match = re.search(
        r"(?:continuous\s*service|worked\s*(?:in\s*an\s*establishment)?|employed)\s*(?:for\s*|of\s*)?(?:not\s*less\s*than\s*)?(\d+)\s*days",
        text_lower
    )
    if cs_match:
        quantities["continuous_service_days"] = int(cs_match.group(1))

    # 2. Notice period days (e.g. 30 days notice, one month notice, 15 days notice)
    notice_match = re.search(
        r"\b(\d+)\s*(?:day|days)(?:'|\s*written|\s*prior)?\s*notice\b",
        text_lower
    )
    if notice_match:
        quantities["notice_days"] = int(notice_match.group(1))
    elif re.search(r"\bnotice\s*(?:period\s*)?(?:of\s*)?(\d+)\s*days\b", text_lower):
        quantities["notice_days"] = int(re.search(r"\bnotice\s*(?:period\s*)?(?:of\s*)?(\d+)\s*days\b", text_lower).group(1))
    elif re.search(r"\b(?:one|1)\s*month(?:'s)?\s*notice\b", text_lower) or re.search(r"\bnotice\s*of\s*(?:one|1)\s*month\b", text_lower):
        quantities["notice_days"] = 30
    elif re.search(r"\bfifteen\s*days(?:'|\s*written)?\s*notice\b", text_lower):
        quantities["notice_days"] = 15
    elif re.search(r"\bsix\s*months(?:'|\s*written)?\s*notice\b", text_lower):
        quantities["notice_days"] = 180
    elif "notice" in text_lower:
        # Fallback for "by providing 30 days" in notice clause
        day_match = re.search(r"\b(\d+)\s*(?:day|days)\b", text_lower)
        if day_match:
            d_val = int(day_match.group(1))
            if d_val != quantities.get("continuous_service_days"):
                quantities["notice_days"] = d_val

    # 3. Wage payment day (Payment of Wages Act)
    if "seventh day" in text_lower or "7th day" in text_lower:
        quantities["wage_payment_day"] = 7
    elif "tenth day" in text_lower or "10th day" in text_lower:
        quantities["wage_payment_day"] = 10
    elif "second working day" in text_lower or "2nd working day" in text_lower:
        quantities["wage_payment_day"] = 2
    else:
        # Check explicit clause payment day e.g. "by 15th of each month"
        pay_match = re.search(r"\b(?:on\s*or\s*before\s*the\s*|by\s*the\s*)(\d+)(?:st|nd|rd|th)?\s*(?:day)?\b", text_lower)
        if pay_match and any(w in text_lower for w in ["salary", "wages", "rent", "payable", "payment"]):
            quantities["wage_payment_day"] = int(pay_match.group(1))

    # 4. Working hours
    wh_weekly = re.search(r"(\d+)\s*hours?\s*(?:in|per)\s*(?:any\s*)?week", text_lower)
    if wh_weekly:
        quantities["working_hours_weekly"] = int(wh_weekly.group(1))
    wh_daily = re.search(r"(\d+)\s*hours?\s*(?:in|per)\s*(?:any\s*)?day", text_lower)
    if wh_daily:
        quantities["working_hours_daily"] = int(wh_daily.group(1))

    return quantities


def detect_topic(text: str) -> str:
    """Classify the subject domain of a clause or legal provision."""
    t = text.lower()
    if any(k in t for k in ["terminate", "termination", "retrenchment", "notice to quit", "discharge"]):
        return "termination"
    if any(k in t for k in ["salary", "wages", "seventh day", "tenth day", "deduction", "payment terms"]):
        return "salary"
    if any(k in t for k in ["leave", "vacation", "maternity", "casual leave"]):
        return "leave"
    if any(k in t for k in ["restraint of trade", "non-compete", "working for competitor", "post-employment"]):
        return "restraint_of_trade"
    if any(k in t for k in ["penalty", "forfeit", "liquidated damages", "bond amount"]):
        return "penalty"
    if any(k in t for k in ["working hours", "48 hours", "9 hours", "rest interval", "overtime"]):
        return "working_hours"
    if any(k in t for k in ["rent", "security deposit", "lease period"]):
        return "tenancy"
    return "general"


def contains_conditional_language(text):
    """Detect meaningful conditions or exceptions."""
    if not text:
        return False
    conditional_terms = [
        "subject to", "provided that", "unless", "except",
        "exception", "where applicable", "as applicable"
    ]
    text_lower = text.lower()
    return any(term in text_lower for term in conditional_terms)


def contains_unconditional_language(text):
    """Detect strong unconditional language in a document clause."""
    if not text:
        return False
    unconditional_terms = ["must", "shall", "required to", "will", "always"]
    text_lower = text.lower()
    return any(term in text_lower for term in unconditional_terms)


def normalize_legal_field(value):
    """Convert a legal dataset field into clean text."""
    if not value:
        return ""
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value if item)
    return str(value).strip()


def calculate_confidence(conflict_type, clause, provision):
    """Calculate a transparent signal-strength value."""
    if conflict_type == "direct_numeric_conflict":
        confidence = 0.90
    elif conflict_type == "statutory_restriction_review":
        confidence = 0.88
    elif conflict_type == "conditional_context_review":
        confidence = 0.60
    elif conflict_type == "missing_fact_dependency":
        confidence = 0.70
    else:
        confidence = 0.50

    return min(round(confidence, 2), 0.95)


def analyze_clause_against_provision(
    clause,
    provision,
    provision_obj=None,
    clause_category=None
):
    """
    Compare one document clause against one retrieved legal provision.
    Checks topic compatibility to avoid comparing unrelated numbers or rules.
    Only compares numeric quantities when they concern the same legal concept and unit.
    """
    if not clause or not provision:
        return None

    clause_text = clause.strip()
    provision_text = provision.strip()

    clause_topic = clause_category or detect_topic(clause_text)
    provision_topic = detect_topic(provision_text)

    # Topic Compatibility Guard:
    topics_compatible = (
        clause_topic == provision_topic
        or clause_topic == "general"
        or provision_topic == "general"
        or (clause_topic in {"termination", "deadlines"} and provision_topic in {"termination", "deadlines"})
    )

    clause_quantities = extract_legal_quantities(clause_text)
    provision_quantities = extract_legal_quantities(provision_text)

    # ------------------------------------------------------------------
    # CASE 1: NOTICE PERIOD COMPARISON (Same concept: notice_days)
    # ------------------------------------------------------------------
    if topics_compatible and "notice_days" in clause_quantities and "notice_days" in provision_quantities:
        c_notice = clause_quantities["notice_days"]
        p_notice = provision_quantities["notice_days"]

        if c_notice != p_notice:
            confidence = calculate_confidence("direct_numeric_conflict", clause_text, provision_text)
            return {
                "title": f"Notice Period Discrepancy ({c_notice} days vs {p_notice} days)",
                "conflict_type": "direct_numeric_conflict",
                "finding_status": "potential_concern",
                "fact_status": "confirmed_document_fact",
                "document_clause": clause_text,
                "legal_provision": provision_text,
                "reason": (
                    f"The document specifies a notice period of {c_notice} days, while the statutory baseline "
                    f"under the retrieved provision specifies {p_notice} days. This duration difference requires review."
                ),
                "confidence": confidence,
                "confidence_meaning": (
                    "High signal strength (0.90) reflecting direct numerical difference between contractual notice "
                    "days and statutory notice baseline. It is a heuristic indicator, not a definitive legal finding."
                ),
                "conditions_to_review": (
                    "Check whether statutory exemptions, establishment headcount, or mutual contractual "
                    "waivers apply to this notice requirement."
                ),
                "missing_facts": [
                    "workman_status",
                    "continuous_service_duration",
                    "establishment_size"
                ],
                "suggested_next_step": (
                    "Confirm the applicable statutory notice threshold or consult a qualified legal professional "
                    "regarding the enforceability of the shorter/longer notice duration."
                )
            }

    # ------------------------------------------------------------------
    # CASE 2: CONTINUOUS SERVICE PREREQUISITE (Missing fact, NOT numeric conflict)
    # ------------------------------------------------------------------
    # If the provision requires continuous service (e.g. 240 days under IDA Section 25F),
    # but the document clause has a valid notice period (e.g. 30 days) and does not state
    # whether continuous service is met: do NOT flag numeric conflict!
    # Instead, recognize that continuous service is a statutory prerequisite.
    if topics_compatible and "continuous_service_days" in provision_quantities:
        p_cs = provision_quantities["continuous_service_days"]
        # If the clause notice days matched or were evaluated, check if continuous service is stated
        if "continuous_service_days" not in clause_quantities:
            # This is a missing fact condition, NOT a numeric conflict between notice and 240 days!
            pass

    # ------------------------------------------------------------------
    # CASE 3: WORKING HOURS COMPARISON (Same concept: weekly/daily hours)
    # ------------------------------------------------------------------
    if "working_hours_weekly" in clause_quantities and "working_hours_weekly" in provision_quantities:
        c_wh = clause_quantities["working_hours_weekly"]
        p_wh = provision_quantities["working_hours_weekly"]
        if c_wh > p_wh:
            confidence = calculate_confidence("direct_numeric_conflict", clause_text, provision_text)
            return {
                "title": f"Weekly Working Hours Exceed Statutory Ceiling ({c_wh}h vs {p_wh}h)",
                "conflict_type": "direct_numeric_conflict",
                "finding_status": "potential_concern",
                "fact_status": "confirmed_document_fact",
                "document_clause": clause_text,
                "legal_provision": provision_text,
                "reason": (
                    f"The document stipulates {c_wh} working hours per week, which exceeds the statutory maximum "
                    f"of {p_wh} hours per week under the Factories Act / Shops & Establishments Act."
                ),
                "confidence": confidence,
                "confidence_meaning": (
                    "High signal strength (0.90) reflecting numerical excess over statutory weekly maximum hours."
                ),
                "conditions_to_review": (
                    "Check whether statutory overtime compensation (at twice ordinary rate) is provided."
                ),
                "missing_facts": [
                    "overtime_compensation_terms",
                    "managerial_exemption"
                ],
                "suggested_next_step": (
                    "Verify whether overtime pay provisions exist and whether hours caps comply with state rules."
                )
            }

    # ------------------------------------------------------------------
    # CASE 4: RESTRAINT OF TRADE (Section 27 Indian Contract Act)
    # ------------------------------------------------------------------
    if "non-compete" in clause_text.lower() or "restrain" in clause_text.lower() or "competitor" in clause_text.lower():
        if "section 27" in provision_text.lower() or "restraint of trade" in provision_text.lower():
            return {
                "title": "Post-Employment Non-Compete Restriction (Restraint of Trade)",
                "conflict_type": "statutory_restriction_review",
                "finding_status": "potential_concern",
                "fact_status": "confirmed_document_fact",
                "document_clause": clause_text,
                "legal_provision": provision_text,
                "reason": (
                    "Under Section 27 of the Indian Contract Act, 1872, agreements that restrain any person from "
                    "exercising a lawful profession, trade, or business are void to that extent. Post-employment non-compete "
                    "restrictions are routinely struck down by Indian courts as contrary to public policy."
                ),
                "confidence": 0.88,
                "confidence_meaning": (
                    "Established legal principle (0.88) based on settled judicial interpretation of Section 27. "
                    "Non-disclosure of proprietary trade secrets remains lawful, but general covenants prohibiting "
                    "taking employment with competitors post-termination are generally unenforceable."
                ),
                "conditions_to_review": (
                    "Non-disclosure of confidential trade secrets is permissible, but broad post-employment non-compete "
                    "restrictions are routinely struck down by Indian courts."
                ),
                "missing_facts": [
                    "scope_of_confidentiality",
                    "geographical_and_temporal_limits"
                ],
                "suggested_next_step": (
                    "Seek legal advice to confirm whether post-termination restrictions exceed permissible confidentiality boundaries."
                )
            }

    # ------------------------------------------------------------------
    # CASE 5: CONDITIONAL CONTEXT REVIEW (Only on compatible topics)
    # ------------------------------------------------------------------
    if topics_compatible and contains_conditional_language(provision_text) and contains_unconditional_language(clause_text):
        confidence = calculate_confidence(
            "conditional_context_review",
            clause_text,
            provision_text
        )

        return {
            "title": f"Unconditional Clause vs Statutory Exceptions ({clause_topic.replace('_', ' ').title()})",
            "conflict_type": "conditional_context_review",
            "finding_status": "conditional_review",
            "fact_status": "confirmed_document_fact",
            "document_clause": clause_text,
            "legal_provision": provision_text,
            "reason": (
                f"The document clause uses unconditional language regarding {clause_topic.replace('_', ' ')}, "
                f"while the statutory provision contains statutory conditions or exceptions."
            ),
            "confidence": confidence,
            "confidence_meaning": (
                "Moderate signal strength (0.60) indicating that statutory qualifications or exceptions may qualify "
                "the absolute contractual wording."
            ),
            "conditions_to_review": (
                "Verify whether the specific factual prerequisites in the statutory provision "
                "apply to the parties and establishment."
            ),
            "missing_facts": [
                "statutory_exceptions_applicability",
                "factual_prerequisites"
            ],
            "suggested_next_step": (
                "Review the official legislative exceptions cited in the provision to confirm whether full unconditional compliance is mandated."
            )
        }

    return None


def detect_conflicts(
    clauses,
    legal_evidence
):
    """
    Compare document clauses with their associated retrieved legal evidence.
    Deduplicates findings using stable identity: (clause, provision_id, conflict_type).
    Preserves confirmed document facts, distinguishes missing facts, and avoids false positives.
    """
    findings = []
    seen_finding_keys = set()

    if not clauses or not legal_evidence:
        return findings

    for clause_item in clauses:
        if not isinstance(clause_item, dict):
            continue

        clause_text = clause_item.get("text", "").strip()
        if not clause_text:
            continue

        for evidence_item in legal_evidence:
            if not isinstance(evidence_item, dict):
                continue

            evidence_clause = evidence_item.get("clause", "").strip()
            # Only compare evidence associated with the current clause
            if evidence_clause and evidence_clause != clause_text:
                continue

            provisions = evidence_item.get("provisions", [])
            for provision in provisions:
                if not isinstance(provision, dict):
                    continue

                title = normalize_legal_field(provision.get("title", "Legal Provision"))
                description = normalize_legal_field(provision.get("description", ""))
                conditions = normalize_legal_field(provision.get("conditions", ""))
                exceptions = normalize_legal_field(provision.get("exceptions", ""))

                legal_context = " ".join(
                    part for part in [title, description, conditions, exceptions] if part
                )

                finding = analyze_clause_against_provision(
                    clause_text,
                    legal_context,
                    provision_obj=provision,
                    clause_category=clause_item.get("category")
                )

                if finding:
                    prov_id = provision.get("provision_id", provision.get("id", ""))
                    conf_type = finding.get("conflict_type", "")
                    dedup_key = (clause_text.lower(), prov_id, conf_type)

                    # Deduplication guard: ignore duplicate findings
                    if dedup_key in seen_finding_keys:
                        continue
                    seen_finding_keys.add(dedup_key)

                    finding["finding_id"] = f"issue_{len(findings) + 1}"
                    finding["category"] = clause_item.get("category", "unknown")
                    finding["provision_id"] = prov_id
                    src = provision.get("source", {})
                    finding["act"] = provision.get("act", src.get("act", src.get("name", "Indian Statute")))
                    finding["section"] = provision.get("section", src.get("section", ""))
                    finding["citation"] = provision.get("citation", src.get("citation", ""))
                    finding["source_url"] = src.get("url", "")
                    finding["source_organization"] = src.get("source_organization", "Government of India")
                    finding["verification_status"] = provision.get("verification_status", src.get("verification_status", "verified_statute"))
                    findings.append(finding)

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