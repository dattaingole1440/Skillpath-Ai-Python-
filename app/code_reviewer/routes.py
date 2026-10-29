from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, CodeReview, ActivityLog
from app.utils.auth import get_current_user
from app.ai.service import review_code_ai

router = APIRouter(prefix="/code-reviewer", tags=["AI Code Reviewer"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_code_reviewer_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reviews = db.query(CodeReview).filter(CodeReview.student_id == current_user.id).order_by(CodeReview.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(
        "code_reviewer/index.html",
        {
            "request": request,
            "user": current_user,
            "reviews": reviews
        }
    )

@router.post("/analyze")
def analyze_code(
    code: str = Form(...),
    language: str = Form("python"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    try:
        review_data = review_code_ai(code, language)

        review = CodeReview(
            student_id=current_user.id,
            language=language,
            code=code,
            score=review_data.get("score", 80),
            bugs=review_data.get("bugs", ""),
            complexity=review_data.get("complexity", ""),
            readability=review_data.get("readability", ""),
            performance=review_data.get("performance", ""),
            security=review_data.get("security", ""),
            suggestions=review_data.get("suggestions", ""),
            improved_code=review_data.get("improved_code", ""),
            explanation=review_data.get("explanation", "")
        )
        db.add(review)
        current_user.xp += 15
        db.commit()
        db.refresh(review)

        log = ActivityLog(user_id=current_user.id, action="ai_code_review", details=f"Reviewed {language} code snippet with score {review.score}%.")
        db.add(log)
        db.commit()

        return JSONResponse({"status": "success", "review": {
            "id": review.id,
            "score": review.score,
            "bugs": review.bugs,
            "complexity": review.complexity,
            "readability": review.readability,
            "performance": review.performance,
            "security": review.security,
            "suggestions": review.suggestions,
            "improved_code": review.improved_code,
            "explanation": review.explanation
        }})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
