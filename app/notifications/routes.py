from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, SystemNotification, TeacherNotification
from app.utils.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_notifications_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch system notifications
    notifications = db.query(SystemNotification).filter(
        SystemNotification.student_id == current_user.id
    ).order_by(SystemNotification.created_at.desc()).all()
    
    # Fetch teacher notifications if student
    teacher_notifs = []
    if current_user.role == "student":
        teacher_notifs = db.query(TeacherNotification).filter(
            (TeacherNotification.recipient_student_id == current_user.id) |
            (TeacherNotification.recipient_student_id == None)
        ).order_by(TeacherNotification.sent_at.desc()).all()
    
    # Mark system notifications as read
    db.query(SystemNotification).filter(
        SystemNotification.student_id == current_user.id,
        SystemNotification.is_read == False
    ).update({"is_read": True})
    db.commit()

    return templates.TemplateResponse(
        "notifications/index.html",
        {
            "request": request,
            "user": current_user,
            "notifications": notifications,
            "teacher_notifications": teacher_notifs
        }
    )

@router.get("/api/unread")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = db.query(SystemNotification).filter(
        SystemNotification.student_id == current_user.id,
        SystemNotification.is_read == False
    ).count()
    return JSONResponse({"unread_count": count})

