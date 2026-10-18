"""
Law2Life AI - Lightweight In-Memory Vector & Lexical Store
Provides deterministic TF-IDF vectorization and cosine similarity
matching for statutory legal retrieval without requiring external dependencies.
"""

import math
import re
from typing import List, Dict, Any, Tuple


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with", "would",
    "you", "your", "yours", "will", "shall"
}


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into alphanumeric words, filtering stopwords."""
    if not text:
        return []
    words = re.findall(r"\b[a-z0-9_]{2,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]


class LegalVectorStore:
    """
    In-memory vector store that computes TF-IDF representations
    for legal provisions and enables hybrid similarity retrieval.
    """

    def __init__(self, documents: List[Dict[str, Any]] = None):
        self.documents: List[Dict[str, Any]] = []
        self.doc_vectors: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self.vocab: set = set()
        if documents:
            self.index_documents(documents)

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index a collection of legal provisions."""
        self.documents = documents
        total_docs = len(documents)
        if total_docs == 0:
            return

        doc_tokens_list = []
        doc_freq: Dict[str, int] = {}

        for doc in documents:
            # Build search content from title, description, keywords, and conditions
            content = " ".join([
                doc.get("title", ""),
                doc.get("description", ""),
                " ".join(doc.get("keywords", [])),
                " ".join(doc.get("conditions", []))
            ])
            tokens = tokenize(content)
            doc_tokens_list.append(tokens)
            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_freq[t] = doc_freq.get(t, 0) + 1
                self.vocab.add(t)

        # Compute smoothed IDF: log((N + 1) / (df + 1)) + 1
        self.idf = {
            t: math.log((total_docs + 1) / (freq + 1)) + 1.0
            for t, freq in doc_freq.items()
        }

        # Build normalized TF-IDF vector for each document
        self.doc_vectors = []
        for tokens in doc_tokens_list:
            tf: Dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            length = len(tokens) or 1
            vector: Dict[str, float] = {}
            norm_sq = 0.0
            for t, count in tf.items():
                w = (count / length) * self.idf.get(t, 1.0)
                vector[t] = w
                norm_sq += w * w
            norm = math.sqrt(norm_sq) or 1.0
            for t in vector:
                vector[t] /= norm
            self.doc_vectors.append(vector)

    def query(
        self,
        query_text: str,
        document_type: str = None,
        top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Query vector store using cosine similarity with optional metadata filtering.
        """
        query_tokens = tokenize(query_text)
        if not query_tokens or not self.doc_vectors:
            return []

        # Build query vector
        q_tf: Dict[str, float] = {}
        for t in query_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1
        q_len = len(query_tokens) or 1
        q_vec: Dict[str, float] = {}
        norm_sq = 0.0
        for t, count in q_tf.items():
            if t in self.idf:
                w = (count / q_len) * self.idf[t]
                q_vec[t] = w
                norm_sq += w * w
        q_norm = math.sqrt(norm_sq) or 1.0
        for t in q_vec:
            q_vec[t] /= q_norm

        scored_results = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            doc = self.documents[idx]

            # Filter by document_type if specified and supported
            if document_type:
                supported_types = doc.get("document_types", [])
                if supported_types and document_type not in supported_types:
                    continue

            # Dot product for cosine similarity
            sim = 0.0
            for t, weight in q_vec.items():
                if t in doc_vec:
                    sim += weight * doc_vec[t]

            if sim > 0.05:
                scored_results.append((doc, round(sim, 4)))

        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]
