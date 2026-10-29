import os
import shutil
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import (
    User, Subject, Assignment, AssignmentSubmission, AttendanceRecord,
    EarlyWarningAlert, TeacherNotification, SystemNotification, Quiz, Question, CodingChallenge, Project,
    Resource, ActivityTrack, StudentProgress, QuizAttempt, CodingSubmission, Topic, Video, Career, Roadmap, KnowledgeVideo
)
from app.utils.auth import get_current_user
from app.utils.permissions import require_teacher
from app.ai.service import (
    evaluate_assignment_ai, evaluate_early_warning_ai,
    generate_teacher_performance_summary_ai
)

router = APIRouter(prefix="/teacher", tags=["Teacher Module"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def teacher_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    """Renders the Teacher Dashboard with class overviews, pending submissions, and early warning alerts."""
    # Subjects taught by this teacher (or all subjects if admin)
    if current_user.role in ["super_admin", "admin"]:
        subjects = db.query(Subject).all()
    else:
        subjects = db.query(Subject).filter(Subject.teacher_id == current_user.id).all()
        
    subject_ids = [s.id for s in subjects]
    
    pending_submissions = db.query(AssignmentSubmission).join(Assignment).filter(
        Assignment.subject_id.in_(subject_ids),
        AssignmentSubmission.marks_obtained == None
    ).count() if subject_ids else 0

    open_alerts = db.query(EarlyWarningAlert).filter(
        EarlyWarningAlert.status == "open"
    ).all()

    students_count = db.query(User).filter(User.role == "student").count()

    return templates.TemplateResponse("teacher/dashboard.html", {
        "request": request,
        "user": current_user,
        "subjects": subjects,
        "pending_submissions_count": pending_submissions,
        "open_alerts": open_alerts,
        "students_count": students_count
    })


@router.get("/assignments", response_class=HTMLResponse)
def view_assignments(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    assignments = db.query(Assignment).all()
    subjects = db.query(Subject).all()
    return templates.TemplateResponse("teacher/assignments.html", {
        "request": request,
        "user": current_user,
        "assignments": assignments,
        "subjects": subjects
    })


@router.post("/assignments/create")
def create_assignment(
    subject_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    type: str = Form("theory"), # coding, pdf, theory, project
    due_days: int = Form(7),
    max_marks: int = Form(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    due_date = datetime.utcnow() + timedelta(days=due_days)
    assignment = Assignment(
        subject_id=subject_id,
        teacher_id=current_user.id,
        title=title,
        description=description,
        type=type,
        due_date=due_date,
        max_marks=max_marks
    )
    db.add(assignment)
    db.commit()
    return RedirectResponse(url="/teacher/assignments", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/submissions/{assignment_id}", response_class=HTMLResponse)
def view_submissions(assignment_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    submissions = db.query(AssignmentSubmission).filter(AssignmentSubmission.assignment_id == assignment_id).all()
    return templates.TemplateResponse("teacher/submissions.html", {
        "request": request,
        "user": current_user,
        "assignment": assignment,
        "submissions": submissions
    })


@router.post("/submissions/grade")
def grade_submission(
    submission_id: int = Form(...),
    marks_obtained: float = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    sub = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    sub.marks_obtained = marks_obtained
    sub.feedback = feedback
    db.commit()
    return RedirectResponse(url=f"/teacher/submissions/{sub.assignment_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/submissions/ai-grade/{submission_id}")
def ai_grade_submission(submission_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    """Generates AI evaluation using Gemini API for student submission."""
    sub = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    eval_res = evaluate_assignment_ai(
        title=sub.assignment.title,
        description=sub.assignment.description,
        submission=sub.submission_text or sub.code or "No text provided",
        assignment_type=sub.assignment.type
    )
    
    sub.ai_feedback = eval_res.get("feedback", "AI evaluation completed.")
    if sub.marks_obtained is None:
        sub.marks_obtained = eval_res.get("marks_suggested", 80.0)
    db.commit()
    return {"status": "success", "ai_feedback": sub.ai_feedback, "marks_suggested": eval_res.get("marks_suggested")}


@router.get("/resources", response_class=HTMLResponse)
def manage_resources(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    resources = db.query(Resource).all()
    subjects = db.query(Subject).all()
    return templates.TemplateResponse("teacher/resources.html", {
        "request": request,
        "user": current_user,
        "resources": resources,
        "subjects": subjects
    })


@router.post("/resources/upload")
async def upload_resource(
    type: str = Form(...), # video, doc, notes, cheatsheet
    title: str = Form(...),
    url: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    topic_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    resource_url = url
    if file and file.filename:
        os.makedirs("app/static/uploads/resources", exist_ok=True)
        filename = f"res_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join("app/static/uploads/resources", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        resource_url = f"/static/uploads/resources/{filename}"

    # Ensure a valid topic exists
    valid_topic = None
    if topic_id:
        valid_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not valid_topic:
        valid_topic = db.query(Topic).first()
    
    if not valid_topic:
        raise HTTPException(status_code=400, detail="No topic found to associate resource.")

    resource = Resource(type=type, title=title, url=resource_url, content=content, topic_id=valid_topic.id)
    db.add(resource)
    db.commit()
    return RedirectResponse(url="/teacher/resources", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/notifications", response_class=HTMLResponse)
def notifications_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    sent = db.query(TeacherNotification).filter(TeacherNotification.sender_teacher_id == current_user.id).order_by(TeacherNotification.sent_at.desc()).all()
    students = db.query(User).filter(User.role == "student").all()
    return templates.TemplateResponse("teacher/notifications.html", {
        "request": request,
        "user": current_user,
        "notifications": sent,
        "students": students
    })


@router.post("/notifications/send")
def send_notification(
    title: str = Form(...),
    message: str = Form(...),
    type: str = Form("general"), # greeting, birthday, congratulations, warning, assignment_reminder, exam_reminder
    recipient_student_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    # 1. Create TeacherNotification record
    notification = TeacherNotification(
        sender_teacher_id=current_user.id,
        recipient_student_id=recipient_student_id if recipient_student_id else None,
        college_id=current_user.college_id,
        department_id=current_user.department_id,
        type=type,
        title=title,
        message=message
    )
    db.add(notification)
    db.commit()

    # 2. Create SystemNotification for targeted student or all students
    if recipient_student_id:
        target_students = db.query(User).filter(User.id == recipient_student_id).all()
    else:
        # Broadcast to all students in college or system wide
        q = db.query(User).filter(User.role == "student")
        if current_user.college_id:
            q = q.filter((User.college_id == current_user.college_id) | (User.college_id == None))
        target_students = q.all()

    for s in target_students:
        sys_notif = SystemNotification(
            student_id=s.id,
            title=f"📢 {title} (Prof. {current_user.name})",
            message=message,
            type=type,
            link="/notifications",
            is_read=False
        )
        db.add(sys_notif)

    db.commit()
    return RedirectResponse(url="/teacher/notifications", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/early-warning", response_class=HTMLResponse)
def early_warning_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    alerts = db.query(EarlyWarningAlert).order_by(EarlyWarningAlert.created_at.desc()).all()
    students = db.query(User).filter(User.role == "student").all()
    return templates.TemplateResponse("teacher/early_warning.html", {
        "request": request,
        "user": current_user,
        "alerts": alerts,
        "students": students
    })


@router.post("/early-warning/analyze/{student_id}")
def analyze_student_risk(student_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Evaluate parameters
    attendance_recs = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id).all()
    present_cnt = sum(1 for a in attendance_recs if a.status == "Present")
    total_att = len(attendance_recs) if attendance_recs else 1
    att_pct = (present_cnt / total_att) * 100.0 if attendance_recs else 100.0

    eval_res = evaluate_early_warning_ai(
        student_name=student.name,
        study_minutes=int(student.learning_hours * 60),
        attendance_pct=att_pct,
        quiz_avg=student.quiz_avg,
        coding_avg=student.coding_avg,
        missing_assignments=0
    )

    alert = EarlyWarningAlert(
        student_id=student_id,
        teacher_id=current_user.id,
        risk_level=eval_res.get("risk_level", "medium"),
        trigger_reason=eval_res.get("trigger_reason", "AI evaluation triggered"),
        ai_analysis=eval_res.get("ai_analysis", "")
    )
    db.add(alert)
    db.commit()
    return RedirectResponse(url="/teacher/early-warning", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/performance", response_class=HTMLResponse)
def view_all_students_performance(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    """Overview of all students with attempt counts and average scores."""
    students = db.query(User).filter(User.role == "student").order_by(User.name).all()
    
    student_stats = []
    for s in students:
        quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == s.id).all()
        quiz_attempts_count = len(quiz_attempts)
        quiz_avg = round(sum(a.score for a in quiz_attempts) / quiz_attempts_count, 1) if quiz_attempts_count > 0 else (s.quiz_avg or 0.0)
        
        coding_submissions = db.query(CodingSubmission).filter(CodingSubmission.student_id == s.id).all()
        coding_submissions_count = len(coding_submissions)
        coding_avg = round(sum(c.score_earned for c in coding_submissions) / coding_submissions_count, 1) if coding_submissions_count > 0 else (s.coding_avg or 0.0)
        
        assignment_submissions = db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == s.id).all()
        assignments_count = len(assignment_submissions)
        graded_assignments = [sub for sub in assignment_submissions if sub.marks_obtained is not None and sub.assignment and sub.assignment.max_marks]
        assignment_avg = round(sum((sub.marks_obtained / sub.assignment.max_marks * 100.0) for sub in graded_assignments) / len(graded_assignments), 1) if graded_assignments else 0.0
        
        # Overall academic composite marks percentage
        composite_marks = round((quiz_avg * 0.4 + coding_avg * 0.35 + (assignment_avg if assignment_avg > 0 else quiz_avg) * 0.25), 1)

        # Performance Tier Badge
        if composite_marks >= 85:
            performance_tier = "Distinction ⭐"
            tier_badge = "bg-success text-white"
        elif composite_marks >= 70:
            performance_tier = "Merit 🚀"
            tier_badge = "bg-primary text-white"
        elif composite_marks >= 50:
            performance_tier = "Satisfactory ⚡"
            tier_badge = "bg-warning text-dark"
        else:
            performance_tier = "Needs Support ⚠️"
            tier_badge = "bg-danger text-white"

        student_stats.append({
            "student": s,
            "quiz_attempts_count": quiz_attempts_count,
            "coding_submissions_count": coding_submissions_count,
            "assignments_count": assignments_count,
            "quiz_avg": quiz_avg,
            "coding_avg": coding_avg,
            "assignment_avg": assignment_avg,
            "composite_marks": composite_marks,
            "performance_tier": performance_tier,
            "tier_badge": tier_badge
        })
        
    return templates.TemplateResponse("teacher/performance.html", {
        "request": request,
        "user": current_user,
        "student_stats": student_stats
    })


@router.get("/performance/{student_id}", response_class=HTMLResponse)
def view_student_performance_detail(student_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    """Detailed attempt-by-attempt breakdown for a specific student."""
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Fetch quiz attempts grouped by quiz
    quiz_attempts_raw = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).order_by(QuizAttempt.attempted_at.desc()).all()
    
    # Group quiz attempts and calculate attempt numbers
    quiz_history = []
    quiz_attempts_by_quiz = {}
    for att in reversed(quiz_attempts_raw): # Oldest first to count 1, 2, 3...
        q_id = att.quiz_id
        if q_id not in quiz_attempts_by_quiz:
            quiz_attempts_by_quiz[q_id] = []
        quiz_attempts_by_quiz[q_id].append(att)
        attempt_number = len(quiz_attempts_by_quiz[q_id])
        
        quiz_obj = db.query(Quiz).filter(Quiz.id == q_id).first()
        topic_obj = db.query(Topic).filter(Topic.id == quiz_obj.topic_id).first() if quiz_obj else None
        
        # Calculate actual questions count and marks obtained
        q_count = db.query(Question).filter(Question.quiz_id == q_id, Question.is_deleted == False).count()
        total_questions = q_count if q_count > 0 else 10
        actual_marks = round((att.score / 100.0) * total_questions) if att.score <= 100.0 else int(att.score)

        quiz_history.insert(0, {
            "attempt_id": att.id,
            "quiz_id": q_id,
            "quiz_title": quiz_obj.title if (quiz_obj and quiz_obj.title) else (topic_obj.title if topic_obj else f"Quiz #{q_id}"),
            "topic_title": topic_obj.title if topic_obj else "Topic Checkpoint",
            "attempt_number": attempt_number,
            "score": att.score,
            "actual_marks": actual_marks,
            "total_questions": total_questions,
            "passed": att.passed,
            "attempted_at": att.attempted_at
        })

    # Fetch coding submissions grouped by challenge
    coding_subs_raw = db.query(CodingSubmission).filter(CodingSubmission.student_id == student_id).order_by(CodingSubmission.submitted_at.desc()).all()
    
    coding_history = []
    coding_by_challenge = {}
    for sub in reversed(coding_subs_raw):
        c_id = sub.challenge_id
        if c_id not in coding_by_challenge:
            coding_by_challenge[c_id] = []
        coding_by_challenge[c_id].append(sub)
        attempt_number = len(coding_by_challenge[c_id])
        
        challenge_obj = db.query(CodingChallenge).filter(CodingChallenge.id == c_id).first()
        
        coding_history.insert(0, {
            "submission_id": sub.id,
            "challenge_id": c_id,
            "challenge_title": challenge_obj.title if challenge_obj else f"Challenge #{c_id}",
            "attempt_number": attempt_number,
            "status": sub.status,
            "score_earned": sub.score_earned,
            "submitted_code": sub.submitted_code,
            "submitted_at": sub.submitted_at
        })

    # Fetch assignment submissions
    assignment_subs_raw = db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == student_id).order_by(AssignmentSubmission.submitted_at.desc()).all()
    assignment_history = []
    for asub in assignment_subs_raw:
        asgn = asub.assignment
        pct = round((asub.marks_obtained / asgn.max_marks * 100), 1) if (asub.marks_obtained is not None and asgn and asgn.max_marks) else None
        assignment_history.append({
            "submission_id": asub.id,
            "assignment_title": asgn.title if asgn else f"Assignment #{asub.assignment_id}",
            "subject_name": asgn.subject.name if (asgn and asgn.subject) else "Subject",
            "max_marks": asgn.max_marks if asgn else 100,
            "marks_obtained": asub.marks_obtained,
            "percentage": pct,
            "feedback": asub.feedback,
            "ai_feedback": asub.ai_feedback,
            "code": asub.code,
            "submission_text": asub.submission_text,
            "file_url": asub.file_url,
            "submitted_at": asub.submitted_at
        })

    # Summary Scores
    quiz_avg = round(sum(a.score for a in quiz_attempts_raw) / len(quiz_attempts_raw), 1) if quiz_attempts_raw else student.quiz_avg
    coding_avg = round(sum(c.score_earned for c in coding_subs_raw) / len(coding_subs_raw), 1) if coding_subs_raw else student.coding_avg
    graded_assignments = [h for h in assignment_history if h["marks_obtained"] is not None]
    assignment_avg = round(sum(h["percentage"] for h in graded_assignments) / len(graded_assignments), 1) if graded_assignments else 0.0

    return templates.TemplateResponse("teacher/student_performance_detail.html", {
        "request": request,
        "user": current_user,
        "student": student,
        "quiz_history": quiz_history,
        "coding_history": coding_history,
        "assignment_history": assignment_history,
        "quiz_avg": quiz_avg,
        "coding_avg": coding_avg,
        "assignment_avg": assignment_avg
    })


# =======================================================
# TEACHER & HOD EXTRA KNOWLEDGE IMPROVEMENT VIDEOS
# =======================================================
@router.get("/knowledge-videos", response_class=HTMLResponse)
def manage_knowledge_videos(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    """Teacher and HOD dashboard to manage extra videos for student knowledge improvement."""
    videos = db.query(KnowledgeVideo).order_by(KnowledgeVideo.created_at.desc()).all()
    subjects = db.query(Subject).all()
    topics = db.query(Topic).filter(Topic.is_deleted == False).all()
    
    return templates.TemplateResponse("teacher/knowledge_videos.html", {
        "request": request,
        "user": current_user,
        "videos": videos,
        "subjects": subjects,
        "topics": topics
    })


@router.post("/knowledge-videos/add")
async def add_knowledge_video(
    title: str = Form(...),
    video_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: str = Form("Knowledge Booster"),
    subject_id: Optional[int] = Form(None),
    topic_id: Optional[int] = Form(None),
    is_hod_recommended: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Adds a new knowledge improvement video curated by Teacher or HOD."""
    cleaned_url = (video_url or "").strip()
    
    if file and file.filename:
        os.makedirs("app/static/uploads/videos", exist_ok=True)
        filename = f"vid_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join("app/static/uploads/videos", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        cleaned_url = f"/static/uploads/videos/{filename}"
    elif "youtube.com/watch?v=" in cleaned_url:
        video_id = cleaned_url.split("watch?v=")[1].split("&")[0]
        cleaned_url = f"https://www.youtube.com/embed/{video_id}"
    elif "youtu.be/" in cleaned_url:
        video_id = cleaned_url.split("youtu.be/")[1].split("?")[0]
        cleaned_url = f"https://www.youtube.com/embed/{video_id}"

    # If current user is HOD, auto-flag as HOD recommended
    hod_flag = True if current_user.role == "hod" else is_hod_recommended

    video = KnowledgeVideo(
        title=title.strip(),
        description=description.strip() if description else "Supplementary video curated to boost student practical understanding.",
        video_url=cleaned_url or "/static/uploads/videos/default.mp4",
        category=category,
        subject_id=subject_id if subject_id else None,
        topic_id=topic_id if topic_id else None,
        teacher_id=current_user.id,
        is_hod_recommended=hod_flag
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    # Broadcast notification to students
    target_students = db.query(User).filter(User.role == "student").all()
    hod_tag = " [⭐ HOD Curated]" if hod_flag else ""
    for s in target_students:
        notif = SystemNotification(
            student_id=s.id,
            title=f"🎥 New Knowledge Video: {title}{hod_tag}",
            message=f"Prof. {current_user.name} added a new knowledge booster video '{title}'. Watch now to improve your concepts!",
            type="study",
            link="/student/resources",
            is_read=False
        )
        db.add(notif)
    db.commit()

    return RedirectResponse(url="/teacher/knowledge-videos", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/knowledge-videos/delete/{video_id}")
def delete_knowledge_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    """Deletes a knowledge video."""
    video = db.query(KnowledgeVideo).filter(KnowledgeVideo.id == video_id).first()
    if video:
        if current_user.role in ["hod", "super_admin", "admin"] or video.teacher_id == current_user.id:
            db.delete(video)
            db.commit()
    return RedirectResponse(url="/teacher/knowledge-videos", status_code=status.HTTP_303_SEE_OTHER)

