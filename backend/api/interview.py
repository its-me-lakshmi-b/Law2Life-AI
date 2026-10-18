"""
Law2Life AI - Adaptive Missing-Facts Interview & Evidence Feedback API
Provides endpoints for:
- Fetching targeted missing-fact interview questions per finding
- Submitting interview answers, re-evaluating findings, and creating assessment versions
- Collecting user evidence feedback (relevant/not_relevant/uncertain) without altering statutory truth
- Viewing assessment versions and diff history
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.reasoning.interview_engine import (
    get_questions_for_finding,
    process_interview_submission
)
from backend.database.models import (
    save_evidence_feedback,
    get_evidence_feedback,
    get_assessment_versions,
    get_interview_answers
)

router = APIRouter()


class InterviewQuestionsRequest(BaseModel):
    finding: Dict[str, Any]
    document_id: Optional[str] = None


class InterviewSubmitRequest(BaseModel):
    document_id: Optional[str] = None
    finding_id: str
    answers: Dict[str, str]
    current_analysis: Optional[Dict[str, Any]] = None


class EvidenceFeedbackRequest(BaseModel):
    document_id: Optional[str] = None
    finding_id: Optional[str] = None
    provision_id: str
    rating: str  # "relevant", "not_relevant", "uncertain"
    rationale: Optional[str] = ""


@router.post("/interview/questions")
async def get_interview_questions(request: InterviewQuestionsRequest):
    """
    Generate targeted missing-fact questions for a specific potential issue.
    Excludes previously answered questions for the document.
    """
    finding = request.finding
    if not finding:
        raise HTTPException(status_code=400, detail="Finding object is required.")

    existing_answers = {}
    if request.document_id:
        past_records = get_interview_answers(
            document_id=request.document_id,
            finding_id=finding.get("finding_id")
        )
        for r in past_records:
            existing_answers[r["question_id"]] = r["user_value"]
            existing_answers[r["fact_key"]] = r["user_value"]

    questions = get_questions_for_finding(
        finding=finding,
        existing_answers=existing_answers
    )

    return {
        "status": "success",
        "finding_id": finding.get("finding_id"),
        "total_questions": len(questions),
        "questions": questions
    }


@router.post("/interview/submit")
async def submit_interview_answers(request: InterviewSubmitRequest):
    """
    Process user interview answers, record them with origin='user_supplied',
    re-evaluate the targeted finding, and return the versioned assessment diff.
    """
    if not request.answers:
        raise HTTPException(status_code=400, detail="No answers provided.")

    current_analysis = request.current_analysis or {}
    result = process_interview_submission(
        document_id=request.document_id or "session_doc",
        finding_id=request.finding_id,
        answers=request.answers,
        current_analysis=current_analysis
    )

    return result


@router.post("/feedback/evidence")
async def submit_evidence_feedback(request: EvidenceFeedbackRequest):
    """
    Record user feedback on a statutory evidence item (relevant, not_relevant, uncertain).
    Feedback is stored as user perspective and never alters the underlying statutory truth.
    """
    allowed_ratings = {"relevant", "not_relevant", "uncertain"}
    if request.rating not in allowed_ratings:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rating '{request.rating}'. Must be one of: {allowed_ratings}"
        )

    fb_id = save_evidence_feedback(
        document_id=request.document_id,
        finding_id=request.finding_id,
        provision_id=request.provision_id,
        rating=request.rating,
        rationale=request.rationale
    )

    return {
        "status": "success",
        "message": f"Feedback '{request.rating}' recorded for provision {request.provision_id}.",
        "feedback_id": fb_id,
        "provision_id": request.provision_id,
        "rating": request.rating
    }


@router.get("/feedback/evidence")
async def fetch_evidence_feedback(document_id: Optional[str] = None):
    """Retrieve logged evidence feedback records."""
    records = get_evidence_feedback(document_id=document_id)
    return {
        "status": "success",
        "total_feedback": len(records),
        "feedback": records
    }


@router.get("/assessment/versions")
async def fetch_assessment_versions(document_id: str):
    """Retrieve all saved assessment versions and diff history for a document."""
    if not document_id:
        raise HTTPException(status_code=400, detail="document_id parameter is required.")

    versions = get_assessment_versions(document_id=document_id)
    return {
        "status": "success",
        "document_id": document_id,
        "total_versions": len(versions),
        "versions": versions
    }
