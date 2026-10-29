from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Career, Roadmap, Topic, StudentProgress, Recommendation, ActivityLog
from app.utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_dashboard(request: Request, view: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Role-based routing unless explicitly requesting student preview
    if view != "student":
        if current_user.role in ["super_admin", "admin"]:
            return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        elif current_user.role in ["principal", "college_admin"]:
            return RedirectResponse(url="/principal/dashboard", status_code=status.HTTP_302_FOUND)
        elif current_user.role == "hod":
            return RedirectResponse(url="/hod/dashboard", status_code=status.HTTP_302_FOUND)
        elif current_user.role == "teacher":
            return RedirectResponse(url="/teacher/dashboard", status_code=status.HTTP_302_FOUND)

    # 2. Check if student is enrolled in any career paths
    if not current_user.enrolled_careers:
        careers = db.query(Career).filter(Career.is_active == True).all()
        return templates.TemplateResponse(
            "dashboard/select_career.html", 
            {"request": request, "user": current_user, "careers": careers}
        )

    # 3. Ensure an active career ID is selected contextually
    if not current_user.current_career_id:
        current_user.current_career_id = current_user.enrolled_careers[0].id
        db.commit()

    # Calculate metrics for all enrolled pathways
    enrolled_paths = []
    for ec in current_user.enrolled_careers:
        ec_topics = db.query(Topic).join(Roadmap).filter(Roadmap.career_id == ec.id).all()
        ec_total = len(ec_topics)
        
        # Calculate how many of these specific topics are marked Completed
        ec_completed = 0
        if ec_topics:
            topic_ids = [t.id for t in ec_topics]
            ec_completed = db.query(StudentProgress).filter(
                StudentProgress.student_id == current_user.id,
                StudentProgress.status == "Completed",
                StudentProgress.topic_id.in_(topic_ids)
            ).count()
            
        ec_percent = round((ec_completed / ec_total * 100), 1) if ec_total > 0 else 0.0
        enrolled_paths.append({
            "career": ec,
            "completed": ec_completed,
            "total": ec_total,
            "percent": ec_percent,
            "is_active": ec.id == current_user.current_career_id
        })

    # 4. Calculate metrics for the active focus pathway
    career = db.query(Career).filter(Career.id == current_user.current_career_id).first()
    
    # Get all topics in career path
    all_topics = db.query(Topic).join(Roadmap).filter(
        Roadmap.career_id == current_user.current_career_id
    ).order_by(Roadmap.order, Topic.order).all()
    
    total_topics = len(all_topics)
    
    # Ensure progress records exist for all topics in this career for this user
    user_progress = db.query(StudentProgress).filter(StudentProgress.student_id == current_user.id).all()
    progress_map = {p.topic_id: p for p in user_progress}
    
    initialized_progress = False
    for i, topic in enumerate(all_topics):
        if topic.id not in progress_map:
            # Set the first topic to Unlocked, rest to Locked
            initial_status = "Unlocked" if i == 0 else "Locked"
            new_p = StudentProgress(
                student_id=current_user.id,
                topic_id=topic.id,
                status=initial_status
            )
            db.add(new_p)
            progress_map[topic.id] = new_p
            initialized_progress = True
            
    if initialized_progress:
        db.commit()
        # Refetch progress
        user_progress = db.query(StudentProgress).filter(StudentProgress.student_id == current_user.id).all()
        progress_map = {p.topic_id: p for p in user_progress}

    completed_progress = [p for p in user_progress if p.status == "Completed" and p.topic_id in [t.id for t in all_topics]]
    completed_count = len(completed_progress)
    progress_percentage = round((completed_count / total_topics * 100), 1) if total_topics > 0 else 0.0

    # Determine Current and Next Topic
    current_topic = None
    next_topic = None
    found_current = False
    
    for topic in all_topics:
        p = progress_map.get(topic.id)
        if p and p.status != "Completed":
            if not found_current:
                current_topic = topic
                found_current = True
            else:
                next_topic = topic
                break

    # Fetch last 5 activities
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(5).all()

    # Fetch latest recommendation
    recommendation = db.query(Recommendation).filter(
        Recommendation.student_id == current_user.id
    ).order_by(Recommendation.created_at.desc()).first()

    return templates.TemplateResponse(
        "dashboard/student.html",
        {
            "request": request,
            "user": current_user,
            "career": career,
            "progress_percent": progress_percentage,
            "completed_count": completed_count,
            "total_topics": total_topics,
            "current_topic": current_topic,
            "next_topic": next_topic,
            "activities": activities,
            "recommendation": recommendation,
            "enrolled_paths": enrolled_paths
        }
    )
