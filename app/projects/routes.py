from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Project, UserProjectSubmission, ActivityLog
from app.utils.auth import get_current_user
from app.ai.service import recommend_projects_ai

router = APIRouter(prefix="/projects", tags=["Project Recommendation"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_projects_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = db.query(Project).all()

    # Seed default projects if table is empty
    if not projects:
        default_p = [
            Project(title="Calculator App", description="Command line & GUI calculator performing arithmetic operations and math functions.", level="Beginner", category="Python/Logic", tech_stack="Python 3.11, Tkinter", github_template="https://github.com/microsoft/calculator"),
            Project(title="BMI & Fitness Calculator", description="Health metric application calculating BMI, calorie requirements, and macros.", level="Beginner", category="Utility", tech_stack="JavaScript ES6, Bootstrap 5", github_template="https://github.com/StartBootstrap/startbootstrap-resume"),
            Project(title="Real-Time Weather App", description="Fetches real-time weather forecasts, humidity, and wind speeds via OpenWeather REST API.", level="Beginner", category="Web API", tech_stack="JavaScript, Fetch API, HTML5", github_template="https://github.com/public-apis/public-apis"),
            Project(title="TodoMVC Task Manager", description="Interactive task manager app supporting add, edit, filter, local storage, and completion stats.", level="Beginner", category="Web App", tech_stack="HTML5, Vanilla CSS, JS", github_template="https://github.com/tastejs/todomvc"),
            Project(title="FastAPI Student Management System", description="Production-grade CRUD REST microservice managing student enrollment, topics, and grade records.", level="Intermediate", category="Full Stack", tech_stack="Python, FastAPI, SQLAlchemy, SQLite", github_template="https://github.com/tiangolo/full-stack-fastapi-template"),
            Project(title="Expense Analytics Tracker", description="Financial application categorizing income vs expenses with interactive Chart.js graphs.", level="Intermediate", category="Analytics", tech_stack="FastAPI, Chart.js, Bootstrap", github_template="https://github.com/highcharts/highcharts"),
            Project(title="Java Online Quiz & Assessment System", description="Multi-tenant test system evaluating student MCQ answers and outputting performance analytics.", level="Intermediate", category="EdTech", tech_stack="Java 17, Spring Boot, MySQL", github_template="https://github.com/eugenp/tutorials"),
            Project(title="Personal Developer Portfolio", description="Modern responsive developer portfolio displaying achievements, verified certificates, and GitHub stats.", level="Intermediate", category="Frontend", tech_stack="Bootstrap 5, Inter Font, JS", github_template="https://github.com/anuraghazra/github-readme-stats"),
            Project(title="Real-Time WebSocket Chat Room", description="WebSocket-enabled chat platform supporting active presence, room creation, and instant messaging.", level="Advanced", category="Full Stack", tech_stack="Node.js, Express, Socket.io", github_template="https://github.com/socketio/socket.io-chat-example"),
            Project(title="Spring Boot PetClinic & Hospital System", description="Enterprise healthcare management system for patient appointments, prescriptions, and billing.", level="Advanced", category="Enterprise Java", tech_stack="Java Spring Boot, Hibernate, MySQL", github_template="https://github.com/spring-projects/spring-petclinic"),
            Project(title="Full-Stack E-Commerce SaaS", description="Modern online store with product search, cart state management, and Stripe checkout integration.", level="Advanced", category="E-Commerce", tech_stack="Next.js, TypeScript, Stripe, PostgreSQL", github_template="https://github.com/nextjs/saas-starter"),
            Project(title="Hazel High-Performance C++ Engine", description="Low-level 2D/3D graphics and game engine sandbox supporting custom memory allocators and OpenGL.", level="Advanced", category="C++ Systems", tech_stack="C++ 20, CMake, OpenGL, GLFW", github_template="https://github.com/TheCherno/Hazel"),
            Project(title="Gemini AI Multimodal Copilot Platform", description="AI powered learning roadmap platform featuring real-time code analysis, resume review, and doubt solving.", level="Advanced", category="AI Platform", tech_stack="Python, FastAPI, Gemini AI, SQLite", github_template="https://github.com/google/generative-ai-python")
        ]
        db.add_all(default_p)
        db.commit()
        projects = db.query(Project).all()

    user_submissions = db.query(UserProjectSubmission).filter(UserProjectSubmission.student_id == current_user.id).all()
    submitted_project_ids = [s.project_id for s in user_submissions]

    return templates.TemplateResponse(
        "projects/index.html",
        {
            "request": request,
            "user": current_user,
            "projects": projects,
            "submitted_project_ids": submitted_project_ids
        }
    )

@router.post("/recommend-ai")
def get_ai_project_recommendations(
    level: str = Form("Intermediate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        career_name = current_user.current_career.name if current_user.current_career else "Software Engineering"
        recs = recommend_projects_ai(career_name, level)
        return JSONResponse({"status": "success", "recommendations": recs.get("projects", [])})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
