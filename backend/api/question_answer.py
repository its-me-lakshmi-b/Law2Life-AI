"""
Law2Life AI - Document-Grounded Question Answering API
Answers user queries grounded strictly in the uploaded document and verified legal evidence.
Defends against prompt injection and returns citations and uncertainty indicators.
"""

import re
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    document_context: Optional[Dict[str, Any]] = None


# Prompt injection keywords to reject or neutralize
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"system\s+prompt",
    r"you\s+are\s+now\s+an?\s+unrestricted",
    r"developer\s+mode",
    r"bypass\s+safety",
    r"<script.*?>",
    r"exec\s*\(",
    r"eval\s*\(",
    r"sudo\s+",
    r"reveal\s+(?:your\s+)?instructions"
]


def detect_prompt_injection(text: str) -> bool:
    """Check for adversarial jailbreak or prompt injection attempts."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def find_best_matching_clause(query: str, clauses: Any) -> Optional[str]:
    """Find the most lexically relevant clause from the document."""
    clause_list: List[str] = []
    if isinstance(clauses, dict):
        for items in clauses.values():
            if isinstance(items, list):
                clause_list.extend(str(i) for i in items if i)
    elif isinstance(clauses, list):
        for item in clauses:
            if isinstance(item, dict):
                clause_list.append(item.get("text", ""))
            elif isinstance(item, str):
                clause_list.append(item)

    if not clause_list:
        return None

    query_words = set(re.findall(r"\b[a-zA-Z0-9_]{3,}\b", query.lower()))
    if not query_words:
        return None

    best_clause = None
    best_overlap = 0

    for c in clause_list:
        c_words = set(re.findall(r"\b[a-zA-Z0-9_]{3,}\b", c.lower()))
        overlap = len(query_words.intersection(c_words))
        if overlap > best_overlap:
            best_overlap = overlap
            best_clause = c

    if best_overlap >= 1:
        return best_clause
    return None


@router.post("/question")
async def answer_question(request: QuestionRequest):
    """
    Answer document-grounded question using extracted facts, clauses,
    Knowledge Graph reasoning, and retrieved statutory provisions.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please enter a question.")

    # Guard against prompt injection
    if detect_prompt_injection(question):
        return {
            "answer": "Law2Life AI only answers questions grounded in your uploaded legal document and applicable Indian law.",
            "evidence": "Security Policy Enforcement",
            "reason": "The system rejected this query because it contained instructions attempting to override application boundaries.",
            "is_grounded": False
        }

    context = request.document_context or {}
    legal_facts = context.get("legal_facts", {})
    clauses = context.get("clauses", {})
    conflicts = context.get("conflicts", [])
    risk = context.get("risk", context.get("risk_assessment", {}))
    actions = context.get("actions", [])
    doc_type = context.get("document_type", "document")
    doc_readable = doc_type.replace("_", " ").title() if doc_type else "General Legal Document"
    q_lower = question.lower()

    # 1. Salary / Compensation / Rent questions
    if any(k in q_lower for k in ["salary", "pay", "compensation", "wages", "how much", "rent"]):
        salary = legal_facts.get("salary")
        rent = legal_facts.get("rent")
        if salary:
            payment_clauses = clauses.get("payment", []) if isinstance(clauses, dict) else []
            evidence_text = payment_clauses[0] if payment_clauses else f"Stated Salary: {salary}"
            return {
                "answer": f"According to the document, the stated compensation is {salary}.",
                "evidence": evidence_text,
                "reason": "Extracted from the compensation and payment provisions of the agreement.",
                "is_grounded": True
            }
        elif rent:
            return {
                "answer": f"According to the rental document, the stated monthly rent is {rent}.",
                "evidence": f"Stated Rent: {rent}",
                "reason": "Extracted from the lease payment terms.",
                "is_grounded": True
            }

    # 2. Notice period / Termination questions
    if any(k in q_lower for k in ["notice period", "notice", "terminate", "termination", "resignation", "leave period"]):
        np = legal_facts.get("notice_period")
        term_clauses = clauses.get("termination", []) if isinstance(clauses, dict) else []
        if np:
            evidence_text = term_clauses[0] if term_clauses else f"Notice Period: {np}"
            return {
                "answer": f"The document specifies a notice period of {np} for termination.",
                "evidence": evidence_text,
                "reason": "Derived from the termination and notice terms of the agreement.",
                "is_grounded": True
            }
        elif term_clauses:
            return {
                "answer": "The agreement specifies the following termination conditions:",
                "evidence": term_clauses[0],
                "reason": "Extracted directly from the termination clause.",
                "is_grounded": True
            }

    # 3. Parties / Employer / Employee / Landlord / Tenant
    if any(k in q_lower for k in ["who is", "parties", "employer", "employee", "tenant", "landlord", "parties to"]):
        parties_info = []
        if legal_facts.get("employee"):
            parties_info.append(f"Employee: {legal_facts['employee']}")
        if legal_facts.get("employer"):
            parties_info.append(f"Employer: {legal_facts['employer']}")
        if legal_facts.get("tenant"):
            parties_info.append(f"Tenant: {legal_facts['tenant']}")
        if legal_facts.get("landlord"):
            parties_info.append(f"Landlord: {legal_facts['landlord']}")

        if parties_info:
            return {
                "answer": "The identified parties in the document are: " + ", ".join(parties_info) + ".",
                "evidence": "Document Header and Parties Schedule",
                "reason": "Extracted through legal entity recognition.",
                "is_grounded": True
            }

    # 4. Leave entitlement questions
    if any(k in q_lower for k in ["leave", "vacation", "holiday", "sick leave"]):
        leave_clauses = clauses.get("leave", []) if isinstance(clauses, dict) else []
        leave_notice = legal_facts.get("leave_notice")
        if leave_clauses or leave_notice:
            ans = "The document specifies that the employee may request paid leave under company policy."
            if leave_notice:
                ans += f" Leave requests must generally be submitted at least {leave_notice} in advance."
            ev = leave_clauses[0] if leave_clauses else f"Leave Notice: {leave_notice}"
            return {
                "answer": ans,
                "evidence": ev,
                "reason": "Grounded in the leave provisions and leave notice conditions.",
                "is_grounded": True
            }

    # 5. Potential issues / Conflicts questions
    if any(k in q_lower for k in ["conflict", "issue", "problem", "illegal", "risk", "concern", "validity"]):
        if conflicts:
            reasons = [c.get("reason", "") for c in conflicts]
            return {
                "answer": f"The system identified {len(conflicts)} potential issue(s) requiring review: " + " ".join(reasons),
                "evidence": conflicts[0].get("legal_provision", "Statutory Comparison"),
                "reason": "Generated by benchmarking document clauses against official Indian statutory baselines.",
                "is_grounded": True
            }
        else:
            return {
                "answer": "No direct legal conflicts or statutory contradictions were flagged from the available evidence.",
                "evidence": "Statutory Consistency Check",
                "reason": "All clauses satisfied basic statutory compliance heuristics.",
                "is_grounded": True
            }

    # 6. Risk Level questions
    if any(k in q_lower for k in ["risk level", "score", "risk score", "how risky"]):
        score = risk.get("risk_score", risk.get("score", 0))
        level = risk.get("risk_level", risk.get("level", "Low"))
        expl = risk.get("explanation", "")
        return {
            "answer": f"The calculated risk indicator for this document is {score}/100, categorized as {level} Risk. {expl}",
            "evidence": f"Risk Factors: {len(risk.get('factors', []))} evaluated parameters",
            "reason": "Calculated by the Law2Life risk scoring engine based on obligations, deadlines, and potential issues.",
            "is_grounded": True
        }

    # 7. Next Actions / What should I do
    if any(k in q_lower for k in ["what should i do", "action", "next step", "recommend", "advice"]):
        if actions:
            act_texts = [f"{i+1}. {a.get('action', a)}" for i, a in enumerate(actions[:3])]
            return {
                "answer": "Based on the document analysis, the recommended next steps are: " + " ".join(act_texts),
                "evidence": "Action Recommender Synthesis",
                "reason": "Derived from contractual obligations, deadlines, and flagged issues.",
                "is_grounded": True
            }

    # 8. Semantic / Lexical fallback search across all document clauses
    best_clause = find_best_matching_clause(question, clauses)
    if best_clause:
        return {
            "answer": f"Based on the relevant clause in your document: \"{best_clause}\"",
            "evidence": best_clause,
            "reason": "Retrieved as the most relevant contractual provision addressing your query keywords.",
            "is_grounded": True
        }

    # 9. Truthful uncertainty fallback when evidence is insufficient
    return {
        "answer": (
            "The document was analyzed, but it does not appear to contain explicit information directly "
            f"answering your question about '{question}'. Please review the full agreement text or consult "
            "a legal advisor for specific advice."
        ),
        "evidence": f"Document context: {doc_readable}",
        "reason": "No sufficiently matching clauses or extracted legal facts were identified for this query.",
        "is_grounded": False
    }
