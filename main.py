import os
import shutil
from fastapi import FastAPI, Depends, Request, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.connection import engine, Base, get_db, SessionLocal, sync_db_schema
from app.models.models import User, Career, Roadmap, Topic, StudentProgress, Certificate, ActivityLog, QuizAttempt, CodingSubmission
from app.database.seed import seed_database
from app.utils.auth import get_current_user, get_current_user_optional

# Import all module routers
from app.auth.routes import router as auth_router
from app.dashboard.routes import router as dashboard_router
from app.roadmap.routes import router as roadmap_router
from app.quiz.routes import router as quiz_router
from app.coding.routes import router as coding_router
from app.analytics.routes import router as analytics_router
from app.recommendation.routes import router as recommendation_router
from app.certificate.routes import router as certificate_router
from app.admin.routes import router as admin_router
from app.ai.routes import router as ai_chat_router

# Additional Enterprise Module Routers
from app.study_planner.routes import router as study_planner_router
from app.code_reviewer.routes import router as code_reviewer_router
from app.code_editor.routes import router as code_editor_router
from app.resume.routes import router as resume_router
from app.interview.routes import router as interview_router
from app.gamification.routes import router as gamification_router
from app.projects.routes import router as projects_router
from app.forum.routes import router as forum_router
from app.study_groups.routes import router as study_groups_router
from app.notes.routes import router as notes_router
from app.resource_library.routes import router as resource_library_router
from app.search.routes import router as search_router
from app.notifications.routes import router as notifications_router
from app.portfolio.routes import router as portfolio_router
from app.pwa.routes import router as pwa_router
from app.college.routes import router as college_router
from app.teacher.routes import router as teacher_router
from app.student.routes import router as student_router
from app.reports.routes import router as reports_router
from app.roadmap.api_routes import router as core_api_router

# Create all database tables on startup (non-destructive)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillPath AI", description="AI Powered Adaptive Learning Roadmap Platform", version="1.0.0")

@app.on_event("startup")
def on_startup():
    print("=" * 68)
    print("  🚀 [STARTUP] SkillPath AI Initializing...")
    # 1. Synchronize schema columns safely (non-destructive ALTER TABLE ADD COLUMN)
    try:
        sync_db_schema(engine, Base)
        print("  ✅ [MIGRATION] Current schema verified & synchronized")
    except Exception as e:
        print(f"  ⚠️  [MIGRATION WARNING] Schema sync issue: {e}")
    
    # 2. Seed database ONLY if genuinely empty (preserves all existing data permanently)
    db = SessionLocal()
    try:
        seed_database(db)
        
        # 3. Non-destructive Role & Account Synchronization (College Admin -> Principal)
        from app.models.models import College, Department
        from app.utils.security import get_password_hash
        
        legacy_admins = db.query(User).filter(User.role.in_(["college_admin", "clg_admin"])).all()
        for u in legacy_admins:
            u.role = "principal"
            if u.email == "collegeadmin@skillpath.ai":
                u.email = "principal@skillpath.ai"
                u.name = "Dr. Robert Vance (Principal)"
        
        principal_user = db.query(User).filter(User.email == "principal@skillpath.ai").first()
        if not principal_user:
            clg = db.query(College).first()
            principal_user = User(
                name="Dr. Robert Vance (Principal)",
                email="principal@skillpath.ai",
                password_hash=get_password_hash("Principal@123"),
                role="principal",
                college_id=clg.id if clg else None,
                employee_id="PRIN-1001"
            )
            db.add(principal_user)

        hod_user = db.query(User).filter(User.email == "hod@skillpath.ai").first()
        if not hod_user:
            dept = db.query(Department).first()
            hod_user = User(
                name="Dr. HOD Computer Science",
                email="hod@skillpath.ai",
                password_hash=get_password_hash("Hod@123"),
                role="hod",
                college_id=dept.college_id if dept else None,
                department_id=dept.id if dept else None,
                employee_id="HOD-1001"
            )
            db.add(hod_user)
        elif hod_user.role != "hod":
            hod_user.role = "hod"

        db.commit()
        print("  ✅ [ROLE MIGRATION] User roles synced: College Admin replaced with Principal & HOD")
    except Exception as e:
        print(f"  ⚠️  [DATABASE WARNING] Migration check issue: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("  ✅ [STARTUP] No destructive initialization performed - All data intact")
    print("  ⭐ [SERVER] SkillPath AI started successfully")
    print("=" * 68)


# Cache-Control Middleware: Prevents browser/proxy from serving stale cached state
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api") or path.startswith("/admin") or path.startswith("/roadmap") or path.startswith("/dashboard"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler to catch 401 unauthorized errors and redirect to Login Page
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    is_api = request.url.path.startswith("/api")
    if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        if not is_api and not request.url.path.startswith("/auth"):
            resp = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
            resp.delete_cookie("access_token")
            return resp
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Create folders for uploads if they do not exist
os.makedirs("app/static/uploads/avatars", exist_ok=True)
os.makedirs("app/static/uploads/certificates", exist_ok=True)
os.makedirs("app/static/uploads/qrcodes", exist_ok=True)
os.makedirs("app/static/uploads/videos", exist_ok=True)

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Register Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(roadmap_router)
app.include_router(quiz_router)
app.include_router(coding_router)
app.include_router(analytics_router)
app.include_router(recommendation_router)
app.include_router(certificate_router)
app.include_router(admin_router)
app.include_router(ai_chat_router)
app.include_router(study_planner_router)
app.include_router(code_reviewer_router)
app.include_router(code_editor_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(gamification_router)
app.include_router(projects_router)
app.include_router(forum_router)
app.include_router(study_groups_router)
app.include_router(notes_router)
app.include_router(resource_library_router)
app.include_router(search_router)
app.include_router(notifications_router)
app.include_router(portfolio_router)
app.include_router(pwa_router)
app.include_router(college_router)
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(reports_router)
app.include_router(core_api_router)



@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request, current_user = Depends(get_current_user_optional)):
    """
    Renders the modern SkillPath AI Landing Page.
    """
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})


