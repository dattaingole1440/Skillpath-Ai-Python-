import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import (
    User, College, Department, Semester, Division, Subject, Assignment,
    AssignmentSubmission, EarlyWarningAlert, Video
)
from app.utils.auth import get_current_user
from app.utils.permissions import require_principal, require_hod, require_super_admin, require_roles
from app.utils.security import get_password_hash

router = APIRouter(tags=["College & Department Management"])
templates = Jinja2Templates(directory="app/templates")


# =======================================================
# SUPER ADMIN COLLEGE MANAGEMENT
# =======================================================
@router.get("/college/manage", response_class=HTMLResponse)
def manage_colleges_view(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["super_admin", "admin"]))
):
    colleges = db.query(College).all()
    departments = db.query(Department).all()
    principals = db.query(User).filter(User.role.in_(["principal", "college_admin"])).all()
    teachers = db.query(User).filter(User.role == "teacher").all()
    hods = db.query(User).filter(User.role == "hod").all()
    students = db.query(User).filter(User.role == "student").all()
    
    return templates.TemplateResponse("college/manage.html", {
        "request": request,
        "user": current_user,
        "colleges": colleges,
        "departments": departments,
        "principals": principals,
        "teachers": teachers,
        "hods": hods,
        "students": students
    })


@router.post("/college/create")
def create_college(
    name: str = Form(...),
    code: str = Form(...),
    contact_email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    code_clean = code.strip().upper()
    existing = db.query(College).filter(College.code == code_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="College code already exists.")
    
    college = College(name=name.strip(), code=code_clean, contact_email=contact_email, address=address)
    db.add(college)
    db.commit()
    return RedirectResponse(url="/college/manage?success=college_created", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/college/department/create")
def create_department(
    college_id: int = Form(...),
    name: str = Form(...),
    code: str = Form(...),
    hod_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["super_admin", "admin", "principal", "college_admin"]))
):
    parsed_hod_id = int(hod_id) if hod_id and hod_id.strip().isdigit() else None
    
    dept = Department(college_id=college_id, name=name.strip(), code=code.strip().upper(), hod_id=parsed_hod_id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    
    # If HOD user assigned, update their department_id
    if parsed_hod_id:
        hod_user = db.query(User).filter(User.id == parsed_hod_id).first()
        if hod_user:
            hod_user.department_id = dept.id
            hod_user.role = "hod"
            db.commit()

    # Create 8 Semesters by default
    for i in range(1, 9):
        sem = Semester(department_id=dept.id, number=i, name=f"Semester {i}")
        db.add(sem)
        db.commit()
        db.refresh(sem)
        db.add(Division(semester_id=sem.id, name="Division A"))
        db.add(Division(semester_id=sem.id, name="Division B"))
        db.commit()

    redirect_url = "/principal/dashboard" if current_user.role in ["principal", "college_admin"] else "/college/manage"
    return RedirectResponse(url=redirect_url + "?success=dept_created", status_code=status.HTTP_303_SEE_OTHER)


# =======================================================
# PRINCIPAL PANEL ROUTING & VIEWS
# =======================================================
@router.get("/principal", response_class=HTMLResponse)
@router.get("/principal/dashboard", response_class=HTMLResponse)
def principal_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_principal)
):
    """
    Principal Panel: Complete overview of all data in the principal's college.
    """
    college = current_user.college
    if not college:
        college = db.query(College).first()

    college_id = college.id if college else None

    # Fetch stats specific to this college
    departments = db.query(Department).filter(Department.college_id == college_id).all() if college_id else []
    dept_ids = [d.id for d in departments]

    teachers = db.query(User).filter(User.college_id == college_id, User.role == "teacher").all() if college_id else []
    hods = db.query(User).filter(User.college_id == college_id, User.role == "hod").all() if college_id else []
    students = db.query(User).filter(User.college_id == college_id, User.role == "student").all() if college_id else []
    
    subjects = db.query(Subject).filter(Subject.department_id.in_(dept_ids)).all() if dept_ids else []
    assignments = db.query(Assignment).filter(Assignment.subject_id.in_([s.id for s in subjects])).all() if subjects else []

    early_warnings = db.query(EarlyWarningAlert).join(User, EarlyWarningAlert.student_id == User.id).filter(User.college_id == college_id).all() if college_id else []

    # Calculate average scores across college students
    avg_quiz = round(sum(s.quiz_avg for s in students) / len(students), 1) if students else 0.0
    avg_coding = round(sum(s.coding_avg for s in students) / len(students), 1) if students else 0.0

    return templates.TemplateResponse("principal/dashboard.html", {
        "request": request,
        "user": current_user,
        "college": college,
        "departments": departments,
        "teachers": teachers,
        "hods": hods,
        "students": students,
        "subjects": subjects,
        "assignments": assignments,
        "early_warnings": early_warnings,
        "avg_quiz": avg_quiz,
        "avg_coding": avg_coding,
        "active_tab": request.query_params.get("tab", "depts")
    })


@router.get("/principal/departments", response_class=HTMLResponse)
def principal_departments_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_principal)):
    response = principal_dashboard(request, db, current_user)
    response.context["active_tab"] = "depts"
    return response


@router.get("/principal/faculty", response_class=HTMLResponse)
def principal_faculty_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_principal)):
    response = principal_dashboard(request, db, current_user)
    response.context["active_tab"] = "faculty"
    return response


@router.get("/principal/students", response_class=HTMLResponse)
def principal_students_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_principal)):
    response = principal_dashboard(request, db, current_user)
    response.context["active_tab"] = "students"
    return response


