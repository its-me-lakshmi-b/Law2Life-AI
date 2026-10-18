"""
Unit & Integration Tests for Knowledge Graph Modules
"""

import unittest
from backend.knowledge_graph.graph_builder import build_knowledge_graph
from backend.knowledge_graph.graph_queries import get_related_nodes, find_path
from backend.knowledge_graph.graph_reasoning import (
    identify_concepts,
    reason_about_clause,
    reason_about_document
)


class TestKnowledgeGraph(unittest.TestCase):

    def setUp(self):
        self.graph = build_knowledge_graph()

    def test_graph_structure(self):
        """Test graph contains nodes and typed relationships."""
        self.assertIn("nodes", self.graph)
        self.assertIn("relationships", self.graph)
        self.assertGreaterEqual(len(self.graph["nodes"]), 15)
        self.assertGreaterEqual(len(self.graph["relationships"]), 30)

        for rel in self.graph["relationships"]:
            self.assertIn("source", rel)
            self.assertIn("relation", rel)
            self.assertIn("target", rel)

    def test_related_nodes_lookup(self):
        """Test getting incoming and outgoing relationships for a node."""
        related = get_related_nodes("Termination")
        self.assertTrue(len(related) > 0)
        nodes = [r["node"] for r in related]
        self.assertTrue(any("Notice" in n or "Law" in n for n in nodes))

    def test_bfs_path_finding(self):
        """Test BFS path traversal between connected legal concepts."""
        path = find_path("Employment Agreement", "Applicable Law")
        self.assertTrue(len(path) >= 2)
        self.assertEqual(path[0], "Employment Agreement")
        self.assertEqual(path[-1], "Applicable Law")

    def test_path_finding_missing_node(self):
        """Test path finding handles disconnected or non-existent nodes gracefully."""
        path = find_path("NonExistentConceptA", "NonExistentConceptB")
        self.assertEqual(path, [])

    def test_clause_reasoning(self):
        """Test concept identification and reasoning on document clause."""
        clause = "Either party may terminate the employment by providing 30 days' written notice."
        concepts = identify_concepts(clause)
        self.assertIn("termination", concepts)

        reasoning_res = reason_about_clause(clause)
        self.assertIn("clause", reasoning_res)
        self.assertIn("results", reasoning_res)
        self.assertTrue(len(reasoning_res["results"]) > 0)


if __name__ == "__main__":
    unittest.main()
