"""
Law2Life AI - Database Models and Data Access Functions
Provides functions to persist and query document analysis records.
"""

import uuid
import json
from typing import Dict, Any, Optional, List
from backend.database.connection import get_db_connection


def save_uploaded_document(
    original_filename: str,
    stored_filepath: str,
    file_type: str,
    file_size_bytes: int = 0,
    document_type: str = "unknown"
) -> str:
    """Save document metadata to the database and return the assigned ID."""
    doc_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (id, original_filename, stored_filepath, file_type, file_size_bytes, document_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (doc_id, original_filename, stored_filepath, file_type, file_size_bytes, document_type))
    conn.commit()
    conn.close()
    return doc_id


def save_analysis_record(
    document_id: Optional[str],
    document_type: str,
    summary: str,
    risk_score: int,
    risk_level: str,
    conflicts_count: int,
    clauses_count: int,
    dataset_version: str = "1.2.0"
) -> str:
    """Save an analysis execution record."""
    record_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_records (id, document_id, document_type, summary, risk_score, risk_level, conflicts_count, clauses_count, dataset_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (record_id, document_id, document_type, summary, risk_score, risk_level, conflicts_count, clauses_count, dataset_version))
    conn.commit()
    conn.close()
    return record_id


def log_question_interaction(
    document_id: Optional[str],
    question: str,
    answer: str,
    evidence: str
):
    """Log a Q&A interaction for audit and history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO question_history (document_id, question, answer, evidence)
        VALUES (?, ?, ?, ?)
    """, (document_id, question, answer, evidence))
    conn.commit()
    conn.close()


def get_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recent analysis runs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.document_type, a.summary, a.risk_score, a.risk_level,
               a.conflicts_count, a.clauses_count, a.analyzed_at,
               d.original_filename
        FROM analysis_records a
        LEFT JOIN documents d ON a.document_id = d.id
        ORDER BY a.analyzed_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_interview_answer(
    document_id: Optional[str],
    finding_id: str,
    question_id: str,
    fact_key: str,
    user_value: str,
    origin: str = "user_supplied"
) -> int:
    """Save user-supplied answer to missing-facts interview."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interview_records (document_id, finding_id, question_id, fact_key, user_value, origin)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (document_id, finding_id, question_id, fact_key, user_value, origin))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_interview_answers(
    document_id: Optional[str],
    finding_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve user-supplied interview answers for a document."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if finding_id:
        cursor.execute("""
            SELECT * FROM interview_records
            WHERE document_id = ? AND finding_id = ?
            ORDER BY answered_at ASC
        """, (document_id, finding_id))
    else:
        cursor.execute("""
            SELECT * FROM interview_records
            WHERE document_id = ?
            ORDER BY answered_at ASC
        """, (document_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_assessment_version(
    document_id: str,
    version_number: int,
    assessment_data: Dict[str, Any],
    resolved_facts: Optional[List[Dict[str, Any]]] = None,
    findings_diff: Optional[List[Dict[str, Any]]] = None
) -> int:
    """Save an assessment version with snapshot and audit diff."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_versions (document_id, version_number, assessment_json, resolved_facts_json, findings_diff_json)
        VALUES (?, ?, ?, ?, ?)
    """, (
        document_id,
        version_number,
        json.dumps(assessment_data),
        json.dumps(resolved_facts or []),
        json.dumps(findings_diff or [])
    ))
    ver_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ver_id


def get_assessment_versions(document_id: str) -> List[Dict[str, Any]]:
    """Get all assessment versions for a document."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, document_id, version_number, assessment_json, resolved_facts_json, findings_diff_json, created_at
        FROM assessment_versions
        WHERE document_id = ?
        ORDER BY version_number ASC
    """, (document_id,))
    rows = cursor.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["assessment"] = json.loads(d["assessment_json"]) if d.get("assessment_json") else {}
        d["resolved_facts"] = json.loads(d["resolved_facts_json"]) if d.get("resolved_facts_json") else []
        d["findings_diff"] = json.loads(d["findings_diff_json"]) if d.get("findings_diff_json") else []
        out.append(d)
    return out


def save_evidence_feedback(
    document_id: Optional[str],
    finding_id: Optional[str],
    provision_id: str,
    rating: str,
    rationale: Optional[str] = None
) -> int:
    """Save user feedback on a statutory evidence item (relevant/not_relevant/uncertain)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evidence_feedback (document_id, finding_id, provision_id, rating, rationale)
        VALUES (?, ?, ?, ?, ?)
    """, (document_id, finding_id, provision_id, rating, rationale or ""))
    fb_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return fb_id


def get_evidence_feedback(
    document_id: Optional[str] = None,
    provision_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve logged user feedback on statutory evidence."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if document_id and provision_id:
        cursor.execute("""
            SELECT * FROM evidence_feedback WHERE document_id = ? AND provision_id = ? ORDER BY submitted_at DESC
        """, (document_id, provision_id))
    elif document_id:
        cursor.execute("""
            SELECT * FROM evidence_feedback WHERE document_id = ? ORDER BY submitted_at DESC
        """, (document_id,))
    else:
        cursor.execute("SELECT * FROM evidence_feedback ORDER BY submitted_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

