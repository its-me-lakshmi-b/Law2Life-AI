"""
Unit & Integration Tests for Conflict Detection, Risk Engine, Action Recommender, and Explainability
"""

import unittest
from backend.reasoning.conflict_detector import (
    analyze_clause_against_provision,
    detect_conflicts
)
from backend.reasoning.risk_engine import calculate_risk
from backend.reasoning.action_recommender import recommend_actions
from backend.explainability.explanation_engine import generate_explanation


class TestReasoningAndRisk(unittest.TestCase):

    def test_direct_numeric_conflict(self):
        """Test detection of genuine timeline mismatch on same topic."""
        clause = "The employee may terminate with 15 days notice."
        provision = "Section 25F requires 30 days written notice for retrenchment."
        finding = analyze_clause_against_provision(clause, provision, clause_category="termination")
        self.assertIsNotNone(finding)
        self.assertEqual(finding["conflict_type"], "direct_numeric_conflict")
        self.assertIn("15 days", finding["reason"])
        self.assertIn("30 days", finding["reason"])

    def test_avoid_false_numeric_conflict_on_different_topics(self):
        """Test system does NOT falsely compare leave days with termination notice days."""
        leave_clause = "Leave requests must be submitted at least 7 days before intended leave."
        term_provision = "Section 25F requires 30 days written notice for retrenchment."
        finding = analyze_clause_against_provision(leave_clause, term_provision, clause_category="leave")
        self.assertIsNone(finding, "Unrelated leave notice should not be compared against retrenchment notice.")

    def test_restraint_of_trade_detection(self):
        """Test detection of post-employment non-compete under Section 27 Indian Contract Act."""
        clause = "The Employee covenants not to work for any competitor for 1 year following termination."
        provision = "Section 27 of the Indian Contract Act: agreement in restraint of trade is void."
        finding = analyze_clause_against_provision(clause, provision, clause_category="confidentiality")
        self.assertIsNotNone(finding)
        self.assertEqual(finding["conflict_type"], "statutory_restriction_review")
        self.assertIn("Section 27", finding["reason"])

    def test_risk_engine_dict_and_list_compatibility(self):
        """Test risk engine handles both dictionary clauses and list clauses without AttributeError."""
        dict_clauses = {
            "deadlines": ["Payable by 7th day."],
            "termination": ["30 days notice required."],
            "confidentiality": ["Must keep secrets."]
        }
        res_dict = calculate_risk(conflicts=[], clauses=dict_clauses, legal_evidence=[{"clause": "test"}])
        self.assertIn("risk_score", res_dict)
        self.assertIn("score", res_dict)
        self.assertIn("risk_level", res_dict)
        self.assertIn("factors", res_dict)
        self.assertTrue(len(res_dict["factors"]) > 0)
        self.assertIn("points", res_dict["factors"][0])

        list_clauses = [
            {"category": "deadlines", "text": "Payable by 7th day."},
            {"category": "termination", "text": "30 days notice."}
        ]
        res_list = calculate_risk(conflicts=[], clauses=list_clauses, legal_evidence=[])
        self.assertIsInstance(res_list["risk_score"], int)

    def test_risk_engine_high_risk_scoring(self):
        """Test high confidence conflicts correctly elevate the risk score and level."""
        conflicts = [
            {"confidence": 0.90, "conflict_type": "direct_numeric_conflict"},
            {"confidence": 0.88, "conflict_type": "statutory_restriction_review"}
        ]
        res = calculate_risk(conflicts=conflicts, clauses={}, legal_evidence=[])
        self.assertGreaterEqual(res["risk_score"], 50)
        self.assertIn(res["risk_level"], ["Moderate", "High"])

    def test_action_recommender(self):
        """Test generating prudent, grounded recommendations."""
        conflicts = [{
            "conflict_type": "direct_numeric_conflict",
            "document_clause": "15 days notice",
            "citation": "Section 25F, Industrial Disputes Act, 1947",
            "reason": "15 days vs 30 days"
        }]
        clauses = {"deadlines": ["Payment by 5th."]}
        actions = recommend_actions(conflicts=conflicts, clauses=clauses, document_type="employment_agreement")
        self.assertTrue(len(actions) >= 2)
        action_texts = [a["action"] for a in actions]
        self.assertTrue(any("clarification" in a.lower() for a in action_texts))
        self.assertTrue(any("calendar" in a.lower() for a in action_texts))
        self.assertTrue(any("consult" in a.lower() for a in action_texts))

    def test_explainability_engine_10_steps(self):
        """Test 10-step traceable evidence trail generation."""
        expl = generate_explanation(
            document_type="employment_agreement",
            legal_facts={"employee": "Ananya Rao", "salary": "INR 45,000"},
            clauses={"deadlines": ["30 days"]},
            conflicts=[],
            risk_assessment={"risk_score": 25, "risk_level": "Low"}
        )
        self.assertIn("steps", expl)
        self.assertEqual(len(expl["steps"]), 10)
        for s in expl["steps"]:
            self.assertIn("title", s)
            self.assertIn("description", s)
            self.assertTrue(len(s["description"]) > 10)


if __name__ == "__main__":
    unittest.main()
