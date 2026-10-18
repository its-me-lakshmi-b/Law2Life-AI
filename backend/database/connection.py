"""
Law2Life AI - Database Connection & Initialization
Uses self-contained SQLite persistence to store document metadata,
analysis results, and question logs without requiring external database servers.
"""

import os
import sqlite3
from typing import Generator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "law2life.db")


def get_db_connection() -> sqlite3.Connection:
    """Create a new SQLite connection with row factory enabled."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize schema tables for document metadata, analysis runs, and Q&A history."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            stored_filepath TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size_bytes INTEGER DEFAULT 0,
            document_type TEXT DEFAULT 'unknown',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Analysis runs table (stores summary and assessment, not raw sensitive full text)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_records (
            id TEXT PRIMARY KEY,
            document_id TEXT,
            document_type TEXT,
            summary TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            conflicts_count INTEGER DEFAULT 0,
            clauses_count INTEGER DEFAULT 0,
            dataset_version TEXT DEFAULT '1.2.0',
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        );
    """)

    # Q&A history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            evidence TEXT,
            asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Adaptive interview user answers table (origin: user_supplied, never overwrites extracted facts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT,
            finding_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            fact_key TEXT NOT NULL,
            user_value TEXT NOT NULL,
            origin TEXT DEFAULT 'user_supplied',
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        );
    """)

    # Assessment versions table (tracks audit trail and diffs across interview answers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            version_number INTEGER NOT NULL,
            assessment_json TEXT NOT NULL,
            resolved_facts_json TEXT,
            findings_diff_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        );
    """)

    # Evidence feedback table (user ratings: relevant/not_relevant/uncertain; never alters statutory records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT,
            finding_id TEXT,
            provision_id TEXT NOT NULL,
            rating TEXT NOT NULL,
            rationale TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_FILE)
