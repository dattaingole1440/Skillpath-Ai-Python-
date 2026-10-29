import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, DailyChallenge, UserDailyChallenge, ActivityLog
from app.utils.auth import get_current_user

router = APIRouter(tags=["Gamification"])
templates = Jinja2Templates(directory="app/templates")

def calculate_rank(xp: int) -> str:
    if xp >= 5000:
        return "Legend"
    elif xp >= 2500:
        return "Master"
    elif xp >= 1200:
        return "Expert"
    elif xp >= 600:
        return "Developer"
    elif xp >= 200:
        return "Explorer"
    else:
        return "Beginner"

@router.get("/leaderboard", response_class=HTMLResponse)
def get_leaderboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    top_students = db.query(User).filter(User.role == "student").order_by(User.xp.desc(), User.daily_streak.desc()).limit(20).all()
    
    # Update current user's rank
    current_user.rank = calculate_rank(current_user.xp)
    db.commit()

    return templates.TemplateResponse(
        "gamification/leaderboard.html",
        {
            "request": request,
            "user": current_user,
            "students": top_students
        }
    )

@router.get("/daily-challenges", response_class=HTMLResponse)
def get_daily_challenges_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.date.today()
    challenges = db.query(DailyChallenge).filter(DailyChallenge.date == today).all()

    # Seed default daily challenges if empty for today
    if not challenges:
        c1 = DailyChallenge(
            date=today,
            challenge_type="quiz",
            title="Daily Python & Logic Quiz",
            description="Answer 3 rapid-fire concepts questions to test core syntax knowledge.",
            reward_xp=40,
            reward_coins=15
        )
        c2 = DailyChallenge(
            date=today,
            challenge_type="coding",
            title="Daily Coding Challenge: String Reversal",
            description="Write an efficient algorithm to reverse string tokens in place.",
            reward_xp=50,
            reward_coins=20
        )
        c3 = DailyChallenge(
            date=today,
            challenge_type="interview",
            title="Daily Interview Prep Question",
            description="Formulate a structured STAR response to 'Describe a complex technical challenge you solved'.",
            reward_xp=35,
            reward_coins=10
        )
        db.add_all([c1, c2, c3])
        db.commit()
        challenges = [c1, c2, c3]

    completions = db.query(UserDailyChallenge).filter(UserDailyChallenge.student_id == current_user.id).all()
    completed_ids = [c.challenge_id for c in completions]

    return templates.TemplateResponse(
        "gamification/daily.html",
        {
            "request": request,
            "user": current_user,
            "challenges": challenges,
            "completed_ids": completed_ids
        }
    )

@router.post("/api/gamification/complete-challenge/{challenge_id}")
def complete_daily_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    challenge = db.query(DailyChallenge).filter(DailyChallenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    existing = db.query(UserDailyChallenge).filter(
        UserDailyChallenge.student_id == current_user.id,
        UserDailyChallenge.challenge_id == challenge_id
    ).first()

    if existing:
        return JSONResponse({"status": "already_completed", "message": "You have already completed this daily challenge today."})

    completion = UserDailyChallenge(
        student_id=current_user.id,
        challenge_id=challenge_id
    )
    db.add(completion)

    current_user.xp += challenge.reward_xp
    current_user.coins += challenge.reward_coins
    current_user.rank = calculate_rank(current_user.xp)
    db.commit()

    log = ActivityLog(user_id=current_user.id, action="complete_daily_challenge", details=f"Completed daily challenge '{challenge.title}' (+{challenge.reward_xp} XP).")
    db.add(log)
    db.commit()

    return JSONResponse({"status": "success", "xp": current_user.xp, "coins": current_user.coins, "rank": current_user.rank})
