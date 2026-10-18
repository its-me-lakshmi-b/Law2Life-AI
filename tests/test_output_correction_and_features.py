"""
Regression and Feature Verification Tests for Law2Life AI Upgrades:
- Phase 1: Output Deduplication & Semantic Numeric Handling (240 continuous service vs 30 notice days)
- Phase 2: Finding-Specific Explainability (9 mandatory criteria)
- Phase 3: Distinction between Explanation and Document-Grounded Ask Question
- Phase 4: Legal Dataset Audit & Runtime Loading
- Phase 5: Adaptive Missing-Facts Interview & Assessment Versioning
- Phase 6: Traceable Evidence Feedback
"""

import unittest
from fastapi.testclient import TestClient

from backend.main import app
from backend.reasoning.conflict_detector import (
    extract_legal_quantities,
    analyze_clause_against_provision,
    detect_conflicts
)
from backend.explainability.explanation_engine import generate_explanation
from backend.reasoning.interview_engine import (
    get_questions_for_finding,
    reevaluate_finding_with_user_facts,
    process_interview_submission
)
from backend.retrieval.legal_retriever import load_legal_provisions
from backend.knowledge_graph.graph_builder import load_relationships
from backend.database.models import (
    save_interview_answer,
    get_interview_answers,
    save_assessment_version,
    get_assessment_versions,
    save_evidence_feedback,
    get_evidence_feedback
)


