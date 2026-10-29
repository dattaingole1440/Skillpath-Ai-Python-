import os
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Career, Roadmap, Topic, StudentProgress, Certificate, ActivityLog
from app.certificate.service import generate_student_certificate
from app.utils.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/certificate", tags=["Certificate"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/generate/{career_id}")
def generate_certificate_route(
    career_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verifies that the user has completed all topics in the selected career pathway.
    If yes, triggers PDF certificate and QR generation.
    """
    # Verify career exists
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career path not found")

    # Get all topics in career path
    all_topics = db.query(Topic).join(Roadmap).filter(
        Roadmap.career_id == career_id
    ).all()
    
    if not all_topics:
        raise HTTPException(status_code=400, detail="This career pathway does not contain any topics yet.")

    # Get completed topics for user
    completed_progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id,
        StudentProgress.status == "Completed",
        StudentProgress.topic_id.in_([t.id for t in all_topics])
    ).all()

    # Allow generation ONLY if student completed all topics
    if len(completed_progress) < len(all_topics) and current_user.role != "admin":
        raise HTTPException(
            status_code=400,
            detail=f"Incomplete Pathway. You have completed {len(completed_progress)}/{len(all_topics)} topics. Finish all topics to unlock certification."
        )

    # Trigger generation
    try:
        cert = generate_student_certificate(db, current_user.id, career_id)
        
        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            action="generate_certificate",
            details=f"Generated certificate {cert.certificate_number} for career {career.name}."
        )
        db.add(log)
        db.commit()
        
        # Redirect to user profile certificates page or download it directly
        return RedirectResponse(url=f"/profile?certificate_unlocked=true", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate certificate: {str(e)}")


@router.get("/download/{cert_number}")
def download_certificate(cert_number: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Serves the certificate PDF file for download.
    """
    cert = db.query(Certificate).filter(Certificate.certificate_number == cert_number).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate record not found.")

    # Protect downloads - only the student who owns it, or admins, can download
    if cert.student_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized download access.")

    # Convert relative path to absolute
    file_path = cert.file_path.lstrip("/") # static/uploads/...
    abs_path = os.path.abspath(os.path.join("app", file_path))
    
    if os.path.exists(abs_path):
        return FileResponse(
            path=abs_path,
            filename=f"Certificate_{cert_number}.pdf",
            media_type="application/pdf"
        )
        
    raise HTTPException(status_code=404, detail="Certificate PDF file not found on disk.")


# Public route - QR code verification target
@router.get("/verify/{cert_number}", response_class=HTMLResponse)
@router.get("s/verify/{cert_number}", response_class=HTMLResponse)
def verify_certificate_page(request: Request, cert_number: str, db: Session = Depends(get_db)):
    """
    Publicly accessible endpoint that verifies the authenticity of a certificate.
    Displays credentials to visitors (e.g. employers).
    """
    cert = db.query(Certificate).filter(Certificate.certificate_number == cert_number).first()
    
    # We pass verification details to public HTML template
    is_valid = cert is not None
    student_name = cert.student.name if is_valid else None
    career_name = cert.career.name if is_valid else None
    issue_date = cert.issue_date.strftime("%B %d, %Y") if is_valid else None
    
    return templates.TemplateResponse(
        "certificate/verify.html",
        {
            "request": request,
            "is_valid": is_valid,
            "cert_number": cert_number,
            "student_name": student_name,
            "career_name": career_name,
            "issue_date": issue_date
        }
    )

