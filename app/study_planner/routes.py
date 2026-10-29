import datetime
from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, StudyPlan, StudyTask, Career, ActivityLog
from app.utils.auth import get_current_user
from app.ai.service import generate_study_plan_ai

router = APIRouter(prefix="/study-planner", tags=["Study Planner"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_study_planner_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(StudyPlan).filter(StudyPlan.student_id == current_user.id).order_by(StudyPlan.created_at.desc()).first()
    tasks = []
    if plan:
        tasks = db.query(StudyTask).filter(StudyTask.plan_id == plan.id).order_by(StudyTask.scheduled_date).all()
        
    return templates.TemplateResponse(
        "study_planner/index.html",
        {
            "request": request,
            "user": current_user,
            "plan": plan,
            "tasks": tasks
        }
    )

@router.post("/generate")
def generate_study_plan(
    hours_per_day: float = Form(...),
    target_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        career_title = "Full Stack Development"
        if current_user.current_career:
            career_title = current_user.current_career.name

        ai_res = generate_study_plan_ai(hours_per_day, target_date, career_title)
        
        target_d = None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                target_d = datetime.datetime.strptime(target_date.strip(), fmt).date()
                break
            except Exception:
                pass
        if not target_d:
            target_d = datetime.date.today() + datetime.timedelta(days=30)
        
        # Save Plan to DB
        plan = StudyPlan(
            student_id=current_user.id,
            hours_per_day=hours_per_day,
            target_date=target_d,
            plan_summary=ai_res.get("plan_summary", "Custom AI Study Plan")
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        # Save Tasks to DB
        today = datetime.date.today()
        task_objs = []
        for idx, t in enumerate(ai_res.get("tasks", [])):
            try:
                offset = int(t.get("days_from_start", idx))
            except Exception:
                offset = idx
            sched_date = today + datetime.timedelta(days=offset)
            task_obj = StudyTask(
                plan_id=plan.id,
                student_id=current_user.id,
                title=t.get("title", f"Study Session {idx+1}"),
                description=t.get("description", "Review concepts and practice questions."),
                scheduled_date=sched_date,
                hours_estimated=float(t.get("hours_estimated", hours_per_day))
            )
            task_objs.append(task_obj)
            db.add(task_obj)

        db.commit()

        log = ActivityLog(user_id=current_user.id, action="create_study_plan", details=f"Generated study plan targeting {target_date}.")
        db.add(log)
        db.commit()

        return JSONResponse({"status": "success", "plan_id": plan.id, "message": "Study plan created successfully!"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/complete")
def complete_study_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(StudyTask).filter(StudyTask.id == task_id, StudyTask.student_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    task.completed_at = datetime.datetime.utcnow()
    current_user.xp += 20
    current_user.coins += 5
    db.commit()

    return JSONResponse({"status": "success", "message": "Task completed! Earned +20 XP & +5 Coins!"})
