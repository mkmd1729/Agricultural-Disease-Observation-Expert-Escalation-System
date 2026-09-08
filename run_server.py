"""
Application Launcher for Agricultural Disease Observation & Expert Escalation System.
Usage:
    python run_server.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from backend.app.database import init_db

if __name__ == "__main__":
    print("======================================================================")
    print("  AGRICULTURAL DISEASE OBSERVATION & EXPERT ESCALATION APP (MVP)")
    print("======================================================================")
    print("  Initializing local database...")
    init_db()
    print("  Database ready.")
    print("  Starting web application on http://127.0.0.1:8000")
    print("  Press CTRL+C to stop.")
    print("======================================================================")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
