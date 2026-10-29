import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Career, Roadmap, Topic, StudentProgress, Resource, CodingChallenge, Quiz, ActivityLog, Analytics
from app.utils.auth import get_current_user

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])
templates = Jinja2Templates(directory="app/templates")

import json

@router.get("/select-career", response_class=HTMLResponse)
def get_select_career(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    careers = db.query(Career).all()
    return templates.TemplateResponse(
        "dashboard/select_career.html",
        {
            "request": request,
            "user": current_user,
            "careers": careers
        }
    )


@router.post("/select-career")
def select_career(
    career_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career path not found")
    
    # Enroll student in this career if not already enrolled
    if career not in current_user.enrolled_careers:
        current_user.enrolled_careers.append(career)
    
    # Set this career as active focus path
    current_user.current_career_id = career_id
    db.commit()

    # Log action
    log = ActivityLog(user_id=current_user.id, action="enroll_career", details=f"Enrolled in pathway: {career.name}")
    db.add(log)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


@router.get("/view", response_class=HTMLResponse)
def view_roadmap(
    request: Request,
    career_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Determine the target career to display
    target_career_id = career_id or current_user.current_career_id
    
    if not target_career_id:
        if current_user.enrolled_careers:
            target_career_id = current_user.enrolled_careers[0].id
        else:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    # Automatically set active focus pathway context
    if current_user.current_career_id != target_career_id:
        current_user.current_career_id = target_career_id
        db.commit()
        
    career = db.query(Career).filter(Career.id == target_career_id, Career.is_deleted == False).first()
    roadmaps = db.query(Roadmap).filter(
        Roadmap.career_id == career.id,
        Roadmap.is_deleted == False
    ).order_by(Roadmap.order).all()
    
    # Filter active topics for each roadmap
    for rm in roadmaps:
        rm.active_topics = [t for t in rm.topics if not getattr(t, "is_deleted", False)]
    
    # Get user progress mapping
    progress_records = db.query(StudentProgress).filter(StudentProgress.student_id == current_user.id).all()
    progress_map = {p.topic_id: p.status for p in progress_records}

    return templates.TemplateResponse(
        "roadmap/view_roadmap.html",
        {
            "request": request,
            "user": current_user,
            "career": career,
            "roadmaps": roadmaps,
            "progress_map": progress_map
        }
    )


@router.get("/topic/{topic_id}", response_class=HTMLResponse)
def view_topic(topic_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.models import Video
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check progress status (Ensure student has unlocked this topic)
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id,
        StudentProgress.topic_id == topic_id
    ).first()

    if not progress:
        progress = StudentProgress(student_id=current_user.id, topic_id=topic_id, status="Unlocked")
        db.add(progress)
        db.commit()
        db.refresh(progress)

    if progress.status == "Locked" and current_user.role != "admin":
        return HTMLResponse("<h3>Access Denied. This topic is locked. Complete previous topics first!</h3>", status_code=403)

    if progress.status == "Locked" and current_user.role == "admin":
        progress.status = "Unlocked"
        db.commit()

    # Load coding challenges
    challenges = db.query(CodingChallenge).filter(CodingChallenge.topic_id == topic_id, CodingChallenge.is_deleted == False).all()
    
    # Load quiz
    quiz = db.query(Quiz).filter(Quiz.topic_id == topic_id, Quiz.is_deleted == False).first()

    # 1. Load YouTube videos directly from MySQL persistent videos table
    db_videos = db.query(Video).filter(
        Video.topic_id == topic_id,
        Video.is_deleted == False,
        Video.is_active == True
    ).order_by(Video.display_order).all()

    if db_videos:
        youtube_videos_list = [{"title": v.title, "url": v.youtube_url} for v in db_videos]
    elif topic.youtube_videos:
        try:
            youtube_videos_list = json.loads(topic.youtube_videos) if isinstance(topic.youtube_videos, str) else topic.youtube_videos
        except Exception:
            youtube_videos_list = []
    else:
        youtube_videos_list = []

    if not youtube_videos_list or len(youtube_videos_list) == 0:
        t_lower = topic.title.lower() if topic.title else ""
        if "python" in t_lower:
            youtube_videos_list = [
                {"title": f"{topic.title} - Python Full Video Course", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"},
                {"title": f"{topic.title} - Practical Tutorial", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"}
            ]
        elif "web" in t_lower or "html" in t_lower or "css" in t_lower or "js" in t_lower or "javascript" in t_lower:
            youtube_videos_list = [
                {"title": f"{topic.title} - Web Development Video Tutorial", "url": "https://www.youtube.com/watch?v=UB1O30fR-EE"},
                {"title": f"{topic.title} - Hands-on Project Guide", "url": "https://www.youtube.com/watch?v=zJSY8tbf_ys"}
            ]
        elif "sql" in t_lower or "data" in t_lower or "db" in t_lower or "database" in t_lower:
            youtube_videos_list = [
                {"title": f"{topic.title} - SQL & Database Full Tutorial", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
                {"title": f"{topic.title} - Queries & Schema Design", "url": "https://www.youtube.com/watch?v=7S_tz1z_5bA"}
            ]
        elif "react" in t_lower or "frontend" in t_lower:
            youtube_videos_list = [
                {"title": f"{topic.title} - React JS Masterclass", "url": "https://www.youtube.com/watch?v=w7ejDZ8SWv8"},
                {"title": f"{topic.title} - Modern Frontend Guide", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8"}
            ]
        elif "fastapi" in t_lower or "backend" in t_lower or "api" in t_lower:
            youtube_videos_list = [
                {"title": f"{topic.title} - FastAPI & REST API Tutorial", "url": "https://www.youtube.com/watch?v=7t2alSnE2-I"},
                {"title": f"{topic.title} - Backend Architecture Guide", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA"}
            ]
        else:
            youtube_videos_list = [
                {"title": f"{topic.title} - Video Lecture & Guide", "url": "https://www.youtube.com/watch?v=zOjov-2OZ0E"},
                {"title": f"{topic.title} - Practical Concepts Explained", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"}
            ]

    docs_list = []
    if topic.official_documentation:
        try:
            docs_list = json.loads(topic.official_documentation) if isinstance(topic.official_documentation, str) else topic.official_documentation
        except Exception:
            docs_list = []

    practice_list = []
    if topic.practice_questions:
        try:
            practice_list = json.loads(topic.practice_questions) if isinstance(topic.practice_questions, str) else topic.practice_questions
        except Exception:
            practice_list = []

    # Log action
    log = ActivityLog(user_id=current_user.id, action="view_topic", details=f"Viewed topic: {topic.title}")
    db.add(log)
    db.commit()

    return templates.TemplateResponse(
        "roadmap/topic_detail.html",
        {
            "request": request,
            "user": current_user,
            "topic": topic,
            "progress": progress,
            "challenges": challenges,
            "quiz": quiz,
            "youtube_videos_list": youtube_videos_list,
            "docs_list": docs_list,
            "practice_list": practice_list
        }
    )



@router.post("/topic/{topic_id}/heartbeat")
def study_heartbeat(topic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Heartbeat endpoint called by JS client every 60 seconds when student is active on the page.
    Increments study time in User profile, StudentProgress, and Analytics.
    Updates daily streak logic.
    """
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id,
        StudentProgress.topic_id == topic_id
    ).first()
    
    if progress:
        # 1. Increment progress minutes
        progress.study_time_minutes += 1
        
        # 2. Increment user hours
        current_user.learning_hours += (1 / 60.0)
        
        # 3. Update Daily Streak
        today = datetime.date.today()
        if current_user.last_active_date:
            delta = today - current_user.last_active_date
            if delta.days == 1:
                # Active consecutive day, increment streak
                current_user.daily_streak += 1
            elif delta.days > 1:
                # Missed a day, reset streak to 1
                current_user.daily_streak = 1
            # If delta.days == 0 (same day), do nothing (keep current streak)
        else:
            # First time activity, set streak to 1
            current_user.daily_streak = 1
            
        current_user.last_active_date = today

        # 4. Increment daily analytics
        analytic_record = db.query(Analytics).filter(
            Analytics.student_id == current_user.id,
            Analytics.date == today
        ).first()

        if not analytic_record:
            analytic_record = Analytics(student_id=current_user.id, date=today, study_time_minutes=1)
            db.add(analytic_record)
        else:
            analytic_record.study_time_minutes += 1
        db.commit()
        return {"status": "success", "minutes_studied": progress.study_time_minutes, "streak": current_user.daily_streak}
        
    return {"status": "error", "message": "Progress not found"}


@router.post("/topic/{topic_id}/complete")
def complete_topic(topic_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Manually marks a topic as completed and unlocks the next topic in the learning pathway.
    """
    # 1. Fetch current progress
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id,
        StudentProgress.topic_id == topic_id
    ).first()
    
    if not progress:
        progress = StudentProgress(student_id=current_user.id, topic_id=topic_id, status="Unlocked")
        db.add(progress)
        db.commit()
        db.refresh(progress)

    # Check 75% Quiz Passing Rule (Mandatory for non-admin users)
    quiz = db.query(Quiz).filter(Quiz.topic_id == topic_id, Quiz.is_deleted == False).first()
    if quiz and current_user.role not in ["admin", "super_admin"]:
        best_attempt = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.student_id == current_user.id,
            QuizAttempt.score >= 75.0
        ).first()
        if not best_attempt:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "🔒 Mandatory Progression Rule: You must score at least 75% on the topic quiz to complete this topic and unlock the next roadmap milestone."
                }
            )

    if progress.status != "Completed":
        progress.status = "Completed"
        progress.completed_at = datetime.datetime.utcnow()
        
        # Increment topics completed in today's analytics
        today = datetime.date.today()
        analytic_rec = db.query(Analytics).filter(
            Analytics.student_id == current_user.id,
            Analytics.date == today
        ).first()
        if not analytic_rec:
            analytic_rec = Analytics(student_id=current_user.id, date=today, topics_completed=1)
            db.add(analytic_rec)
        else:
            analytic_rec.topics_completed += 1
            
        db.commit()

    # 2. Unlock the next topic in the roadmap
    current_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if current_topic:
        roadmap_topics = db.query(Topic).filter(
            Topic.roadmap_id == current_topic.roadmap_id
        ).order_by(Topic.order).all()
        
        # Check within current roadmap
        next_t = None
        for idx, t in enumerate(roadmap_topics):
            if t.id == current_topic.id and idx + 1 < len(roadmap_topics):
                next_t = roadmap_topics[idx + 1]
                break
        
        # If not found in current roadmap, check subsequent roadmap order
        if not next_t:
            current_roadmap = db.query(Roadmap).filter(Roadmap.id == current_topic.roadmap_id).first()
            next_roadmap = db.query(Roadmap).filter(
                Roadmap.career_id == current_user.current_career_id,
                Roadmap.order > current_roadmap.order
            ).order_by(Roadmap.order).first()
            if next_roadmap:
                next_t = db.query(Topic).filter(Topic.roadmap_id == next_roadmap.id).order_by(Topic.order).first()
        
        if next_t:
            next_progress = db.query(StudentProgress).filter(
                StudentProgress.student_id == current_user.id,
                StudentProgress.topic_id == next_t.id
            ).first()
            if not next_progress:
                next_progress = StudentProgress(
                    student_id=current_user.id,
                    topic_id=next_t.id,
                    status="Unlocked"
                )
                db.add(next_progress)
            elif next_progress.status == "Locked":
                next_progress.status = "Unlocked"
            db.commit()

    # Log action
    log = ActivityLog(user_id=current_user.id, action="complete_topic", details=f"Completed topic manually: {current_topic.title if current_topic else topic_id}")
    db.add(log)
    db.commit()

    return {"status": "success", "message": "Topic completed successfully."}

