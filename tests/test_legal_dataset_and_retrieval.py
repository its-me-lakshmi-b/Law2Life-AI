"""
Unit & Integration Tests for Legal Dataset Provenance and Hybrid Retrieval
"""

import os
import json
import unittest
from backend.retrieval.legal_retriever import load_legal_provisions, retrieve_legal_provisions
from backend.retrieval.vector_store import LegalVectorStore


class TestLegalDatasetAndRetrieval(unittest.TestCase):

    def setUp(self):
        self.provisions = load_legal_provisions()

    def test_dataset_provenance_schema(self):
        """Verify that every legal provision adheres to the verified Indian statute schema."""
        self.assertGreaterEqual(len(self.provisions), 10)
        seen_ids = set()

        for prov in self.provisions:
            pid = prov.get("provision_id")
            self.assertIsNotNone(pid)
            self.assertNotIn(pid, seen_ids, f"Duplicate provision_id found: {pid}")
            seen_ids.add(pid)

            self.assertIn("title", prov)
            self.assertIn("topic", prov)
            self.assertIn("document_types", prov)
            self.assertIsInstance(prov["document_types"], list)
            self.assertIn("keywords", prov)
            self.assertIsInstance(prov["keywords"], list)
            self.assertTrue(len(prov["keywords"]) > 0)
            self.assertIn("description", prov)
            self.assertIn("conditions", prov)
            self.assertIn("exceptions", prov)

            # Source provenance
            source = prov.get("source", {})
            self.assertIn("name", source)
            self.assertEqual(source.get("jurisdiction"), "India")
            self.assertTrue(source.get("url", "").startswith("https://www.indiacode.nic.in/"))
            self.assertEqual(source.get("verification_status"), "verified_statute")

    def test_vector_store_tfidf(self):
        """Test that LegalVectorStore builds indices and calculates non-zero cosine similarities."""
        vstore = LegalVectorStore(self.provisions)
        self.assertTrue(len(vstore.doc_vectors) > 0)

        # Query relevant to wages
        results = vstore.query("monthly salary payable on or before seventh day")
        self.assertTrue(len(results) > 0)
        top_doc, sim = results[0]
        self.assertIn("Payment", top_doc.get("title", "") + top_doc.get("description", ""))
        self.assertGreater(sim, 0.1)

    def test_hybrid_retrieval_termination(self):
        """Test hybrid retrieval matches termination notice against Industrial Disputes Act Section 25F."""
        clause = "Either party may terminate the employment by providing 30 days' written notice."
        results = retrieve_legal_provisions(clause, document_type="employment_agreement", top_k=2)
        self.assertTrue(len(results) >= 1)
        top = results[0]
        self.assertEqual(top["provision_id"], "IND_IDA_S25F")
        self.assertEqual(top["verification_status"], "verified_statute")
        self.assertIn("Section 25F", top["citation"])
        self.assertIn("Industrial Disputes Act", top["act"])
        self.assertIn("relevance_reason", top)

    def test_hybrid_retrieval_restraint_of_trade(self):
        """Test hybrid retrieval matches non-compete restraint against Section 27 Indian Contract Act."""
        clause = "The employee shall not work for any competitor anywhere in India for 2 years post-employment."
        results = retrieve_legal_provisions(clause, document_type="employment_agreement", top_k=2)
        self.assertTrue(len(results) >= 1)
        top = results[0]
        self.assertEqual(top["provision_id"], "IND_CONT_S27")
        self.assertIn("Section 27", top["section"])
        self.assertIn("Restraint of Trade", top["title"])

    def test_hybrid_retrieval_irrelevant_clause(self):
        """Test that completely unrelated non-legal text yields no false statutory match."""
        clause = "We like making chocolate chip cookies on sunny Sunday mornings in the garden."
        results = retrieve_legal_provisions(clause, document_type="employment_agreement", top_k=3)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
