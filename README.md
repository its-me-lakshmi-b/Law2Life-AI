# Law2Life AI

> **Context-Aware Legal Rights Advisor Using Hybrid NLP and Knowledge Graph Reasoning**

Law2Life AI is an end-to-end intelligent legal document advisor. It allows users to upload agreements (Employment Agreements, Rental / Lease Agreements, etc.) as PDF, DOCX, or scanned images, extract parties and terms, detect potential issues and statutory inconsistencies, compute an explainable document risk score, recommend prudent next actions, and query the document using grounded question answering backed by verified Indian statutes.

---

## 🏛️ Key Features

1. **Robust Multi-Format Document Processing**:
   - Native PDF extraction via PyMuPDF with page-by-page OCR fallback for scanned contracts.
   - DOCX extraction parsing both body paragraphs and embedded structured tables.
   - OCR fallback using Tesseract for PNG, JPG, and JPEG documents.

2. **Hybrid NLP & Legal Information Extraction**:
   - Named Entity Recognition (NER) powered by spaCy (`en_core_web_sm`).
   - Rule-assisted legal fact extraction (parties, salary, rent, security deposit, notice periods, dates, jurisdiction).
   - Clause segmentation across rights, obligations, deadlines, termination conditions, payment, leave, confidentiality, and dispute resolution.
   - High-confidence document classification with uncertainty flagging for ambiguous contracts.

3. **Verified Indian Statutory Dataset & Provenance**:
   - 10 verified statutory provisions from official India Code sources with complete provenance citations:
     - *Indian Contract Act, 1872* (Sections 27 & 74: Restraint of Trade, Liquidated Damages)
     - *Payment of Wages Act, 1936* (Sections 5 & 7: Time and Deductions from Wages)
     - *Industrial Disputes Act, 1947* (Section 25F: Conditions Precedent to Retrenchment and Notice)
     - *Maternity Benefit Act, 1961* (Section 5: Maternity Benefit and Leave)
     - *Transfer of Property Act, 1882* (Sections 106 & 108: Duration of Leases, Rights & Liabilities of Lessee)
     - *Factories Act, 1948* (Sections 51, 54, 55: Weekly Working Hours and Rest Intervals)
     - *Consumer Protection Act, 2019* (Section 2(46): Protection Against Unfair Contract Terms)
   - Zero synthetic, hallucinated, or unverified statutory claims.

4. **Internal Knowledge Graph Reasoning**:
   - In-memory directed graph of 42 typed statutory and contractual relationships (`REQUIRES`, `SUBJECT_TO`, `GOVERNS`, `PROHIBITS`).
   - Breadth-First Search (BFS) path-finding between document concepts and legal obligations.
   - *Note:* The Knowledge Graph operates exclusively as an internal reasoning engine; no raw graph visualizations are exposed to the user.

5. **Context-Aware Conflict & Risk Engine**:
   - Topic-scoped comparison avoiding false-positive timeline comparisons (e.g. separates leave notice from termination notice).
   - Direct conflict detection for restraint of trade under Section 27 of the Indian Contract Act.
   - Transparent risk assessment providing a 0–100 risk score and level badge (Low, Moderate, High) with explicit point attributions.

6. **10-Step Traceable Explainability Trail**:
   - Generates an auditable evidence chain covering file verification, OCR status, text normalization, fact extraction, classification, clause extraction, knowledge graph traversal, statutory retrieval, conflict detection, and risk scoring.

7. **Document-Grounded Question Answering**:
   - Answers questions strictly grounded in the extracted document context and retrieved statutory provisions.
   - Prompt injection defense detecting system-override attempts.
   - Fallback responses when requested information is absent or ambiguous, avoiding hallucination.

8. **Privacy-Preserving SQLite Persistence**:
   - Self-contained SQLite database at `data/law2life.db` recording document metadata, analysis summaries, and Q&A history without storing raw sensitive contract text.

---

## 🏗️ Architecture

