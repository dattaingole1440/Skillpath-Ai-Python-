from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Certificate, StudentProgress, Topic, UserProjectSubmission, Project
from app.utils.auth import get_current_user_optional

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/{student_id}", response_class=HTMLResponse)
def get_student_portfolio(
    request: Request,
    student_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    target_id = student_id if student_id else (current_user.id if current_user else 2)
    student = db.query(User).filter(User.id == target_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    certificates = db.query(Certificate).filter(Certificate.student_id == student.id).all()
    completed_progress = db.query(StudentProgress).filter(StudentProgress.student_id == student.id, StudentProgress.status == "Completed").all()
    submissions = db.query(UserProjectSubmission).filter(UserProjectSubmission.student_id == student.id).all()

    return templates.TemplateResponse(
        "portfolio/view.html",
        {
            "request": request,
            "user": current_user,
            "student": student,
            "certificates": certificates,
            "completed_count": len(completed_progress),
            "submissions": submissions
        }
    )
