"""
Law2Life AI - Adaptive Missing-Facts Interview Engine
Deterministically identifies missing material facts for a flagged finding,
generates targeted structured follow-up questions, records user-supplied facts
with explicit origin tags, re-evaluates findings, and maintains versioned audit diffs.
"""

from typing import Dict, List, Any, Optional
from backend.database.models import (
    save_interview_answer,
    get_interview_answers,
    save_assessment_version,
    get_assessment_versions
)


# Canonical Question Catalog mapped to statutory prerequisite fact keys
FACT_QUESTION_CATALOG: Dict[str, Dict[str, Any]] = {
    "continuous_service_duration": {
        "question_id": "q_continuous_service",
        "fact_key": "continuous_service_duration",
        "prompt": "Has the employee completed at least 240 days (approx. 1 year) of continuous service with the employer?",
        "options": [
            "Yes (more than 240 days)",
            "No (less than 240 days / new joinee)",
            "Unsure / Under initial probation"
        ],
        "statutory_basis": "Section 25F, Industrial Disputes Act, 1947",
        "materiality": (
            "Under Section 25F of the Industrial Disputes Act, 1947, statutory retrenchment notice protections "
            "apply only to workmen with not less than 240 days of continuous service in the preceding 12 months."
        )
    },
    "workman_status": {
        "question_id": "q_workman_status",
        "fact_key": "workman_status",
        "prompt": "What is the primary operational nature of the employee's duties under this engagement?",
        "options": [
            "Operational, technical, clerical or manual (Workman)",
            "Managerial, administrative or executive (Non-workman)",
            "Supervisory (earning above statutory wage threshold)"
        ],
        "statutory_basis": "Section 2(s), Industrial Disputes Act, 1947",
        "materiality": (
            "Managerial and senior administrative employees are generally exempt from Section 25F retrenchment "
            "protections; their termination is governed by contractual common law."
        )
    },
    "establishment_size": {
        "question_id": "q_establishment_size",
        "fact_key": "establishment_size",
        "prompt": "Approximately how many total workmen/employees are employed across the employer's establishment?",
        "options": [
            "100 or more employees (or 300+ in certain industrial states)",
            "Fewer than 100 employees",
            "Unsure"
        ],
        "statutory_basis": "Chapter V-B, Industrial Disputes Act, 1947",
        "materiality": (
            "Establishments with 100+ workmen are subject to Chapter V-B special retrenchment procedures "
            "(requiring 3 months' notice and prior government permission)."
        )
    },
    "scope_of_confidentiality": {
        "question_id": "q_confidentiality_scope",
        "fact_key": "scope_of_confidentiality",
        "prompt": "Does the restricted role involve access to genuine proprietary trade secrets, secret algorithms, or patents?",
        "options": [
            "Yes (direct access to proprietary technical trade secrets / patents)",
            "No (standard industry knowledge / general commercial sales experience)",
            "Unsure"
        ],
        "statutory_basis": "Section 27, Indian Contract Act, 1872",
        "materiality": (
            "While broad post-employment non-compete restraints are void under Section 27, confidentiality covenants "
            "protecting genuine trade secrets remain legally enforceable in India."
        )
    },
    "establishment_size_pwa": {
        "question_id": "q_pwa_headcount",
        "fact_key": "establishment_size_pwa",
        "prompt": "Does the employer's establishment employ 1,000 or more persons?",
        "options": [
            "Less than 1,000 employees (7th day statutory wage deadline)",
            "1,000 or more employees (10th day statutory wage deadline)",
            "Unsure"
        ],
        "statutory_basis": "Section 5, Payment of Wages Act, 1936",
        "materiality": (
            "Wages must be disbursed before the expiry of the 7th day for establishments under 1,000 persons, "
            "or 10th day for larger establishments."
        )
    },
    "lease_purpose": {
        "question_id": "q_lease_purpose",
        "fact_key": "lease_purpose",
        "prompt": "What is the primary permitted use of the leased immovable property?",
        "options": [
            "Residential / Commercial (15 days' notice baseline)",
            "Manufacturing / Agricultural (6 months' notice baseline)",
            "Unsure"
        ],
        "statutory_basis": "Section 106, Transfer of Property Act, 1882",
        "materiality": (
            "Section 106 establishes a 15-day notice baseline for residential/commercial leases vs 6 months "
            "for agricultural/manufacturing leases where contract or local law is silent."
        )
    }
}


