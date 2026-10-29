from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Topic, Project, Resource, Quiz, CodingChallenge, Certificate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/search", tags=["Smart Search"])

@router.get("")
def global_search(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not q or len(q.strip()) < 2:
        return JSONResponse({"results": []})

    term = q.strip()
    results = []

    # Search Topics
    topics = db.query(Topic).filter(Topic.title.contains(term)).limit(5).all()
    for t in topics:
        results.append({
            "category": "Topic",
            "title": t.title,
            "description": t.description[:100] if t.description else "",
            "link": f"/roadmap/topic/{t.id}"
        })

    # Search Projects
    projects = db.query(Project).filter(Project.title.contains(term) | Project.tech_stack.contains(term)).limit(5).all()
    for p in projects:
        results.append({
            "category": "Project",
            "title": p.title,
            "description": f"{p.level} • {p.tech_stack}",
            "link": "/projects"
        })

    # Search Coding Challenges
    challenges = db.query(CodingChallenge).filter(CodingChallenge.title.contains(term)).limit(5).all()
    for c in challenges:
        results.append({
            "category": "Coding Challenge",
            "title": c.title,
            "description": f"Difficulty: {c.difficulty}",
            "link": f"/coding/challenge/{c.id}"
        })

    # Search Resources
    resources = db.query(Resource).filter(Resource.title.contains(term)).limit(5).all()
    for r in resources:
        results.append({
            "category": "Resource",
            "title": r.title,
            "description": f"Type: {r.type}",
            "link": r.url or "/resources"
        })

    # Search Certificates
    certificates = db.query(Certificate).filter(Certificate.certificate_number.contains(term)).limit(5).all()
    for cert in certificates:
        results.append({
            "category": "Certificate",
            "title": f"Certificate #{cert.certificate_number}",
            "description": f"Issued: {cert.issue_date}",
            "link": f"/certificates/verify/{cert.certificate_number}"
        })

    return JSONResponse({"results": results})
