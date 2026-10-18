import json
import os
import re
from typing import Dict, List, Any, Optional


# ------------------------------------------------------------
# LOAD LEGAL PROVISIONS
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

PROVISIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "legal_provisions.json"
)


def load_legal_provisions():

    try:

        with open(
            PROVISIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        raise Exception(
            f"Unable to load legal provisions: {str(e)}"
        )


# ------------------------------------------------------------
# TEXT NORMALIZATION
# ------------------------------------------------------------

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ------------------------------------------------------------
# KEYWORD MATCHING
# ------------------------------------------------------------

try:
    from backend.retrieval.vector_store import LegalVectorStore
except ImportError:
    LegalVectorStore = None

_CACHED_VECTOR_STORE = None


def get_vector_store():
    """Lazily initialize in-memory vector store singleton."""
    global _CACHED_VECTOR_STORE
    if _CACHED_VECTOR_STORE is None and LegalVectorStore is not None:
        provisions = load_legal_provisions()
        _CACHED_VECTOR_STORE = LegalVectorStore(provisions)
    return _CACHED_VECTOR_STORE


def calculate_keyword_match(
    clause_text,
    provision
):
    clause_text = normalize_text(clause_text)
    keywords = provision.get("keywords", [])
    matched_keywords = []

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword in clause_text:
            matched_keywords.append(keyword)

    return matched_keywords


# ------------------------------------------------------------
# RETRIEVE RELEVANT PROVISIONS (HYBRID RETRIEVAL)
# ------------------------------------------------------------

def retrieve_legal_provisions(
    clause_text: str,
    document_type: str = None,
    top_k: int = 3
):
    """
    Hybrid legal retrieval combining lexical keyword matching and
    TF-IDF semantic similarity with document-type filtering and provenance.
    """
    if not clause_text or not clause_text.strip():
        return []

    provisions = load_legal_provisions()
    if not provisions:
        return []

    vstore = get_vector_store()
    vector_scores: Dict[str, float] = {}
    if vstore:
        v_results = vstore.query(clause_text, document_type=document_type, top_k=top_k * 2)
        for doc, sim in v_results:
            pid = doc.get("provision_id")
            if pid:
                vector_scores[pid] = sim

    results = []
    normalized_clause = normalize_text(clause_text)

    for provision in provisions:
        pid = provision.get("provision_id")
        supported_types = provision.get("document_types", [])

        # Document type compatibility check
        document_match = (
            not document_type
            or document_type in supported_types
        )

        matched_keywords = calculate_keyword_match(normalized_clause, provision)
        keyword_count = len(matched_keywords)
        semantic_sim = vector_scores.get(pid, 0.0)

        # Skip provisions with neither keyword nor semantic match
        if keyword_count == 0 and semantic_sim < 0.10:
            continue

        # Hybrid scoring formulation:
        # Lexical signal + Semantic cosine similarity + Document type match bonus
        lexical_norm = min(keyword_count / max(len(provision.get("keywords", [1])), 1), 1.0)
        hybrid_score = round(
            (0.55 * lexical_norm) + (0.35 * semantic_sim) + (0.10 if document_match else 0.0),
            3
        )

        # Relevance reason for explainability
        reasons = []
        if matched_keywords:
            reasons.append(f"Matched legal keywords: {', '.join(matched_keywords[:4])}")
        if semantic_sim > 0.15:
            reasons.append(f"Contextual similarity score: {semantic_sim:.2f}")
        if document_match and document_type:
            reasons.append(f"Statutory scope covers {document_type.replace('_', ' ')}")
        relevance_reason = "; ".join(reasons) if reasons else "Relevant legal subject matter."

        src = provision.get("source", {})
        results.append({
            "provision_id": pid,
            "title": provision.get("title", "Legal Provision"),
            "topic": provision.get("topic", "general"),
            "act": src.get("act", src.get("name", "Indian Statute")),
            "section": src.get("section", ""),
            "citation": src.get("citation", ""),
            "description": provision.get("description", ""),
            "conditions": provision.get("conditions", []),
            "exceptions": provision.get("exceptions", []),
            "source": src,
            "verification_status": src.get("verification_status", "verified_statute"),
            "matched_keywords": matched_keywords,
            "semantic_score": semantic_sim,
            "score": hybrid_score,
            "relevance_reason": relevance_reason
        })

    # Sort by hybrid score descending
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]