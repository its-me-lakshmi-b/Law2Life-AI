from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.upload import router as upload_router
from backend.api.analysis import router as analysis_router
from backend.api.question_answer import router as question_router
from backend.api.interview import router as interview_router
from backend.database.connection import init_db
from backend.database.models import get_recent_analyses

# Initialize database schema on startup
try:
    init_db()
except Exception:
    pass

app = FastAPI(
    title="Law2Life AI",
    description="Context-Aware Legal Rights Advisor Using Hybrid NLP and Knowledge Graph Reasoning",
    version="1.2.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# API ROUTES
# --------------------------------------------------

app.include_router(
    upload_router,
    prefix="/api"
)
app.include_router(
    analysis_router,
    prefix="/api"
)
app.include_router(
    question_router,
    prefix="/api"
)
app.include_router(
    interview_router,
    prefix="/api"
)

# --------------------------------------------------
# STATIC FILES (FRONTEND UI)
# --------------------------------------------------

import os
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# --------------------------------------------------
# ROOT & HEALTH
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "application": "Law2Life AI",
        "status": "running",
        "message": "Context-Aware Legal Rights Advisor API",
        "version": "1.2.0"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "sqlite_connected",
        "dataset_version": "1.2.0",
        "capabilities": [
            "pdf_extraction",
            "docx_extraction",
            "ocr_fallback",
            "spacy_ner",
            "statutory_hybrid_retrieval",
            "knowledge_graph_reasoning",
            "conflict_detection",
            "risk_scoring",
            "action_recommender",
            "explainability_engine",
            "document_grounded_qa"
        ]
    }


@app.get("/api/history")
def history_endpoint(limit: int = 10):
    return {
        "status": "success",
        "recent_analyses": get_recent_analyses(limit=limit)
    }



@app.get("/test-ner")
def test_ner():

    from backend.nlp.ner import (
        extract_entities,
        extract_legal_facts
    )

    test_text = """
    Employee Ananya Rao
    Employer ABC Technologies Pvt. Ltd.
    Position Data Analyst
    Start Date 1 October 2026
    Monthly Salary I45,000
    Work Location Vellore, Tamil Nadu

    6. Notice and Termination
    Either party may terminate the employment by providing 30 days' written notice.

    4. Leave
    Leave requests should normally be submitted at least seven days before the intended leave date.
    """

    return {
        "entities": extract_entities(test_text),
        "legal_facts": extract_legal_facts(test_text)
    }