def get_questions_for_finding(
    finding: Dict[str, Any],
    existing_answers: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Select targeted, relevant questions for a specific potential issue.
    Excludes already answered questions and attaches origin and materiality metadata.
    """
    existing_answers = existing_answers or {}
    questions = []

    missing_keys = finding.get("missing_facts", [])
    clause_text = finding.get("document_clause", "").lower()
    cat = finding.get("category", "").lower()
    act = finding.get("act", "").lower()

    # Fallback missing key inference if not explicitly provided
    if not missing_keys:
        if "notice" in clause_text or "terminate" in clause_text or "retrench" in clause_text:
            missing_keys = ["continuous_service_duration", "workman_status"]
        elif "non-compete" in clause_text or "restraint" in clause_text:
            missing_keys = ["scope_of_confidentiality"]
        elif "salary" in clause_text or "wages" in clause_text:
            missing_keys = ["establishment_size_pwa"]
        elif "lease" in clause_text or "rent" in clause_text:
            missing_keys = ["lease_purpose"]

    for key in missing_keys:
        if key in FACT_QUESTION_CATALOG:
            q_meta = dict(FACT_QUESTION_CATALOG[key])
            qid = q_meta["question_id"]

            is_answered = qid in existing_answers or key in existing_answers
            user_val = existing_answers.get(qid, existing_answers.get(key))

            q_meta["is_answered"] = is_answered
            q_meta["user_answer"] = user_val
            q_meta["fact_origin"] = "user_supplied" if is_answered else "unanswered"
            questions.append(q_meta)

    return questions


def reevaluate_finding_with_user_facts(
    finding: Dict[str, Any],
    user_facts: Dict[str, str]
) -> Dict[str, Any]:
    """
    Deterministically re-evaluate a finding when new user-supplied facts are provided.
    Does not guess or invent facts; explicitly notes which conditions were modified.
    """
    updated_finding = dict(finding)
    finding_id = finding.get("finding_id", "issue_1")
    title = finding.get("title", "")
    orig_status = finding.get("finding_status", "potential_concern")
    orig_conf = finding.get("confidence", 0.50)

    change_notes = []
    resolved_keys = []

    # 1. EVALUATE CONTINUOUS SERVICE ANSWER
    cs_ans = user_facts.get("continuous_service_duration") or user_facts.get("q_continuous_service")
    if cs_ans:
        resolved_keys.append("continuous_service_duration")
        if "No" in cs_ans or "less than 240" in cs_ans:
            updated_finding["finding_status"] = "statutory_prerequisite_not_met"
            updated_finding["status_label"] = "Prerequisite Not Met"
            updated_finding["confidence"] = 0.85
            updated_finding["reason"] = (
                f"User-supplied fact confirms continuous service is under 240 days. Therefore, statutory retrenchment "
                f"notice protections under Section 25F of the Industrial Disputes Act, 1947 do not mandate 30 days notice for this engagement. "
                f"Contractual notice terms govern, subject to any local State Shops and Commercial Establishments Act baselines (which may require shorter service thresholds)."
            )
            change_notes.append("Continuous service prerequisite (< 240 days) not satisfied for Section 25F IDA mandatory retrenchment notice. State Shops Act thresholds remain an open consideration.")
        elif "Yes" in cs_ans or "more than 240" in cs_ans:
            updated_finding["finding_status"] = "statutory_protection_confirmed"
            updated_finding["status_label"] = "Statutory Condition Confirmed"
            updated_finding["confidence"] = 0.92
            updated_finding["reason"] = (
                f"User-supplied fact confirms employee has completed > 240 days continuous service. Section 25F IDA "
                f"retrenchment protections apply if workman criteria are met. Contractual notice difference is an active issue."
            )
            change_notes.append("Continuous service prerequisite (>= 240 days) confirmed. Retrenchment rules apply.")

    # 2. EVALUATE WORKMAN STATUS ANSWER
    wm_ans = user_facts.get("workman_status") or user_facts.get("q_workman_status")
    if wm_ans:
        resolved_keys.append("workman_status")
        if "Managerial" in wm_ans or "Executive" in wm_ans:
            updated_finding["finding_status"] = "statutory_exemption_applies"
            updated_finding["status_label"] = "Managerial Exemption Applies"
            updated_finding["confidence"] = 0.85
            updated_finding["reason"] = (
                "User-supplied fact confirms the role is managerial/executive. Under Indian labour jurisprudence, "
                "managerial employees are not 'workmen' under Section 2(s) IDA. Contractual terms govern rather than Section 25F."
            )
            change_notes.append("Managerial classification exempts employee from Section 25F retrenchment protection.")
        elif "Workman" in wm_ans:
            change_notes.append("Workman classification confirmed under Section 2(s) Industrial Disputes Act.")

    # 3. EVALUATE NON-COMPETE CONFIDENTIALITY ANSWER
    nc_ans = user_facts.get("scope_of_confidentiality") or user_facts.get("q_confidentiality_scope")
    if nc_ans:
        resolved_keys.append("scope_of_confidentiality")
        if "Yes" in nc_ans or "trade secrets" in nc_ans:
            change_notes.append("Legitimate proprietary trade secret interest identified. Non-disclosure covenants are valid, but post-employment work ban remains void under Section 27.")
        else:
            change_notes.append("No specialized trade secrets involved. Post-employment non-compete is strictly void under Section 27.")

    return {
        "finding": updated_finding,
        "resolved_keys": resolved_keys,
        "change_notes": change_notes,
        "status_before": orig_status,
        "status_after": updated_finding.get("finding_status", orig_status),
        "confidence_before": orig_conf,
        "confidence_after": updated_finding.get("confidence", orig_conf)
    }


def process_interview_submission(
    document_id: str,
    finding_id: str,
    answers: Dict[str, str],
    current_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Record user interview answers, re-evaluate relevant findings, create an assessment version,
    and return the audit comparison diff.
    """
    # 1. Save answers to database with origin="user_supplied"
    for q_or_fact_key, answer_val in answers.items():
        # Match to fact key
        fact_key = q_or_fact_key
        qid = q_or_fact_key
        for f_key, q_data in FACT_QUESTION_CATALOG.items():
            if q_data["question_id"] == q_or_fact_key or f_key == q_or_fact_key:
                fact_key = f_key
                qid = q_data["question_id"]
                break

        save_interview_answer(
            document_id=document_id,
            finding_id=finding_id,
            question_id=qid,
            fact_key=fact_key,
            user_value=str(answer_val),
            origin="user_supplied"
        )

    # 2. Re-evaluate the target finding
    conflicts = current_analysis.get("conflicts", [])
    target_finding = None
    target_idx = -1

    for idx, c in enumerate(conflicts):
        if c.get("finding_id") == finding_id:
            target_finding = c
            target_idx = idx
            break

    if not target_finding and conflicts:
        target_finding = conflicts[0]
        target_idx = 0

    eval_result = {}
    if target_finding:
        eval_result = reevaluate_finding_with_user_facts(target_finding, answers)
        # Update the finding in the analysis copy
        conflicts[target_idx] = eval_result["finding"]

    # 3. Compile resolved facts and origin tracking
    resolved_facts = []
    for k, v in answers.items():
        resolved_facts.append({
            "fact_key": k,
            "value": v,
            "origin": "user_supplied",
            "statutory_basis": FACT_QUESTION_CATALOG.get(k, {}).get("statutory_basis", "User Interview")
        })

    # 4. Determine assessment version number
    past_versions = get_assessment_versions(document_id) if document_id else []
    new_version_num = len(past_versions) + 1

    findings_diff = [{
        "finding_id": finding_id,
        "status_before": eval_result.get("status_before", "potential_concern"),
        "status_after": eval_result.get("status_after", "potential_concern"),
        "confidence_before": eval_result.get("confidence_before", 0.50),
        "confidence_after": eval_result.get("confidence_after", 0.50),
        "change_notes": eval_result.get("change_notes", ["Finding re-evaluated with user-supplied context."])
    }]

    # 5. Persist versioned snapshot
    if document_id:
        save_assessment_version(
            document_id=document_id,
            version_number=new_version_num,
            assessment_data=current_analysis,
            resolved_facts=resolved_facts,
            findings_diff=findings_diff
        )

    return {
        "status": "success",
        "version_number": new_version_num,
        "finding_id": finding_id,
        "updated_finding": eval_result.get("finding", target_finding),
        "resolved_facts": resolved_facts,
        "findings_diff": findings_diff,
        "remaining_uncertainties": [
            k for k in target_finding.get("missing_facts", [])
            if k not in eval_result.get("resolved_keys", [])
        ] if target_finding else []
    }
