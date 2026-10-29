from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, AttendanceRecord, QuizAttempt, CodingSubmission, AssignmentSubmission, PlacementRecord, Department, Subject, College
from app.utils.auth import get_current_user
from app.utils.permissions import require_teacher
from app.reports.service import generate_pdf_report, generate_csv_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/", response_class=HTMLResponse)
def view_reports_hub(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Renders the Reports Dashboard with options to download PDF and CSV reports."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse("reports/index.html", {"request": request, "user": current_user})


@router.get("/students/pdf")
def download_student_report_pdf(db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    students = db.query(User).filter(User.role == "student").all()
    headers = ["ID", "Name", "Email", "Roll No", "Department", "Learning Hours", "Quiz Avg", "Coding Avg"]
    data = []
    for s in students:
        dept = s.department.name if s.department else "N/A"
        data.append([s.id, s.name, s.email, s.roll_number or "N/A", dept, f"{s.learning_hours:.1f}", f"{s.quiz_avg:.1f}%", f"{s.coding_avg:.1f}%"])
    
    pdf_bytes = generate_pdf_report("Student Performance Report", "Comprehensive academic metrics summary", headers, data)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=student_report.pdf"})


@router.get("/students/excel")
def download_student_report_excel(db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    students = db.query(User).filter(User.role == "student").all()
    headers = ["ID", "Name", "Email", "Roll No", "Department", "Learning Hours", "Quiz Avg", "Coding Avg"]
    data = []
    for s in students:
        dept = s.department.name if s.department else "N/A"
        data.append([s.id, s.name, s.email, s.roll_number or "N/A", dept, f"{s.learning_hours:.1f}", f"{s.quiz_avg:.1f}%", f"{s.coding_avg:.1f}%"])
    
    csv_str = generate_csv_report(headers, data)
    return Response(content=csv_str, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=student_report.csv"})


@router.get("/attendance/pdf")
def download_attendance_report_pdf(db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    records = db.query(AttendanceRecord).order_by(AttendanceRecord.date.desc()).limit(200).all()
    headers = ["Student", "Subject", "Date", "Status", "Study Minutes", "Override"]
    data = []
    for r in records:
        student_name = r.student.name if r.student else "N/A"
        subject_name = r.subject.name if r.subject else "General Learning"
        data.append([student_name, subject_name, str(r.date), r.status, f"{r.study_minutes} mins", "Yes" if r.is_manual_override else "No"])
    
    pdf_bytes = generate_pdf_report("Attendance Activity Report", "Automated and manual attendance logs", headers, data)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=attendance_report.pdf"})


@router.get("/placement/pdf")
def download_placement_report_pdf(db: Session = Depends(get_db), current_user: User = Depends(require_teacher)):
    records = db.query(PlacementRecord).all()
    headers = ["Student", "Composite Score", "Coding", "Quiz", "Projects", "Attendance", "Resume", "Interview"]
    data = []
    for p in records:
        s_name = p.student.name if p.student else "N/A"
        data.append([s_name, f"{p.placement_score:.1f}%", f"{p.coding_score:.1f}%", f"{p.quiz_score:.1f}%", f"{p.projects_score:.1f}%", f"{p.attendance_score:.1f}%", f"{p.resume_score:.1f}%", f"{p.interview_score:.1f}%"])
    
    pdf_bytes = generate_pdf_report("Placement Readiness Report", "Composite placement readiness evaluation", headers, data)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=placement_report.pdf"})
