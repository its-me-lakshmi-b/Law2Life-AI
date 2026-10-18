"""
Law2Life AI - Evidence-Grounded Action Recommender
Generates prudent, actionable, and legally sound advisory recommendations
based on detected potential issues, deadlines, contractual obligations, and uncertainty.
"""

from typing import List, Dict, Any


def recommend_actions(
    conflicts: List[Dict[str, Any]] = None,
    clauses: Dict[str, List[str]] = None,
    legal_facts: Dict[str, Any] = None,
    legal_evidence: List[Dict[str, Any]] = None,
    document_type: str = "unknown"
) -> List[Dict[str, Any]]:
    """
    Generate evidence-grounded practical next actions.

    Returns:
        List of dicts with:
        - action: Action description string
        - reason: Rational explanation why the action is suggested
        - supporting_clause: Relevant clause snippet (if any)
        - supporting_evidence: Statutory authority or provision cited (if any)
        - urgency: 'normal' | 'moderate' | 'high'
        - limitation: Boundaries of the advice
    """
    conflicts = conflicts or []
    clauses = clauses or {}
    legal_facts = legal_facts or {}
    legal_evidence = legal_evidence or []

    # Normalize clauses if passed as list of dicts
    if isinstance(clauses, list):
        c_dict = {}
        for item in clauses:
            if isinstance(item, dict):
                c_dict.setdefault(item.get("category", "general"), []).append(item.get("text", ""))
        clauses = c_dict

    recommendations: List[Dict[str, Any]] = []

    # 1. RECOMMENDATIONS GROUNDED IN POTENTIAL ISSUES / CONFLICTS
    for conflict in conflicts:
        ctype = conflict.get("conflict_type")
        clause = conflict.get("document_clause", "")
        prov = conflict.get("legal_provision", "")
        reason = conflict.get("reason", "")
        citation = conflict.get("citation", conflict.get("section", "Statutory Provision"))

        if ctype == "direct_numeric_conflict":
            recommendations.append({
                "action": "Request written clarification regarding the notice period or timeframe discrepancy.",
                "reason": f"Document specifies a timeline that differs from the statutory baseline cited under {citation}.",
                "supporting_clause": clause[:120] + ("..." if len(clause) > 120 else ""),
                "supporting_evidence": citation,
                "urgency": "high",
                "limitation": "Statutory exemptions or industry-specific rules may modify standard timeframes."
            })

        elif ctype == "statutory_restriction_review":
            recommendations.append({
                "action": "Consult legal counsel regarding the enforceability of post-employment trade restrictions.",
                "reason": "Section 27 of the Indian Contract Act, 1872 renders agreements in restraint of trade void in India.",
                "supporting_clause": clause[:120] + ("..." if len(clause) > 120 else ""),
                "supporting_evidence": "Section 27, Indian Contract Act, 1872",
                "urgency": "high",
                "limitation": "Confidentiality of proprietary trade secrets remains protectable under Indian jurisprudence."
            })

        elif ctype == "conditional_context_review":
            recommendations.append({
                "action": "Verify whether statutory preconditions or exceptions apply to this unconditional clause.",
                "reason": conflict.get("conditions_to_review", "Statutory context includes conditions that may limit strict application."),
                "supporting_clause": clause[:120] + ("..." if len(clause) > 120 else ""),
                "supporting_evidence": citation,
                "urgency": "moderate",
                "limitation": "Factual applicability depends on employee category and establishment size."
            })

    # 2. RECOMMENDATIONS GROUNDED IN DEADLINES
    deadlines = clauses.get("deadlines", [])
    if deadlines and not any(r["action"].startswith("Calendar") for r in recommendations):
        recommendations.append({
            "action": "Calendar and track all explicit notice, payment, and request deadlines.",
            "reason": f"The document identifies {len(deadlines)} time-sensitive deadline condition(s) governing compliance.",
            "supporting_clause": deadlines[0][:120] + ("..." if len(deadlines[0]) > 120 else ""),
            "supporting_evidence": "Contractual time-bar stipulations",
            "urgency": "moderate",
            "limitation": "Failure to submit timely notices or requests may waive contractual entitlements."
        })

    # 3. RECOMMENDATIONS GROUNDED IN MISSING DOCUMENTATION OR FACTS
    if document_type == "employment_agreement":
        if not legal_facts.get("salary"):
            recommendations.append({
                "action": "Confirm written compensation schedule and remuneration Annexure with employer.",
                "reason": "Explicit salary or compensation figures are not clearly detailed in the main agreement body.",
                "supporting_clause": "",
                "supporting_evidence": "Payment of Wages Act, 1936",
                "urgency": "moderate",
                "limitation": "Compensation may be defined in an accompanying offer letter or appointment order."
            })
    elif document_type == "rental_agreement":
        if not legal_facts.get("security_deposit"):
            recommendations.append({
                "action": "Record the security deposit receipt and explicit refund terms in writing.",
                "reason": "Security deposit quantum and refund timeline should be documented to avoid tenancy disputes.",
                "supporting_clause": "",
                "supporting_evidence": "Transfer of Property Act, 1882",
                "urgency": "moderate",
                "limitation": "Local rent control or tenancy agreements require transparent deposit stipulations."
            })

    # 4. DISPUTE RESOLUTION / GRIEVANCE REDRESSAL ADVICE
    dispute_clauses = clauses.get("dispute_resolution", [])
    if dispute_clauses:
        recommendations.append({
            "action": "Note the agreed dispute resolution escalation hierarchy.",
            "reason": "The document specifies internal resolution or designated jurisdiction before initiating formal proceedings.",
            "supporting_clause": dispute_clauses[0][:120] + ("..." if len(dispute_clauses[0]) > 120 else ""),
            "supporting_evidence": "Dispute Resolution Clause",
            "urgency": "normal",
            "limitation": "Statutory labour courts or consumer forums may retain overriding statutory jurisdiction."
        })

    # 5. SAFE PROFESSIONAL CONSULTATION FALLBACK
    recommendations.append({
        "action": "Consult a qualified legal practitioner for binding legal advice.",
        "reason": (
            "Law2Life AI provides informational decision support based on automated NLP and Knowledge Graph reasoning. "
            "It does not substitute for qualified legal representation."
        ),
        "supporting_clause": "",
        "supporting_evidence": "Advisory Disclaimer",
        "urgency": "normal",
        "limitation": "Analysis is subject to document completeness and jurisdiction-specific legislation."
    })

    return recommendations


if __name__ == "__main__":
    test_conflicts = [{
        "conflict_type": "direct_numeric_conflict",
        "document_clause": "Notice period of 15 days.",
        "legal_provision": "Section 25F requires 30 days notice.",
        "citation": "Section 25F, Industrial Disputes Act, 1947",
        "reason": "Difference between 15 days and 30 days."
    }]
    test_clauses = {
        "deadlines": ["Salary payable by 7th day."],
        "dispute_resolution": ["Courts in Bengaluru shall have exclusive jurisdiction."]
    }
    actions = recommend_actions(
        conflicts=test_conflicts,
        clauses=test_clauses,
        document_type="employment_agreement"
    )
    print("===== RECOMMENDED ACTIONS =====")
    for idx, act in enumerate(actions, 1):
        print(f"{idx}. {act['action']} (Urgency: {act['urgency']})")
        print(f"   Why: {act['reason']}")
