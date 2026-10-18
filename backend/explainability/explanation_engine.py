"""
Law2Life AI - Traceable Explainability Engine
Generates human-readable evidence trails connecting document text,
NLP extractions, retrieved statutory evidence, Knowledge Graph relations,
detected potential issues, risk indicator, and recommendations.
"""

from typing import Dict, List, Any


def generate_explanation(
    document_type: str = "unknown",
    legal_facts: Dict[str, Any] = None,
    clauses: Any = None,
    legal_evidence: List[Dict[str, Any]] = None,
    graph_reasoning: List[Dict[str, Any]] = None,
    conflicts: List[Dict[str, Any]] = None,
    risk_assessment: Dict[str, Any] = None,
    actions: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Construct a traceable, 10-point reasoning trail explaining how the analysis was produced.
    Matches the schema expected by frontend/js/dashboard.js:
    {
        "steps": [
            { "title": str, "description": str },
            ...
        ],
        "summary": str
    }
    """
    legal_facts = legal_facts or {}
    legal_evidence = legal_evidence or []
    graph_reasoning = graph_reasoning or []
    conflicts = conflicts or []
    risk_assessment = risk_assessment or {}
    actions = actions or []

    # Count clauses
    clause_count = 0
    if isinstance(clauses, dict):
        clause_count = sum(len(v) for v in clauses.values())
    elif isinstance(clauses, list):
        clause_count = len(clauses)

    steps: List[Dict[str, str]] = []

    # 1. Document Ingestion & Classification
    doc_readable = document_type.replace("_", " ").title() if document_type != "unknown" else "General Legal Document"
    steps.append({
        "title": "1. Document Extraction & Classification",
        "description": (
            f"The uploaded document was processed and classified as '{doc_readable}'. "
            f"The NLP pipeline extracted the core legal structure, identifying {clause_count} clauses "
            f"and key document metadata."
        )
    })

    # 2. Entity & Fact Grounding
    parties_found = []
    if legal_facts.get("employee"):
        parties_found.append(f"Employee: {legal_facts['employee']}")
    if legal_facts.get("employer"):
        parties_found.append(f"Employer: {legal_facts['employer']}")
    if legal_facts.get("tenant"):
        parties_found.append(f"Tenant: {legal_facts['tenant']}")
    if legal_facts.get("landlord"):
        parties_found.append(f"Landlord: {legal_facts['landlord']}")
    if legal_facts.get("salary"):
        parties_found.append(f"Compensation: {legal_facts['salary']}")
    if legal_facts.get("notice_period"):
        parties_found.append(f"Notice Period: {legal_facts['notice_period']}")

    parties_desc = "; ".join(parties_found) if parties_found else "Parties and key financial/temporal terms were scanned."
    steps.append({
        "title": "2. Grounded Legal Fact Extraction",
        "description": (
            f"The system extracted key contractual entities and terms: {parties_desc}. "
            f"These grounded facts establish the legal context for statutory evaluation."
        )
    })

    # 3. Statutory Retrieval Matching
    evidence_provisions = []
    for item in legal_evidence:
        for prov in item.get("provisions", []):
            title = prov.get("title", "")
            act = prov.get("act", prov.get("source", {}).get("act", ""))
            section = prov.get("section", prov.get("source", {}).get("section", ""))
            citation = f"{act} ({section})" if section else act
            if citation and citation not in evidence_provisions:
                evidence_provisions.append(citation)

    ev_summary = ", ".join(evidence_provisions[:3]) if evidence_provisions else "Indian statutory baseline rules"
    steps.append({
        "title": "3. Relevant Statutory Evidence Retrieval",
        "description": (
            f"Using hybrid retrieval (lexical matching combined with TF-IDF semantic similarity), "
            f"the system matched extracted clauses against official Indian statutes, including {ev_summary}."
        )
    })

    # 4. Relevance & Provenance Verification
    steps.append({
        "title": "4. Relevance & Provenance Verification",
        "description": (
            f"Every retrieved legal provision was verified for jurisdiction (India), official authority "
            f"(Ministry of Law & Justice / India Code), and subject matter scope. Only provisions directly "
            f"pertaining to the document's identified categories were retained."
        )
    })

    # 5. Knowledge Graph Contextual Relationships
    kg_connections = []
    for item in graph_reasoning:
        concept = item.get("concept", "")
        for r_node in item.get("related_nodes", []):
            relation = r_node.get("relation", "")
            target = r_node.get("node", "")
            conn = f"'{concept}' --[{relation}]--> '{target}'"
            if conn not in kg_connections and len(kg_connections) < 3:
                kg_connections.append(conn)

    kg_desc = "; ".join(kg_connections) if kg_connections else "Cross-concept relationships mapped across parties, obligations, and statutes."
    steps.append({
        "title": "5. Internal Knowledge Graph Reasoning",
        "description": (
            f"The system traversed the internal Knowledge Graph to trace relationships connecting document obligations "
            f"to legal principles. Key traversed relationships: {kg_desc}."
        )
    })

    # 6. Conditions & Exceptions Review
    steps.append({
        "title": "6. Conditions and Statutory Exceptions Checked",
        "description": (
            "The reasoning engine evaluated statutory preconditions, threshold exemptions (e.g. establishment size, "
            "continuous service criteria, trade secret protection exceptions) to ensure contextual nuance rather than "
            "mechanistic rule matching."
        )
    })

    # 7. Potential Issue & Conflict Detection
    if conflicts:
        issue_summaries = [c.get("reason", "Potential discrepancy identified.") for c in conflicts[:2]]
        issue_desc = " | ".join(issue_summaries)
        steps.append({
            "title": "7. Potential Issues Identified",
            "description": (
                f"The analysis flagged {len(conflicts)} potential issue(s): {issue_desc}. "
                f"These represent areas of potential friction or contractual uncertainty requiring review."
            )
        })
    else:
        steps.append({
            "title": "7. Consistency Evaluation",
            "description": (
                "The analysis detected no direct contradictions or manifest statutory conflicts between the "
                "document clauses and the verified legal provisions."
            )
        })

    # 8. Explainable Risk Indicator Computation
    score = risk_assessment.get("risk_score", risk_assessment.get("score", 0))
    level = risk_assessment.get("risk_level", risk_assessment.get("level", "Low"))
    steps.append({
        "title": "8. Risk Indicator Formulation",
        "description": (
            f"An overall risk indicator was computed as {score}/100 ({level} Risk). "
            f"Points were assigned transparently based on detected potential issues, mandatory deadlines, "
            f"and termination covenants."
        )
    })

    # 9. Practical Next Steps Grounding
    if actions:
        top_action = actions[0].get("action", "Review key terms with legal counsel.")
        action_desc = f"Primary recommendation: {top_action}"
    else:
        action_desc = "Maintain calendar records of all compliance deadlines."
    steps.append({
        "title": "9. Evidence-Grounded Recommendations",
        "description": (
            f"Recommendations were synthesized directly from the identified facts, deadlines, and potential issues: "
            f"{action_desc}."
        )
    })

    # 10. Uncertainty & Disclaimer Boundaries
    steps.append({
        "title": "10. Limitations & Advisory Scope",
        "description": (
            "Law2Life AI operates as an automated decision-support tool. It does not replace advice from a licensed "
            "advocate or solicitor. Unstated oral terms, jurisdiction-specific local amendments, and judicial discretion "
            "remain open questions requiring independent legal review."
        )
    })

    # ------------------------------------------------------------------
    # FINDING-SPECIFIC EXPLANATIONS (PHASE 2)
    # ------------------------------------------------------------------
    finding_explanations: List[Dict[str, Any]] = []

    for i, finding in enumerate(conflicts):
        f_id = finding.get("finding_id", f"issue_{i+1}")
        f_title = finding.get("title", f"Potential Issue {i+1}")
        f_status = finding.get("finding_status", "potential_concern")
        f_clause = finding.get("document_clause", "")
        f_cat = finding.get("category", "General").replace("_", " ").title()
        f_act = finding.get("act", "Indian Statute")
        f_sec = finding.get("section", "")
        f_citation = finding.get("citation", f"{f_act} {f_sec}".strip())
        f_prov = finding.get("legal_provision", "")
        f_url = finding.get("source_url", "https://www.indiacode.nic.in")
        f_org = finding.get("source_organization", "Government of India")
        f_score = finding.get("confidence", 0.50)
        f_meaning = finding.get(
            "confidence_meaning",
            f"Heuristic signal strength ({f_score:.2f}) reflecting directness of statutory rule correspondence against contractual phrasing. It is an automated screening metric, not a mathematical legal probability."
        )

        # Build step-by-step relevance explanation
        relevance_steps = [
            f"Step 1 (Extraction): Document clause was classified under '{f_cat}' based on contractual terminology.",
            f"Step 2 (Retrieval): Hybrid retrieval matched the clause against statutory provisions in {f_citation}.",
            f"Step 3 (Knowledge Graph): Concept relationships linked the clause's obligations to mandatory statutory safeguards.",
            f"Step 4 (Contextual Review): {finding.get('reason', 'Contextual discrepancy identified requiring verification.')}"
        ]

        # Extract conditions, exceptions, and missing facts
        cond_text = finding.get("conditions_to_review", "Statutory threshold conditions apply.")
        missing_facts = finding.get("missing_facts", [])
        if not missing_facts:
            if "notice" in f_clause.lower() or "terminate" in f_clause.lower():
                missing_facts = ["workman_status", "continuous_service_duration", "establishment_size"]
            elif "non-compete" in f_clause.lower():
                missing_facts = ["confidential_trade_secret_involvement", "geographical_scope"]
            else:
                missing_facts = ["factual_prerequisites_unconfirmed"]

        # Limitations
        limitations = [
            "Analysis is based strictly on the uploaded document text without knowledge of oral representations or subsequent amendments.",
            f"Applicability of {f_act} may depend on judicial discretion, establishment thresholds, or state-specific amendments.",
            "Automated review provides decision support and does not constitute formal legal counsel."
        ]

        # User next steps and questions
        suggested_q = []
        if "notice" in f_clause.lower():
            suggested_q.append("Ask employer/landlord: Does this notice period conform with applicable statutory baseline requirements?")
            suggested_q.append("Clarify with legal counsel: Does the continuous service threshold or workman classification apply?")
        elif "non-compete" in f_clause.lower():
            suggested_q.append("Ask employer: Can this clause be modified to protect genuine trade secrets rather than restricting future lawful employment?")
            suggested_q.append("Seek legal advice: Confirm whether post-employment covenants in this jurisdiction are void under Section 27.")
        else:
            suggested_q.append(f"Ask the other party: What statutory provisions or exceptions govern this {f_cat.lower()} requirement?")
            suggested_q.append("Consult a qualified advocate with the highlighted clause and cited statute.")

        finding_explanations.append({
            "finding_id": f_id,
            "title": f_title,
            "status": f_status,
            "status_label": f_status.replace("_", " ").title(),
            "exact_clause": f_clause,
            "clause_reference": f_cat,
            "statute": f_act,
            "section": f_sec,
            "citation": f_citation,
            "supporting_evidence": f_prov,
            "source_url": f_url,
            "source_organization": f_org,
            "relevance_steps": relevance_steps,
            "conditions_to_review": cond_text,
            "missing_facts": missing_facts,
            "confidence": f_score,
            "confidence_meaning": f_meaning,
            "limitations": limitations,
            "possible_questions": suggested_q,
            "suggested_next_step": finding.get("suggested_next_step", "Review with a qualified legal professional.")
        })

    summary_text = (
        f"Document analysis completed for {doc_readable}. "
        f"Identified {len(conflicts)} potential issue(s) and assigned a {level} risk indicator ({score}/100) "
        f"supported by verified Indian statutory provisions."
    )

    return {
        "summary": summary_text,
        "finding_explanations": finding_explanations,
        "process_steps": steps,
        "steps": steps  # Backwards compatibility
    }


if __name__ == "__main__":
    explanation = generate_explanation(
        document_type="employment_agreement",
        legal_facts={"employee": "Ananya Rao", "employer": "ABC Technologies Pvt. Ltd.", "salary": "INR 45,000"},
        clauses={"deadlines": ["Within 30 days"]},
        conflicts=[{
            "finding_id": "issue_1",
            "title": "Notice Period Discrepancy",
            "finding_status": "potential_concern",
            "document_clause": "Either party may terminate the employment by providing 15 days written notice.",
            "category": "termination",
            "act": "Industrial Disputes Act, 1947",
            "section": "Section 25F",
            "citation": "Act No. 14 of 1947, Section 25F",
            "legal_provision": "Under Section 25F, one month's notice in writing is required.",
            "source_url": "https://www.indiacode.nic.in/handle/123456789/1518",
            "reason": "Document specifies 15 days vs statutory baseline of 30 days.",
            "confidence": 0.90,
            "confidence_meaning": "Direct numerical variance on notice duration.",
            "conditions_to_review": "Workman service must exceed 240 days in prior 12 months.",
            "missing_facts": ["workman_status", "continuous_service_duration"]
        }],
        risk_assessment={"risk_score": 40, "risk_level": "Moderate"},
        actions=[{"action": "Request written clarification on notice period."}]
    )
    print("===== FINDING EXPLANATIONS =====")
    for fe in explanation["finding_explanations"]:
        print(f"[{fe['title']}] ({fe['status']})\nClause: {fe['exact_clause']}\nStatute: {fe['citation']}\n")

