from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Career, Recommendation, Topic, StudentProgress, QuizAttempt
from app.ai.service import generate_ai_recommendation
from app.utils.auth import get_current_user

router = APIRouter(prefix="/recommendation", tags=["AI Recommendation"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def view_career_guidance_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Renders the Student Career Guidance & AI Roadmap Coach Page.
    """
    # Fetch student career
    career = db.query(Career).filter(Career.id == current_user.current_career_id).first() if current_user.current_career_id else db.query(Career).first()
    
    # Fetch latest recommendation
    latest_rec = db.query(Recommendation).filter(Recommendation.student_id == current_user.id).order_by(Recommendation.created_at.desc()).first()
    
    # Analyze topic progress
    all_topics = db.query(Topic).all()
    completed_topic_ids = [p.topic_id for p in current_user.progress if p.status == "Completed"]
    
    weak_topics = []
    strong_topics = []
    for p in current_user.progress:
        attempts = db.query(QuizAttempt).join(QuizAttempt.quiz).filter(
            QuizAttempt.student_id == current_user.id,
            QuizAttempt.quiz.has(topic_id=p.topic_id)
        ).all()
        if attempts:
            avg_s = sum(a.score for a in attempts) / len(attempts)
            if avg_s < 75:
                weak_topics.append(p.topic.title)
            elif avg_s >= 85:
                strong_topics.append(p.topic.title)

    return templates.TemplateResponse("recommendation/index.html", {
        "request": request,
        "user": current_user,
        "career": career,
        "recommendation": latest_rec,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "completed_count": len(completed_topic_ids),
        "total_topics": len(all_topics)
    })

@router.post("/generate")
def get_recommendation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Invokes the AI recommendation logic to analyze current progress and output
    adaptive study actions. Saves to database and returns.
    """
    try:
        recommendation_data = generate_ai_recommendation(db, current_user.id)
        return recommendation_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation: {str(e)}")