class TestOutputCorrectionAndFeatures(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # ========================================================
    # PHASE 1: DEDUPLICATION & NUMERIC CONCEPT DIFFERENTIATION
    # ========================================================

    def test_extract_legal_quantities_differentiates_concepts(self):
        """Test that notice days and continuous service days are extracted into separate concepts."""
        text_ida = (
            "Under Section 25F of the Industrial Disputes Act, 1947, no workman employed in any "
            "industry who has been in continuous service for not less than one year shall be retrenched "
            "until the workman has been given one month's notice in writing... "
            "Conditions: Applicable to workmen with continuous service of not less than 240 days."
        )
        quantities = extract_legal_quantities(text_ida)
        self.assertEqual(quantities.get("notice_days"), 30)
        self.assertEqual(quantities.get("continuous_service_days"), 240)

    def test_no_false_conflict_between_30_days_notice_and_240_days_service(self):
        """
        Regression test: Verify that a contract specifying 30 days notice is NOT falsely flagged
        as a numeric conflict against Section 25F continuous service threshold of 240 days.
        """
        clause = "Either party may terminate the employment by providing 30 days written notice."
        provision = (
            "Conditions Precedent to Retrenchment and Notice. Under Section 25F of the Industrial Disputes "
            "Act, 1947, no workman who has been in continuous service for not less than one year shall be "
            "retrenched until given one month's notice in writing. Conditions: continuous service of not less than 240 days."
        )
        finding = analyze_clause_against_provision(clause, provision, clause_category="termination")
        # Notice is 30 days vs 1 month (30 days) -> Notice durations match!
        # The 240 days continuous service is a prerequisite, NOT a conflicting notice duration.
        if finding:
            self.assertNotEqual(
                finding.get("conflict_type"),
                "direct_numeric_conflict",
                "Continuous service 240 days was falsely compared against 30 days notice!"
            )

    def test_genuine_numeric_notice_mismatch_detected(self):
        """Test that genuine notice differences (e.g. 15 days vs 30 days) on the same concept ARE detected."""
        clause = "Either party may terminate the employment by providing 15 days written notice."
        provision = (
            "Conditions Precedent to Retrenchment and Notice. Under Section 25F of the Industrial Disputes "
            "Act, 1947, no workman shall be retrenched until given one month's notice in writing (30 days)."
        )
        finding = analyze_clause_against_provision(clause, provision, clause_category="termination")
        self.assertIsNotNone(finding)
        self.assertEqual(finding.get("conflict_type"), "direct_numeric_conflict")
        self.assertIn("15", finding.get("title", ""))
        self.assertIn("30", finding.get("title", ""))

    def test_conflict_deduplication(self):
        """Test that detect_conflicts does not append duplicate findings for the same clause and provision."""
        clauses = [
            {"category": "termination", "text": "Either party may terminate the employment by providing 15 days written notice."},
            {"category": "rights", "text": "Either party may terminate the employment by providing 15 days written notice."}
        ]
        legal_evidence = [
            {
                "clause": "Either party may terminate the employment by providing 15 days written notice.",
                "provisions": [
                    {
                        "provision_id": "IND_IDA_S25F",
                        "title": "Conditions Precedent to Retrenchment",
                        "description": "Requires one month's notice in writing (30 days).",
                        "conditions": "Continuous service 240 days.",
                        "exceptions": "Excludes voluntary retirement.",
                        "source": {"act": "Industrial Disputes Act, 1947", "section": "Section 25F"}
                    }
                ]
            }
        ]
        conflicts = detect_conflicts(clauses, legal_evidence)
        # Even though clause appeared in two categories, finding must be deduplicated
        self.assertEqual(len(conflicts), 1)

    # ========================================================
    # PHASE 2: FINDING-SPECIFIC EXPLANATION
    # ========================================================

    def test_finding_specific_explanation_9_elements(self):
        """Test that generate_explanation produces finding_explanations containing all 9 required elements."""
        conflicts = [{
            "finding_id": "issue_1",
            "title": "Notice Period Discrepancy (15 days vs 30 days)",
            "finding_status": "potential_concern",
            "document_clause": "Either party may terminate the employment by providing 15 days written notice.",
            "category": "termination",
            "act": "Industrial Disputes Act, 1947",
            "section": "Section 25F",
            "citation": "Act No. 14 of 1947, Section 25F",
            "legal_provision": "Under Section 25F, one month's notice in writing (30 days) is required for retrenchment.",
            "source_url": "https://www.indiacode.nic.in/handle/123456789/1518",
            "source_organization": "Ministry of Labour and Employment, Government of India",
            "reason": "Contractual notice of 15 days is less than statutory 30 days baseline for workmen.",
            "confidence": 0.90,
            "confidence_meaning": "Direct numerical variance on notice duration.",
            "conditions_to_review": "Workman service must exceed 240 days in prior 12 months.",
            "missing_facts": ["workman_status", "continuous_service_duration"],
            "suggested_next_step": "Review with legal counsel whether employee qualifies as a workman."
        }]
        expl = generate_explanation(
            document_type="employment_agreement",
            legal_facts={"employee": "Ananya Rao", "employer": "Tech Corp"},
            clauses={"termination": ["15 days written notice"]},
            conflicts=conflicts,
            risk_assessment={"risk_score": 50, "risk_level": "Moderate"}
        )

        self.assertIn("finding_explanations", expl)
        self.assertEqual(len(expl["finding_explanations"]), 1)
        fe = expl["finding_explanations"][0]

        # 1. Finding title and status
        self.assertEqual(fe["title"], "Notice Period Discrepancy (15 days vs 30 days)")
        self.assertEqual(fe["status"], "potential_concern")
        # 2. Exact document clause and reference
        self.assertEqual(fe["exact_clause"], "Either party may terminate the employment by providing 15 days written notice.")
        self.assertEqual(fe["clause_reference"], "Termination")
        # 3. Applicable legal source, statute and section
        self.assertEqual(fe["statute"], "Industrial Disputes Act, 1947")
        self.assertEqual(fe["section"], "Section 25F")
        # 4. Retrieved supporting evidence and source URL
        self.assertIn("Section 25F", fe["supporting_evidence"])
        self.assertIn("indiacode.nic.in", fe["source_url"])
        # 5. Step-by-step explanation of why evidence is relevant
        self.assertTrue(len(fe["relevance_steps"]) >= 4)
        # 6. Applicable conditions, exceptions and missing facts
        self.assertIn("240 days", fe["conditions_to_review"])
        self.assertTrue("workman_status" in fe["missing_facts"])
        # 7. Confidence or evidence-strength information with truthful explanation
        self.assertEqual(fe["confidence"], 0.90)
        self.assertTrue(len(fe["confidence_meaning"]) > 10)
        # 8. Limitations and reasons finding may be uncertain
        self.assertTrue(len(fe["limitations"]) >= 2)
        # 9. Possible questions or next steps for the user
        self.assertTrue(len(fe["possible_questions"]) >= 2)
        self.assertTrue(len(fe["suggested_next_step"]) > 5)

    # ========================================================
    # PHASE 3: DISTINCTION BETWEEN EXPLANATION AND ASK QUESTION
    # ========================================================

    def test_ask_question_grounded_answer(self):
        """Test that Ask Question returns document-grounded answers with citations."""
        response = self.client.post("/api/question", json={
            "question": "What is the notice period in this agreement?",
            "document_context": {
                "document_type": "employment_agreement",
                "legal_facts": {"notice_period": "30 days"},
                "clauses": {"termination": ["Either party may terminate by providing 30 days written notice."]}
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_grounded"])
        self.assertIn("30 days", data["answer"])
        self.assertIn("termination", data["reason"].lower())

    def test_ask_question_uncertainty_fallback(self):
        """Test that an unanswerable question triggers the uncertainty fallback safely."""
        response = self.client.post("/api/question", json={
            "question": "Does this company provide stock options or equity grants?",
            "document_context": {
                "document_type": "employment_agreement",
                "legal_facts": {},
                "clauses": {}
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_grounded"])
        self.assertIn("does not appear to contain explicit information", data["answer"])

    # ========================================================
    # PHASE 4: DATASET AUDIT & RUNTIME USAGE
    # ========================================================

    def test_dataset_record_counts_and_provenance(self):
        """Audit test: Verify exact counts (10 provisions, 42 relationships) and provenance fields."""
        provisions = load_legal_provisions()
        relationships = load_relationships()

        self.assertEqual(len(provisions), 10)
        self.assertEqual(len(relationships), 42)

        for p in provisions:
            src = p.get("source", {})
            self.assertTrue(p.get("provision_id"))
            self.assertTrue(p.get("title"))
            self.assertTrue(src.get("url", "").startswith("https://www.indiacode.nic.in"))
            self.assertEqual(src.get("jurisdiction"), "India")
            self.assertEqual(src.get("verification_status"), "verified_statute")

    # ========================================================
    # PHASE 5: ADAPTIVE MISSING-FACTS INTERVIEW
    # ========================================================

    def test_interview_question_generation_and_origin_tagging(self):
        """Test that targeted questions are generated for missing material facts with origin tags."""
        finding = {
            "finding_id": "issue_1",
            "title": "Notice Period Discrepancy",
            "document_clause": "Either party may terminate the employment by providing 15 days written notice.",
            "missing_facts": ["continuous_service_duration", "workman_status"]
        }
        questions = get_questions_for_finding(finding)
        self.assertTrue(len(questions) >= 2)
        q_keys = [q["fact_key"] for q in questions]
        self.assertIn("continuous_service_duration", q_keys)
        self.assertIn("workman_status", q_keys)
        for q in questions:
            self.assertEqual(q["fact_origin"], "unanswered")
            self.assertTrue(len(q["options"]) >= 2)

    def test_interview_reevaluation_prerequisite_not_met(self):
        """
        Test that when user supplies fact that continuous service is < 240 days,
        the finding status transitions to prerequisite_not_met and does not assert a violation.
        """
        finding = {
            "finding_id": "issue_1",
            "title": "Notice Period Discrepancy",
            "finding_status": "potential_concern",
            "confidence": 0.90,
            "document_clause": "Either party may terminate the employment by providing 15 days written notice.",
            "missing_facts": ["continuous_service_duration"]
        }
        user_facts = {"continuous_service_duration": "No (less than 240 days / new joinee)"}
        eval_result = reevaluate_finding_with_user_facts(finding, user_facts)

        self.assertEqual(eval_result["status_after"], "statutory_prerequisite_not_met")
        self.assertIn("Continuous service prerequisite", eval_result["change_notes"][0])

    def test_interview_submission_preserves_extracted_facts(self):
        """
        Test that submitting interview answers stores user_supplied facts separately
        and does NOT overwrite extracted facts in the document context.
        """
        doc_id = "test_doc_interview_audit"
        finding_id = "issue_1"
        analysis_state = {
            "document_id": doc_id,
            "legal_facts": {"salary": "INR 50,000", "notice_period": "15 days"},
            "conflicts": [{
                "finding_id": "issue_1",
                "title": "Notice Period Discrepancy",
                "finding_status": "potential_concern",
                "document_clause": "Either party may terminate the employment by providing 15 days written notice.",
                "missing_facts": ["continuous_service_duration"]
            }]
        }
        result = process_interview_submission(
            document_id=doc_id,
            finding_id=finding_id,
            answers={"continuous_service_duration": "No (less than 240 days / new joinee)"},
            current_analysis=analysis_state
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["version_number"] >= 1)

        # Verify extracted facts are unchanged
        self.assertEqual(analysis_state["legal_facts"]["salary"], "INR 50,000")
        self.assertEqual(analysis_state["legal_facts"]["notice_period"], "15 days")

        # Verify database record has origin="user_supplied"
        db_records = get_interview_answers(document_id=doc_id, finding_id=finding_id)
        self.assertTrue(len(db_records) >= 1)
        self.assertEqual(db_records[-1]["origin"], "user_supplied")

    # ========================================================
    # PHASE 6: EVIDENCE FEEDBACK
    # ========================================================

    def test_evidence_feedback_api(self):
        """Test recording user evidence feedback (relevant/not_relevant/uncertain) without mutating statute data."""
        response = self.client.post("/api/feedback/evidence", json={
            "document_id": "doc_test_feedback",
            "provision_id": "IND_IDA_S25F",
            "rating": "relevant",
            "rationale": "Directly relates to termination clause in section 4."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["rating"], "relevant")

        # Query feedback back
        fb_records = get_evidence_feedback(document_id="doc_test_feedback", provision_id="IND_IDA_S25F")
        self.assertTrue(len(fb_records) >= 1)
        self.assertEqual(fb_records[0]["rating"], "relevant")

    def test_evidence_feedback_validation_rejects_invalid_rating(self):
        """Test that invalid rating strings are rejected with 400 error."""
        response = self.client.post("/api/feedback/evidence", json={
            "provision_id": "IND_IDA_S25F",
            "rating": "bogus_rating"
        })
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
