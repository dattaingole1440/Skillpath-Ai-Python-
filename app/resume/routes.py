import json
import os
from fastapi import APIRouter, Depends, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Resume, ResumeAnalysis, ActivityLog
from app.utils.auth import get_current_user
from app.ai.service import build_resume_ai, analyze_resume_ai

router = APIRouter(prefix="/resume", tags=["AI Resume"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/builder", response_class=HTMLResponse)
def get_resume_builder_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.student_id == current_user.id).order_by(Resume.updated_at.desc()).first()
    return templates.TemplateResponse(
        "resume/builder.html",
        {
            "request": request,
            "user": current_user,
            "resume": resume
        }
    )

@router.get("/analyzer", response_class=HTMLResponse)
def get_resume_analyzer_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analyses = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == current_user.id).order_by(ResumeAnalysis.created_at.desc()).limit(5).all()
    return templates.TemplateResponse(
        "resume/analyzer.html",
        {
            "request": request,
            "user": current_user,
            "analyses": analyses
        }
    )

@router.post("/generate")
def generate_resume(
    personal_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    skills_csv: str = Form(...),
    projects_text: str = Form(""),
    certificates_text: str = Form(""),
    achievements_text: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        personal_info = {
            "name": personal_name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github
        }
        skills = [s.strip() for s in skills_csv.split(",") if s.strip()]
        projects = [p.strip() for p in projects_text.split("\n") if p.strip()]
        certificates = [c.strip() for c in certificates_text.split("\n") if c.strip()]
        achievements = [a.strip() for a in achievements_text.split("\n") if a.strip()]

        res_data = build_resume_ai(personal_info, skills, projects, certificates, achievements)

        resume = Resume(
            student_id=current_user.id,
            title=f"ATS Resume - {personal_name}",
            personal_info=json.dumps(personal_info),
            skills=json.dumps(skills),
            projects=json.dumps(projects),
            certificates=json.dumps(certificates),
            achievements=json.dumps(achievements),
            generated_ats_resume=res_data.get("formatted_resume", "")
        )
        db.add(resume)
        current_user.xp += 30
        db.commit()
        db.refresh(resume)

        log = ActivityLog(user_id=current_user.id, action="generate_resume", details="Generated ATS-friendly resume.")
        db.add(log)
        db.commit()

        return JSONResponse({
            "status": "success",
            "resume_id": resume.id,
            "resume_text": resume.generated_ats_resume,
            "resume_data": res_data
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_resume_file(
    resume_file: UploadFile = File(None),
    resume_text_input: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        text_to_analyze = resume_text_input.strip()

        if resume_file and resume_file.filename:
            content_bytes = await resume_file.read()
            # If plain text file or extracted text:
            try:
                text_to_analyze += "\n" + content_bytes.decode("utf-8", errors="ignore")
            except Exception:
                pass

        if not text_to_analyze:
            text_to_analyze = f"Resume of {current_user.name}. Email: {current_user.email}. Skills: Python, Java, SQL, FastAPI, HTML, CSS, JavaScript."

        analysis = analyze_resume_ai(text_to_analyze)

        analysis_rec = ResumeAnalysis(
            student_id=current_user.id,
            filename=resume_file.filename if (resume_file and resume_file.filename) else "Text Resume",
            ats_score=analysis.get("ats_score", 75),
            missing_skills=json.dumps(analysis.get("missing_skills", [])),
            improvement_suggestions=analysis.get("improvement_suggestions", ""),
            rating=analysis.get("rating", "Good"),
            recommended_skills=json.dumps(analysis.get("recommended_skills", [])),
            raw_analysis=analysis.get("raw_analysis", "")
        )
        db.add(analysis_rec)
        current_user.xp += 25
        db.commit()
        db.refresh(analysis_rec)

        log = ActivityLog(user_id=current_user.id, action="analyze_resume", details=f"Analyzed resume with ATS score {analysis_rec.ats_score}%.")
        db.add(log)
        db.commit()

        return JSONResponse({
            "status": "success",
            "ats_score": analysis_rec.ats_score,
            "rating": analysis_rec.rating,
            "missing_skills": json.loads(analysis_rec.missing_skills),
            "recommended_skills": json.loads(analysis_rec.recommended_skills),
            "suggestions": analysis_rec.improvement_suggestions,
            "raw_analysis": analysis_rec.raw_analysis
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
