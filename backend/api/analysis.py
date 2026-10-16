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


router = APIRouter()


class AnalysisRequest(BaseModel):
    text: str


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

    document_type = "unknown"

    if (
        legal_facts.get("employee")
        or legal_facts.get("employer")
        or legal_facts.get("salary")
        or legal_facts.get("notice_period")
    ):

        document_type = "employment_agreement"

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

    clause_list = []

    for category, items in clauses.items():

        for item in items:

            clause_list.append({
                "category": category,
                "text": item
            })

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
    # 11. RETURN COMPLETE ANALYSIS
    # ========================================================

    return {

        "status": "success",

        "document_type": document_type,

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
        # This remains available to the backend but is
        # not displayed as a Knowledge Graph to the user.
        "graph_reasoning": graph_reasoning,

        # Potential issues.
        "conflicts": conflicts,

        # New risk assessment.
        "risk_assessment": risk_assessment,

        # Flattened evidence for the dashboard.
        "evidence": [

            {
                "title": provision.get(
                    "title",
                    "Legal Provision"
                ),

                "description": provision.get(
                    "description",
                    ""
                ),

                "source": provision.get(
                    "source",
                    {}
                ).get(
                    "name",
                    "Source not specified"
                ),

                "clause": item.get(
                    "clause",
                    ""
                ),

                "matched_keywords": provision.get(
                    "matched_keywords",
                    []
                ),

                "score": provision.get(
                    "score",
                    0
                )
            }

            for item in legal_evidence

            for provision in item.get(
                "provisions",
                []
            )
        ]
    }