@router.get("/principal/subjects", response_class=HTMLResponse)
def principal_subjects_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_principal)):
    response = principal_dashboard(request, db, current_user)
    response.context["active_tab"] = "subjects"
    return response


@router.post("/principal/assign-hod")
def principal_assign_hod(
    department_id: int = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_principal)
):
    dept = db.query(Department).filter(Department.id == department_id).first()
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if dept and target_user:
        dept.hod_id = target_user.id
        target_user.role = "hod"
        target_user.department_id = dept.id
        if dept.college_id:
            target_user.college_id = dept.college_id
        db.commit()

    return RedirectResponse(url="/principal/dashboard?success=hod_assigned", status_code=status.HTTP_303_SEE_OTHER)


# =======================================================
# HOD PANEL ROUTING & VIEWS
# =======================================================
@router.get("/hod", response_class=HTMLResponse)
@router.get("/hod/dashboard", response_class=HTMLResponse)
def hod_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    """
    HOD Panel: Complete management hub for Head of Department.
    """
    dept = current_user.department
    if not dept:
        dept = db.query(Department).first()

    dept_id = dept.id if dept else None

    # Fetch Department Stats
    dept_teachers = db.query(User).filter(User.department_id == dept_id, User.role == "teacher").all() if dept_id else []
    dept_students = db.query(User).filter(User.department_id == dept_id, User.role == "student").all() if dept_id else []
    dept_subjects = db.query(Subject).filter(Subject.department_id == dept_id).all() if dept_id else []
    
    subject_ids = [s.id for s in dept_subjects]
    dept_assignments = db.query(Assignment).filter(Assignment.subject_id.in_(subject_ids)).all() if subject_ids else []
    
    warnings = db.query(EarlyWarningAlert).join(User, EarlyWarningAlert.student_id == User.id).filter(User.department_id == dept_id).all() if dept_id else []
    videos = db.query(Video).filter(Video.is_deleted == False).all()

    avg_quiz = round(sum(s.quiz_avg for s in dept_students) / len(dept_students), 1) if dept_students else 0.0
    avg_coding = round(sum(s.coding_avg for s in dept_students) / len(dept_students), 1) if dept_students else 0.0

    return templates.TemplateResponse("hod/dashboard.html", {
        "request": request,
        "user": current_user,
        "department": dept,
        "teachers": dept_teachers,
        "students": dept_students,
        "subjects": dept_subjects,
        "assignments": dept_assignments,
        "warnings": warnings,
        "videos": videos,
        "avg_quiz": avg_quiz,
        "avg_coding": avg_coding,
        "active_tab": request.query_params.get("tab", "subjects")
    })


@router.get("/hod/subjects", response_class=HTMLResponse)
def hod_subjects_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_hod)):
    response = hod_dashboard(request, db, current_user)
    response.context["active_tab"] = "subjects"
    return response


@router.get("/hod/faculty", response_class=HTMLResponse)
def hod_faculty_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_hod)):
    response = hod_dashboard(request, db, current_user)
    response.context["active_tab"] = "faculty"
    return response


@router.get("/hod/students", response_class=HTMLResponse)
def hod_students_view(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_hod)):
    response = hod_dashboard(request, db, current_user)
    response.context["active_tab"] = "students"
    return response



@router.post("/hod/subject/create")
def hod_create_subject(
    name: str = Form(...),
    code: str = Form(...),
    semester_number: int = Form(1),
    teacher_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    dept = current_user.department or db.query(Department).first()
    if not dept:
        raise HTTPException(status_code=400, detail="Department context missing")
        
    sem = db.query(Semester).filter(Semester.department_id == dept.id, Semester.number == semester_number).first()
    if not sem:
        sem = Semester(department_id=dept.id, number=semester_number, name=f"Semester {semester_number}")
        db.add(sem)
        db.commit()
        db.refresh(sem)

    parsed_teacher_id = int(teacher_id) if teacher_id and teacher_id.strip().isdigit() else None
    
    subj = Subject(
        department_id=dept.id,
        semester_id=sem.id,
        name=name.strip(),
        code=code.strip().upper(),
        teacher_id=parsed_teacher_id
    )
    db.add(subj)
    db.commit()

    return RedirectResponse(url="/hod/dashboard?success=subject_created", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/hod/subject/assign")
def hod_assign_teacher(
    subject_id: int = Form(...),
    teacher_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    subj = db.query(Subject).filter(Subject.id == subject_id).first()
    if subj:
        subj.teacher_id = teacher_id
        db.commit()
    return RedirectResponse(url="/hod/dashboard?success=teacher_assigned", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/college/students/import")
async def import_students_csv(
    college_id: int = Form(...),
    department_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["super_admin", "admin", "principal", "hod", "college_admin"]))
):
    """Imports students from CSV file. Columns: name, email, roll_number, phone_number"""
    content = await file.read()
    decoded = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    count = 0
    default_password = get_password_hash("Student@123")
    
    for row in csv_reader:
        email = row.get("email", "").strip().lower()
        name = row.get("name", "").strip()
        roll_number = row.get("roll_number", "").strip()
        phone_number = row.get("phone_number", "").strip()
        
        if email and name:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                student = User(
                    name=name,
                    email=email,
                    password_hash=default_password,
                    role="student",
                    college_id=college_id,
                    department_id=department_id,
                    roll_number=roll_number,
                    phone_number=phone_number
                )
                db.add(student)
                count += 1
    db.commit()
    
    redirect_target = "/hod/dashboard" if current_user.role == "hod" else "/principal/dashboard" if current_user.role == "principal" else "/college/manage"
    return RedirectResponse(url=f"{redirect_target}?imported={count}", status_code=status.HTTP_303_SEE_OTHER)