```
User Document (PDF / DOCX / Image)
                 │
                 ▼
     [ Document Extractor ] ──(Scanned PDF / Image)──► [ Tesseract OCR ]
                 │
                 ▼
       [ Text Preprocessing ]
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
[ spaCy NER & Facts ]   [ Clause Extractor ]
    │                         │
    └────────────┬────────────┘
                 ▼
      [ Document Classifier ]
                 │
    ┌────────────┴──────────────────────┐
    ▼                                   ▼
[ Hybrid Retriever ]          [ Internal Knowledge Graph ]
(Keyword + TF-IDF Vector)      (BFS Relationship Traversal)
    │                                   │
    └────────────┬──────────────────────┘
                 ▼
       [ Conflict Detector ]
                 │
                 ▼
      [ Risk & Action Engine ]
                 │
                 ▼
    [ 10-Step Explainability ]
                 │
                 ▼
    [ FastAPI API & SQLite DB ] ◄──► [ Grounded Q&A Endpoint ]
                 │
                 ▼
    [ Existing Vanilla UI Dashboard ]
```

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Tesseract OCR (Optional for scanned images; Windows default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

### 1. Clone & Set Up Virtual Environment

```powershell
cd d:\LAW2LIFE_AI
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Initialize & Verify Dataset Ingestion

```powershell
python backend/retrieval/ingest_legal_data.py
```

### 4. Run Automated Test Suite

```powershell
python -m unittest discover tests -v
```

### 5. Launch the Application

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to:
- **Application UI**: [http://127.0.0.1:8000/frontend/index.html](http://127.0.0.1:8000/frontend/index.html)
- **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🐳 Docker Deployment

To build and run Law2Life AI via Docker:

```bash
# Build the container
docker build -t law2life-ai:latest .

# Run the container
docker run -d -p 8000:8000 --name law2life-ai law2life-ai:latest

# Verify health
curl http://localhost:8000/api/health
```

---

## 📡 API Reference

### 1. `POST /api/upload`
Uploads a document (PDF, DOCX, PNG, JPG, JPEG) up to 15 MB. Sanitizes filename, performs extraction and initial classification, and records metadata in SQLite.

**Response:**
```json
{
  "status": "success",
  "document_id": "c1f72740-4bd4-4497-a616-43b591b65ba1",
  "document_name": "Sample_Employment_Agreement.pdf",
  "file_type": ".pdf",
  "document_type": "employment_agreement",
  "extracted_text": "..."
}
```

### 2. `POST /api/analyze`
Executes comprehensive legal analysis over document text: NER, legal facts, clause extraction, hybrid retrieval against Indian statutes, internal knowledge graph reasoning, conflict detection, risk scoring, action recommendations, and explainability trail.

**Request:**
```json
{
  "text": "The Employee will receive a monthly salary of INR 45,000...",
  "document_id": "c1f72740-4bd4-4497-a616-43b591b65ba1"
}
```

**Response:**
```json
{
  "status": "success",
  "document_type": "employment_agreement",
  "summary": "...",
  "legal_facts": { "employee": "Ananya Rao", "salary": "INR 45,000", ... },
  "rights": [...],
  "obligations": [...],
  "deadlines": [...],
  "termination": [...],
  "conflicts": [...],
  "risk": { "risk_score": 15, "risk_level": "Low", "factors": [...] },
  "actions": [...],
  "explanation": { "steps": [...], "confidence_level": "High" }
}
```

### 3. `POST /api/question`
Answers questions grounded strictly in the analyzed document context and statutory evidence with prompt injection filtering.

**Request:**
```json
{
  "question": "What is my notice period for termination?",
  "document_context": { ... }
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "According to the document, the notice period is 30 days.",
  "evidence": "Either party may terminate the employment by providing 30 days' written notice.",
  "reason": "Direct factual extraction from document clauses and facts.",
  "confidence": 0.95
}
```

### 4. `GET /api/health`
Returns system status, OCR availability, database connectivity, and dataset verification status.

### 5. `GET /api/history`
Returns recent analysis execution logs from SQLite persistence.

---

## ⚖️ Legal Disclaimer

Law2Life AI provides automated document analysis and general legal informational references. It does not provide formal legal advice, representation, or guarantee legal outcomes. Consult a qualified advocate or attorney licensed in your jurisdiction for specific legal counsel.