@app.get("/profile", response_class=HTMLResponse)
def user_profile(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Renders the Student Profile and Credentials manager.
    Computes streaks, scores, and achievement badges.
    """
    # Fetch student certificates
    certificates = db.query(Certificate).filter(Certificate.student_id == current_user.id).all()
    
    # Calculate Achievements based on milestones
    achievements = []
    if current_user.daily_streak >= 3:
        achievements.append({
            "title": "Consistent Learner",
            "desc": "Maintained a 3+ day streak.",
            "icon": "bi-lightning-fill",
            "color": "text-warning"
        })
    if current_user.quiz_avg >= 85:
        achievements.append({
            "title": "Quiz Master",
            "desc": "Averaged over 85% in Quizzes.",
            "icon": "bi-trophy-fill",
            "color": "text-danger"
        })
    if current_user.coding_avg >= 80:
        achievements.append({
            "title": "Code Warrior",
            "desc": "Averaged over 80% in Coding Challenges.",
            "icon": "bi-code-slash",
            "color": "text-primary"
        })
    if len(certificates) > 0:
        achievements.append({
            "title": "Certified Professional",
            "desc": "Successfully completed a learning pathway.",
            "icon": "bi-patch-check-fill",
            "color": "text-success"
        })
        
    return templates.TemplateResponse(
        "profile/view_profile.html",
        {
            "request": request,
            "user": current_user,
            "certificates": certificates,
            "achievements": achievements
        }
    )


@app.post("/profile/photo")
async def update_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the profile photo for the active user.
    """
    # Ensure folder exists
    os.makedirs("app/static/uploads/avatars", exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"user_{current_user.id}{file_ext}"
    file_path = os.path.join("app/static/uploads/avatars", filename)
    
    # Copy file to destination
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Update db record
    current_user.profile_photo = f"/static/uploads/avatars/{filename}"
    db.commit()
    
    # Log Action
    log = ActivityLog(user_id=current_user.id, action="update_profile_photo", details="Updated profile picture.")
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
