import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, StudentProgress, QuizAttempt, CodingSubmission, Analytics
from app.utils.auth import get_current_user
from app.schemas import schemas

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/data", response_model=schemas.AnalyticsResponse)
def get_analytics_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns analytics datasets for the past 7 days, including study hours,
    quiz performance, coding challenge performance, and topics completed.
    """
    today = datetime.date.today()
    # Get past 7 dates
    date_list = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime("%b %d") for d in date_list]

    weekly_hours = [0.0] * 7
    quiz_performance = [0.0] * 7
    coding_performance = [0.0] * 7
    topics_completed = [0] * 7

    # Query analytics for the user in date range
    records = db.query(Analytics).filter(
        Analytics.student_id == current_user.id,
        Analytics.date >= date_list[0],
        Analytics.date <= date_list[-1]
    ).all()

    record_map = {r.date: r for r in records}

    for idx, d in enumerate(date_list):
        rec = record_map.get(d)
        if rec:
            # Convert minutes to hours
            weekly_hours[idx] = round(rec.study_time_minutes / 60.0, 2)
            quiz_performance[idx] = rec.quiz_score
            coding_performance[idx] = rec.coding_score
            topics_completed[idx] = rec.topics_completed

    return {
        "labels": labels,
        "weekly_hours": weekly_hours,
        "quiz_performance": quiz_performance,
        "coding_performance": coding_performance,
        "topics_completed": topics_completed
    }
