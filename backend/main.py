from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.upload import router as upload_router
from backend.api.analysis import router as analysis_router

app = FastAPI(
    title="Law2Life AI",
    description="Context-Aware Legal Rights Advisor",
    version="1.0.0"
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

# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "application": "Law2Life AI",
        "status": "running",
        "message": "Context-Aware Legal Rights Advisor API"
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