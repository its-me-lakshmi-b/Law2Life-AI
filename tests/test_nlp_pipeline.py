"""
Unit & Integration Tests for NLP Pipeline
"""

import unittest
from backend.nlp.preprocessing import preprocess_legal_text
from backend.nlp.ner import extract_entities, extract_legal_facts
from backend.nlp.clause_extractor import extract_clauses
from backend.nlp.legal_classifier import classify_document


class TestNLPPipeline(unittest.TestCase):

    def test_preprocessing_line_joins_and_headings(self):
        """Test normalization and preservation of legal headings."""
        raw_text = (
            "1. Employment The Employee will work as a Data Analyst.\n"
            "2. Salary The Employee will receive a salary of\n"
            "INR 45,000 payable monthly.\n"
        )
        cleaned = preprocess_legal_text(raw_text)
        self.assertIn("1. Employment", cleaned)
        self.assertIn("2. Salary", cleaned)
        self.assertIn("payable monthly", cleaned)

    def test_ner_general_entities(self):
        """Test that spaCy extracts basic entities without error."""
        text = "Ananya Rao joined ABC Technologies Pvt. Ltd. on 1 October 2026 in Bengaluru."
        ents = extract_entities(text)
        self.assertIsInstance(ents, list)
        self.assertTrue(len(ents) > 0)
        labels = [e["label"] for e in ents]
        self.assertTrue(any(l in ["PERSON", "ORG", "DATE", "GPE"] for l in labels))

    def test_legal_facts_employment(self):
        """Test fact extraction for employment agreement format."""
        text = """
        Employee Ananya Rao
        Employer ABC Technologies Pvt. Ltd.
        Position Data Analyst
        Start Date 1 October 2026
        Monthly Salary INR 45,000
        Work Location Vellore, Tamil Nadu
        Either party may terminate the employment by providing 30 days' written notice.
        Leave requests should normally be submitted at least seven days before the intended leave date.
        """
        facts = extract_legal_facts(text)
        self.assertEqual(facts["employee"], "Ananya Rao")
        self.assertEqual(facts["employer"], "ABC Technologies Pvt. Ltd.")
        self.assertEqual(facts["position"], "Data Analyst")
        self.assertEqual(facts["start_date"], "1 October 2026")
        self.assertEqual(facts["salary"], "INR 45,000")
        self.assertEqual(facts["notice_period"], "30 days")
        self.assertEqual(facts["leave_notice"], "seven days")

    def test_legal_facts_rental(self):
        """Test fact extraction for rental agreement format."""
        text = """
        Landlord Rajesh Sharma
        Tenant Priya Patel
        The monthly rent of INR 25,000 shall be paid on or before the 5th day of each calendar month.
        The Tenant has paid a security deposit of INR 100,000.
        Either party may terminate this lease by giving 30 days notice.
        """
        facts = extract_legal_facts(text)
        self.assertIn("Rajesh Sharma", facts["landlord"])
        self.assertIn("Priya Patel", facts["tenant"])
        self.assertIn("25,000", facts["rent"])
        self.assertIn("100,000", facts["security_deposit"])
        self.assertEqual(facts["notice_period"], "30 days")

    def test_legal_facts_missing_data(self):
        """Test that missing facts remain None and are not fabricated."""
        text = "This is a generic document without any named parties or salary terms."
        facts = extract_legal_facts(text)
        self.assertIsNone(facts["employee"])
        self.assertIsNone(facts["employer"])
        self.assertIsNone(facts["salary"])
        self.assertIsNone(facts["notice_period"])

    def test_clause_extraction_numbered_sections(self):
        """Test clause extraction from standard numbered headings."""
        text = """
        1. Employment The Employee will perform duties diligently.
        2. Working Hours Normal schedule is Monday to Friday, 9:00 AM to 6:00 PM.
        3. Salary The monthly salary of INR 50,000 is payable on or before the 7th.
        4. Leave The Employee may request paid leave under company policy.
        5. Confidentiality The Employee must keep confidential all trade secrets.
        6. Notice and Termination Either party may terminate by providing 30 days notice.
        8. Dispute Resolution All disputes shall be resolved through arbitration in Bengaluru.
        """
        clauses = extract_clauses(text)
        self.assertTrue(len(clauses["obligations"]) >= 2)
        self.assertTrue(len(clauses["payment"]) >= 1)
        self.assertTrue(len(clauses["rights"]) >= 1)
        self.assertTrue(len(clauses["leave"]) >= 1)
        self.assertTrue(len(clauses["confidentiality"]) >= 1)
        self.assertTrue(len(clauses["termination"]) >= 1)
        self.assertTrue(len(clauses["deadlines"]) >= 1)
        self.assertTrue(len(clauses["dispute_resolution"]) >= 1)

    def test_clause_extraction_sentence_fallback(self):
        """Test clause extraction on unnumbered contracts via semantic modal classifier."""
        text = """
        The contractor shall deliver all software artifacts by the due date.
        The client is entitled to terminate this agreement upon 15 days' notice.
        The service provider agrees to maintain non-disclosure of proprietary information.
        A monthly fee of USD 3,000 is payable on or before the first of each month.
        Any dispute shall be referred to arbitration in New Delhi.
        """
        clauses = extract_clauses(text)
        self.assertTrue(len(clauses["obligations"]) >= 1)
        self.assertTrue(len(clauses["rights"]) >= 1)
        self.assertTrue(len(clauses["termination"]) >= 1)
        self.assertTrue(len(clauses["payment"]) >= 1)
        self.assertTrue(len(clauses["dispute_resolution"]) >= 1)

    def test_document_classification_high_confidence(self):
        """Test classification of distinct employment agreement."""
        text = "EMPLOYMENT AGREEMENT. This employment agreement is entered between employer and employee with monthly salary, leave, and notice period."
        res = classify_document(text)
        self.assertEqual(res["document_type"], "employment_agreement")
        self.assertGreaterEqual(res["confidence"], 0.5)
        self.assertFalse(res.get("is_uncertain", False))

    def test_document_classification_uncertain_threshold(self):
        """Test classification handles ambiguous or generic text responsibly without false positive."""
        text = "Please note that you should take notice of this general announcement."
        res = classify_document(text)
        # Even though 'notice' appeared once, it should not trigger high confidence legal notice
        self.assertTrue(res["document_type"] == "unknown" or res.get("is_uncertain", False))


if __name__ == "__main__":
    unittest.main()
