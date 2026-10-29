import os
import sys
import json
import datetime

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import text
from app.database.connection import engine, SessionLocal

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def export_database_snapshot() -> str:
    """
    Exports a structured JSON backup snapshot of all major entities
    (Careers, Roadmaps, Topics, Videos, Quizzes, Questions, Users, Progress).
    Returns the file path of the saved backup snapshot.
    """
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"skillpath_backup_{timestamp}.json")

    db = SessionLocal()
    try:
        tables = [
            "colleges", "departments", "academic_years", "semesters", "divisions",
            "users", "careers", "roadmaps", "topics", "videos", "quizzes",
            "questions", "coding_challenges", "student_progress", "certificates",
            "audit_logs", "roadmap_versions"
        ]

        data = {}
        for tbl in tables:
            try:
                rows = db.execute(text(f"SELECT * FROM `{tbl}`")).fetchall()
                # Convert list of Row objects to dictionaries
                if rows:
                    columns = list(rows[0]._fields) if hasattr(rows[0], "_fields") else []
                    data[tbl] = [dict(zip(columns, [str(val) if isinstance(val, (datetime.datetime, datetime.date)) else val for val in row])) for row in rows]
                else:
                    data[tbl] = []
            except Exception as ex:
                print(f"[BACKUP WARNING] Could not backup table {tbl}: {ex}")
                data[tbl] = []

        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"[BACKUP SUCCESS] Database snapshot exported to: {backup_file}")
        return backup_file
    finally:
        db.close()

if __name__ == "__main__":
    export_database_snapshot()
