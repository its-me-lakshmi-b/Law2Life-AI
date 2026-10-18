from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.nlp.ner import (
    extract_entities,
    extract_legal_facts
)

from backend.nlp.clause_extractor import (
    extract_clauses
)

from backend.retrieval.legal_retriever import (
    retrieve_legal_provisions
)

from backend.knowledge_graph.graph_reasoning import (
    reason_about_document
)

from backend.reasoning.conflict_detector import (
    detect_conflicts
)

from backend.reasoning.risk_engine import (
    calculate_risk
)

from backend.nlp.legal_classifier import (
    classify_document
)

from backend.reasoning.action_recommender import (
    recommend_actions
)

from backend.explainability.explanation_engine import (
    generate_explanation
)

from backend.database.models import (
    save_analysis_record
)



from typing import Optional

router = APIRouter()


class AnalysisRequest(BaseModel):
    text: str
    document_id: Optional[str] = None


# ============================================================
# SIMPLIFIED SUMMARY GENERATOR
# ============================================================

def generate_summary(
    document_type,
    legal_facts,
    clauses
):
    """
    Generate a simple human-readable summary using
    information already extracted from the document.

    This is currently rule-based.
    It does not use an external LLM.
    """

    summary_parts = []

    # --------------------------------------------------------
    # DOCUMENT TYPE
    # --------------------------------------------------------

    if document_type == "employment_agreement":

        summary_parts.append(
            "This document is an employment agreement "
            "that describes the terms and conditions of "
            "the employment relationship."
        )

    elif document_type != "unknown":

        readable_type = document_type.replace("_", " ")

        summary_parts.append(
            f"This document appears to be a {readable_type}."
        )

    else:

        summary_parts.append(
            "The document has been analyzed to identify "
            "its important legal terms, rights, obligations, "
            "and conditions."
        )

    # --------------------------------------------------------
    # PARTIES / BASIC FACTS
    # --------------------------------------------------------

    employee = legal_facts.get("employee")
    employer = legal_facts.get("employer")
    position = legal_facts.get("position")
    salary = legal_facts.get("salary")
    work_location = legal_facts.get("work_location")

    if employee and employer:

        summary_parts.append(
            f"The agreement identifies {employee} as the "
            f"employee and {employer} as the employer."
        )

    elif employee:

        summary_parts.append(
            f"The identified employee is {employee}."
        )

    elif employer:

        summary_parts.append(
            f"The identified employer is {employer}."
        )

    if position:

        summary_parts.append(
            f"The stated position is {position}."
        )

    if salary:

        summary_parts.append(
            f"The document specifies a salary or payment "
            f"amount of {salary}."
        )

    if work_location:

        summary_parts.append(
            f"The stated work location is {work_location}."
        )

    # --------------------------------------------------------
    # RIGHTS
    # --------------------------------------------------------

    rights = clauses.get("rights", [])

    if rights:

        summary_parts.append(
            f"The document contains {len(rights)} "
            "identified right-related clause"
            + ("." if len(rights) == 1 else "s.")
        )

    # --------------------------------------------------------
    # OBLIGATIONS
    # --------------------------------------------------------

    obligations = clauses.get("obligations", [])

    if obligations:

        summary_parts.append(
            f"It also contains {len(obligations)} "
            "identified obligation-related clause"
            + ("." if len(obligations) == 1 else "s.")
        )

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    payment = clauses.get("payment", [])

    if payment:

        summary_parts.append(
            "The document includes provisions relating "
            "to salary or payment."
        )

    # --------------------------------------------------------
    # LEAVE
    # --------------------------------------------------------

    leave = clauses.get("leave", [])

    if leave:

        summary_parts.append(
            "Leave entitlement and leave-related "
            "conditions are included."
        )

    # --------------------------------------------------------
    # CONFIDENTIALITY
    # --------------------------------------------------------

    confidentiality = clauses.get("confidentiality", [])

    if confidentiality:

        summary_parts.append(
            "The agreement includes confidentiality "
            "requirements concerning protected information."
        )

    # --------------------------------------------------------
    # TERMINATION
    # --------------------------------------------------------

    termination = clauses.get("termination", [])

    if termination:

        summary_parts.append(
            "The document contains provisions concerning "
            "termination of the employment relationship."
        )

    # --------------------------------------------------------
    # DEADLINES
    # --------------------------------------------------------

    deadlines = clauses.get("deadlines", [])

    if deadlines:

        summary_parts.append(
            f"{len(deadlines)} important deadline or "
            "time-related condition"
            + (" was" if len(deadlines) == 1 else "s were")
            + " identified."
        )

    # --------------------------------------------------------
    # DISPUTE RESOLUTION
    # --------------------------------------------------------

    dispute_resolution = clauses.get(
        "dispute_resolution",
        []
    )

    if dispute_resolution:

        summary_parts.append(
            "The document also contains a dispute "
            "resolution provision."
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not summary_parts:

        return (
            "The document was analyzed, but there was "
            "not enough structured information to generate "
            "a simplified summary."
        )

    return " ".join(summary_parts)


# ============================================================
# ANALYSIS REQUEST
# ============================================================

@router.post("/analyze")
async def analyze_document(
    request: AnalysisRequest
):

    text = request.text

    if not text or not text.strip():

        raise HTTPException(
            status_code=400,
            detail="No document text provided."
        )

    # ========================================================
    # 1. ENTITY EXTRACTION
    # ========================================================

    entities = extract_entities(text)

    # ========================================================
    # 2. LEGAL FACT EXTRACTION
    # ========================================================

    legal_facts = extract_legal_facts(text)

    # ========================================================
    # 3. CLAUSE EXTRACTION
    # ========================================================

    clauses = extract_clauses(text)

    # ========================================================
    # 4. DOCUMENT TYPE
    # ========================================================

    # ========================================================
    # 4. DOCUMENT TYPE & CLASSIFICATION
    # ========================================================

    classification = classify_document(text)
    document_type = classification.get("document_type", "unknown")

    # Contextual fallback if classifier is uncertain but strong facts exist
    if document_type == "unknown":
        if (
            legal_facts.get("employee")
            or legal_facts.get("employer")
            or legal_facts.get("salary")
            or legal_facts.get("notice_period")
        ):
            document_type = "employment_agreement"
        elif legal_facts.get("tenant") or legal_facts.get("landlord") or legal_facts.get("rent"):
            document_type = "rental_agreement"

    # ========================================================
    # 5. SIMPLIFIED SUMMARY
    # ========================================================

    summary = generate_summary(
        document_type,
        legal_facts,
        clauses
    )

    # ========================================================
    # 6. PREPARE CLAUSE LIST
    # ========================================================

    # Deduplicate clause_list by exact text while preserving categories
    clause_list = []
    seen_clauses = {}

    for category, items in clauses.items():
        for item in items:
            text_clean = item.strip()
            if not text_clean:
                continue
            if text_clean not in seen_clauses:
                seen_clauses[text_clean] = {
                    "category": category,
                    "categories": [category],
                    "text": text_clean
                }
            else:
                if category not in seen_clauses[text_clean]["categories"]:
                    seen_clauses[text_clean]["categories"].append(category)

    clause_list = list(seen_clauses.values())

    # ========================================================
    # 7. LEGAL PROVISION RETRIEVAL
    # ========================================================

    legal_evidence = []

    for clause in clause_list:

        retrieved_provisions = retrieve_legal_provisions(
            clause["text"],
            document_type=document_type,
            top_k=3
        )

        if retrieved_provisions:

            legal_evidence.append({
                "clause": clause["text"],
                "category": clause["category"],
                "categories": clause.get("categories", [clause["category"]]),
                "provisions": retrieved_provisions
            })

    # ========================================================
    # 8. KNOWLEDGE GRAPH REASONING
    # ========================================================

    graph_reasoning = reason_about_document(
        clause_list
    )

    # ========================================================
    # 9. POTENTIAL ISSUE DETECTION
    # ========================================================

    conflicts = detect_conflicts(
        clause_list,
        legal_evidence
    )

    # ========================================================
    # 10. RISK ASSESSMENT
    # ========================================================

    risk_assessment = calculate_risk(
        conflicts=conflicts,
        clauses=clauses,
        legal_evidence=legal_evidence
    )

    # ========================================================
    # 11. ACTION RECOMMENDATIONS
    # ========================================================

    actions = recommend_actions(
        conflicts=conflicts,
        clauses=clauses,
        legal_facts=legal_facts,
        legal_evidence=legal_evidence,
        document_type=document_type
    )

    # ========================================================
    # 12. EXPLAINABILITY ENGINE
    # ========================================================

    explanation = generate_explanation(
        document_type=document_type,
        legal_facts=legal_facts,
        clauses=clauses,
        legal_evidence=legal_evidence,
        graph_reasoning=graph_reasoning,
        conflicts=conflicts,
        risk_assessment=risk_assessment,
        actions=actions
    )

    # ========================================================
    # 13. PERSISTENCE RECORDING
    # ========================================================

    try:
        save_analysis_record(
            document_id=request.document_id,
            document_type=document_type,
            summary=summary,
            risk_score=risk_assessment.get("risk_score", 0),
            risk_level=risk_assessment.get("risk_level", "Low"),
            conflicts_count=len(conflicts),
            clauses_count=len(clause_list)
        )
    except Exception:
        # Non-blocking persistence
        pass

    # Consolidate legal evidence by stable statutory provision identity
    evidence_by_provision = {}
    for item in legal_evidence:
        clause_str = item.get("clause", "")
        for prov in item.get("provisions", []):
            pid = prov.get("provision_id", prov.get("id", ""))
            src = prov.get("source", {})
            if not pid:
                pid = f"{prov.get('act', src.get('act', ''))}_{prov.get('section', src.get('section', ''))}"

            if pid not in evidence_by_provision:
                evidence_by_provision[pid] = {
                    "provision_id": pid,
                    "title": prov.get("title", "Legal Provision"),
                    "description": prov.get("description", ""),
                    "act": prov.get("act", src.get("act", src.get("name", "Indian Statute"))),
                    "section": prov.get("section", src.get("section", "")),
                    "citation": prov.get("citation", src.get("citation", "")),
                    "source": src.get("name", prov.get("act", "Indian Statute")),
                    "url": src.get("url", ""),
                    "source_organization": src.get("source_organization", "Government of India"),
                    "verification_status": prov.get("verification_status", src.get("verification_status", "verified_statute")),
                    "conditions": prov.get("conditions", []),
                    "exceptions": prov.get("exceptions", []),
                    "clause": clause_str,
                    "supported_clauses": [clause_str] if clause_str else [],
                    "matched_keywords": list(prov.get("matched_keywords", [])),
                    "score": prov.get("score", 0),
                    "relevance_reason": prov.get("relevance_reason", "")
                }
            else:
                if clause_str and clause_str not in evidence_by_provision[pid]["supported_clauses"]:
                    evidence_by_provision[pid]["supported_clauses"].append(clause_str)
                if prov.get("score", 0) > evidence_by_provision[pid]["score"]:
                    evidence_by_provision[pid]["score"] = prov.get("score", 0)
                for kw in prov.get("matched_keywords", []):
                    if kw not in evidence_by_provision[pid]["matched_keywords"]:
                        evidence_by_provision[pid]["matched_keywords"].append(kw)

    consolidated_evidence = list(evidence_by_provision.values())

    # ========================================================
    # 14. RETURN COMPLETE ANALYSIS
    # ========================================================

    return {

        "status": "success",

        "document_id": request.document_id,

        "document_type": document_type,

        "classification": classification,

        "summary": summary,

        "entities": entities,

        "legal_facts": legal_facts,

        "clauses": clause_list,

        "rights": clauses.get(
            "rights",
            []
        ),

        "obligations": clauses.get(
            "obligations",
            []
        ),

        "deadlines": clauses.get(
            "deadlines",
            []
        ),

        "termination": clauses.get(
            "termination",
            []
        ),

        "confidentiality": clauses.get(
            "confidentiality",
            []
        ),

        "payment": clauses.get(
            "payment",
            []
        ),

        "leave": clauses.get(
            "leave",
            []
        ),

        "dispute_resolution": clauses.get(
            "dispute_resolution",
            []
        ),

        "legal_evidence": legal_evidence,

        # Internal reasoning.
        "graph_reasoning": graph_reasoning,

        # Potential issues.
        "conflicts": conflicts,

        # Risk assessment (dual keys for dashboard.js).
        "risk_assessment": risk_assessment,
        "risk": risk_assessment,

        # Evidence-grounded action recommendations.
        "actions": actions,

        # Explainability trail (finding-specific + 10-step process).
        "explanation": explanation,

        # Consolidated statutory evidence for dashboard.
        "evidence": consolidated_evidence
    }