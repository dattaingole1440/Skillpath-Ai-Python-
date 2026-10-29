from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import (
    User, Assignment, AssignmentSubmission, AttendanceRecord, ActivityTrack,
    PlacementRecord, TeacherNotification, Project, UserProjectSubmission
)
from app.utils.auth import get_current_user
from app.ai.service import generate_placement_readiness_ai

router = APIRouter(prefix="/student", tags=["Student Module"])
templates = Jinja2Templates(directory="app/templates")

@router.post("/activity/log")
def log_learning_activity(
    activity_type: str = Form(...), # video_watch, pdf_read, quiz, coding, assignment, ai_chat, mock_interview
    duration_minutes: float = Form(...),
    details: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logs student learning activity and automatically updates/generates daily attendance:
    - Study > 30 minutes = Present
    - Study 10-30 minutes = Partial
    - Study < 10 minutes = Absent
    """
    track = ActivityTrack(
        student_id=current_user.id,
        activity_type=activity_type,
        duration_minutes=duration_minutes,
        details=details
    )
    db.add(track)

    # Accumulate student learning hours
    current_user.learning_hours += (duration_minutes / 60.0)

    # Fetch today's total study duration
    today = date.today()
    today_tracks = db.query(ActivityTrack).filter(
        ActivityTrack.student_id == current_user.id,
        ActivityTrack.timestamp >= datetime.combine(today, datetime.min.time())
    ).all()
    
    total_today_minutes = sum(t.duration_minutes for t in today_tracks) + duration_minutes

    # Determine attendance status
    if total_today_minutes >= 30.0:
        att_status = "Present"
    elif total_today_minutes >= 10.0:
        att_status = "Partial"
    else:
        att_status = "Absent"

    # Upsert Attendance Record for today
    att_rec = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == current_user.id,
        AttendanceRecord.date == today
    ).first()

    if att_rec:
        if not att_rec.is_manual_override:
            att_rec.status = att_status
            att_rec.study_minutes = int(total_today_minutes)
    else:
        att_rec = AttendanceRecord(
            student_id=current_user.id,
            date=today,
            status=att_status,
            study_minutes=int(total_today_minutes)
        )
        db.add(att_rec)

    db.commit()
    return {"status": "success", "total_today_minutes": total_today_minutes, "attendance_status": att_status}


@router.get("/assignments", response_class=HTMLResponse)
def view_student_assignments(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignments = db.query(Assignment).order_by(Assignment.created_at.desc()).all()
    submissions = {s.assignment_id: s for s in db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == current_user.id).all()}
    
    return templates.TemplateResponse("student/assignments.html", {
        "request": request,
        "user": current_user,
        "assignments": assignments,
        "submissions": submissions
    })


@router.post("/assignments/submit")
def submit_assignment(
    assignment_id: int = Form(...),
    submission_text: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    file_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()

    if existing:
        existing.submission_text = submission_text
        existing.code = code
        existing.file_url = file_url
        existing.submitted_at = datetime.utcnow()
    else:
        sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            submission_text=submission_text,
            code=code,
            file_url=file_url
        )
        db.add(sub)

    # Award XP for submitting assignment
    current_user.xp += 40
    db.commit()

    return RedirectResponse(url="/student/assignments", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/placement", response_class=HTMLResponse)
def view_placement_readiness(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Computes placement score and displays AI advice."""
    attendance_records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == current_user.id).all()
    present_cnt = sum(1 for a in attendance_records if a.status == "Present")
    att_score = (present_cnt / len(attendance_records) * 100.0) if attendance_records else 85.0

    scores = {
        "coding_score": current_user.coding_avg,
        "quiz_score": current_user.quiz_avg,
        "projects_score": 80.0,
        "attendance_score": att_score,
        "resume_score": 82.0,
        "interview_score": 78.0,
        "roadmap_completion_score": 75.0
    }

    placement_eval = generate_placement_readiness_ai(scores)

    placement_rec = db.query(PlacementRecord).filter(PlacementRecord.student_id == current_user.id).first()
    if not placement_rec:
        placement_rec = PlacementRecord(
            student_id=current_user.id,
            placement_score=placement_eval["overall_placement_score"],
            coding_score=scores["coding_score"],
            quiz_score=scores["quiz_score"],
            projects_score=scores["projects_score"],
            attendance_score=scores["attendance_score"],
            resume_score=scores["resume_score"],
            interview_score=scores["interview_score"],
            roadmap_completion_score=scores["roadmap_completion_score"],
            ai_recommendations="\n".join(placement_eval["ai_recommendations"])
        )
        db.add(placement_rec)
        db.commit()

    return templates.TemplateResponse("student/placement.html", {
        "request": request,
        "user": current_user,
        "placement_eval": placement_eval,
        "scores": scores
    })


@router.get("/notifications", response_class=HTMLResponse)
def view_notifications(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifications = db.query(TeacherNotification).filter(
        (TeacherNotification.recipient_student_id == current_user.id) |
        (TeacherNotification.recipient_student_id == None)
    ).order_by(TeacherNotification.sent_at.desc()).all()

    return templates.TemplateResponse("student/notifications.html", {
        "request": request,
        "user": current_user,
        "notifications": notifications
    })


@router.get("/practicals", response_class=HTMLResponse)
def view_student_practicals(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.models import CodingChallenge, Project
    challenges = db.query(CodingChallenge).filter(CodingChallenge.is_deleted == False).limit(30).all()
    projects = db.query(Project).all()
    return templates.TemplateResponse("student/practicals.html", {
        "request": request,
        "user": current_user,
        "challenges": challenges,
        "projects": projects
    })


@router.get("/resources", response_class=HTMLResponse)
def view_student_resources(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.models import Resource, Video, Topic, KnowledgeVideo
    resources = db.query(Resource).all()
    knowledge_videos = db.query(KnowledgeVideo).order_by(KnowledgeVideo.is_hod_recommended.desc(), KnowledgeVideo.created_at.desc()).all()
    videos = db.query(Video).filter(Video.is_deleted == False).all()
    if not videos or len(videos) == 0:
        videos = [
            Video(id=101, title="Python Programming Masterclass", youtube_url="https://www.youtube.com/watch?v=_uQrJ0TkZlc"),
            Video(id=102, title="Full Stack Web Development", youtube_url="https://www.youtube.com/watch?v=UB1O30fR-EE"),
            Video(id=103, title="SQL & Database Management", youtube_url="https://www.youtube.com/watch?v=HXV3zeQKqGY"),
            Video(id=104, title="FastAPI & REST APIs Architecture", youtube_url="https://www.youtube.com/watch?v=7t2alSnE2-I"),
            Video(id=105, title="React JS Complete Course", youtube_url="https://www.youtube.com/watch?v=w7ejDZ8SWv8"),
            Video(id=106, title="Data Structures & Algorithms", youtube_url="https://www.youtube.com/watch?v=zOjov-2OZ0E")
        ]
    topics_with_media = db.query(Topic).filter(Topic.is_deleted == False).limit(20).all()
    return templates.TemplateResponse("student/resources.html", {
        "request": request,
        "user": current_user,
        "resources": resources,
        "knowledge_videos": knowledge_videos,
        "videos": videos,
        "topics": topics_with_media
    })


