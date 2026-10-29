from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, CodingSubmission, ActivityLog
from app.utils.auth import get_current_user
from app.coding.routes import execute_python_code, execute_java_code, execute_cpp_code

router = APIRouter(prefix="/code-editor", tags=["Online Code Editor"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_code_editor_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recent_submissions = db.query(CodingSubmission).filter(CodingSubmission.student_id == current_user.id).order_by(CodingSubmission.submitted_at.desc()).limit(15).all()
    return templates.TemplateResponse(
        "code_editor/index.html",
        {
            "request": request,
            "user": current_user,
            "submissions": recent_submissions
        }
    )

@router.post("/run")
def run_code_in_editor(
    code: str = Form(...),
    language: str = Form("python"),
    test_cases: str = Form("[]"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        lang = language.lower().strip()
        if lang in ["java"]:
            status_str, score, test_results = execute_java_code(code, test_cases)
        elif lang in ["cpp", "c++"]:
            status_str, score, test_results = execute_cpp_code(code, test_cases)
        else:
            status_str, score, test_results = execute_python_code(code, test_cases)

        return JSONResponse({
            "status": status_str,
            "score": score,
            "test_results": test_results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
