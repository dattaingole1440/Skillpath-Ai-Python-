import json
from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, InterviewSession, InterviewQA, ActivityLog
from app.utils.auth import get_current_user
from app.ai.service import generate_interview_question_ai, evaluate_interview_answer_ai

router = APIRouter(prefix="/mock-interview", tags=["Mock Interview"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_mock_interview_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(InterviewSession).filter(InterviewSession.student_id == current_user.id).order_by(InterviewSession.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(
        "interview/index.html",
        {
            "request": request,
            "user": current_user,
            "sessions": sessions
        }
    )

@router.post("/start")
def start_interview_session(
    interview_type: str = Form("Technical"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        session = InterviewSession(
            student_id=current_user.id,
            interview_type=interview_type,
            status="in_progress"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Generate first question using Gemini API
        q_data = generate_interview_question_ai(interview_type, [])
        qa = InterviewQA(
            session_id=session.id,
            question=q_data.get("question", f"Tell us about your background in {interview_type} engineering.")
        )
        db.add(qa)
        db.commit()
        db.refresh(qa)

        log = ActivityLog(user_id=current_user.id, action="start_mock_interview", details=f"Started {interview_type} mock interview session #{session.id}.")
        db.add(log)
        db.commit()

        return JSONResponse({
            "status": "success",
            "session_id": session.id,
            "qa_id": qa.id,
            "question": qa.question,
            "tips": q_data.get("tips", "Be clear and concise.")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer")
def submit_interview_answer(
    session_id: int = Form(...),
    qa_id: int = Form(...),
    answer: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.student_id == current_user.id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found.")

        qa = db.query(InterviewQA).filter(InterviewQA.id == qa_id, InterviewQA.session_id == session_id).first()
        if not qa:
            raise HTTPException(status_code=404, detail="Question entity not found.")

        qa.answer = answer
        eval_data = evaluate_interview_answer_ai(qa.question, answer)
        
        qa.score = float(eval_data.get("score", 75.0))
        qa.feedback = eval_data.get("feedback", "Good effort.")
        db.commit()

        # Check total answered questions in this session
        all_qas = db.query(InterviewQA).filter(InterviewQA.session_id == session_id).all()
        previous_qa_list = [{"question": item.question, "answer": item.answer or ""} for item in all_qas if item.answer]

        if len(previous_qa_list) >= 4:
            # End interview session
            session.status = "completed"
            avg_score = sum(q.score for q in all_qas) / len(all_qas)
            session.overall_score = round(avg_score, 1)
            session.feedback = f"Completed {session.interview_type} Interview with average score {session.overall_score}%."
            session.confidence_rating = eval_data.get("confidence_rating", "High")
            current_user.xp += 50
            current_user.coins += 20
            db.commit()

            return JSONResponse({
                "status": "completed",
                "overall_score": session.overall_score,
                "feedback": session.feedback,
                "confidence_rating": session.confidence_rating,
                "earned_xp": 50
            })
        else:
            # Generate next question
            next_q = generate_interview_question_ai(session.interview_type, previous_qa_list)
            next_qa = InterviewQA(
                session_id=session.id,
                question=next_q.get("question", "What is your process for debugging complex issues?")
            )
            db.add(next_qa)
            db.commit()
            db.refresh(next_qa)

            return JSONResponse({
                "status": "next",
                "previous_eval": {
                    "score": qa.score,
                    "feedback": qa.feedback
                },
                "next_qa_id": next_qa.id,
                "next_question": next_qa.question,
                "tips": next_q.get("tips", "")
            })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
