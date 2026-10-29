import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, ActivityLog
from app.schemas import schemas
from app.utils.security import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    token = request.cookies.get("access_token")
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
    # If token missing or invalid, render login page
    response = templates.TemplateResponse("auth/login.html", {"request": request})
    if token:
        response.delete_cookie("access_token")
    return response


@router.post("/login")
def login_api(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        if "application/json" in request.headers.get("accept", ""):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=400, content={"detail": "Invalid email or password", "success": False})
        return RedirectResponse(url="/auth/login?error=invalid_credentials", status_code=status.HTTP_302_FOUND)
    
    # Create Access Token
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    # Log Activity
    log = ActivityLog(user_id=user.id, action="login", details=f"User {user.email} logged in successfully.")
    db.add(log)
    db.commit()

    # Determine destination based on role
    if user.role in ["super_admin", "admin"]:
        dest = "/admin"
    elif user.role in ["principal", "college_admin"]:
        dest = "/principal/dashboard"
    elif user.role == "hod":
        dest = "/hod/dashboard"
    elif user.role == "teacher":
        dest = "/teacher/dashboard"
    else:
        dest = "/dashboard"

    if "application/json" in request.headers.get("accept", ""):
        from fastapi.responses import JSONResponse
        res = JSONResponse(content={"success": True, "redirect": dest, "user": {"id": user.id, "name": user.name, "role": user.role, "email": user.email}})
        res.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=7200,
            expires=7200,
            samesite="lax",
            secure=False
        )
        return res

    # Set JWT in Cookie for standard form POST
    redirect_resp = RedirectResponse(url=dest, status_code=status.HTTP_302_FOUND)
    redirect_resp.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=7200,
        expires=7200,
        samesite="lax",
        secure=False
    )
    return redirect_resp


@router.get("/demo-login")
def demo_login(role: str = "student", db: Session = Depends(get_db)):
    """
    1-Click Fast Login for quick exploration as Student, Teacher, HOD, Principal, or Super Admin.
    """
    role_email_map = {
        "student": "student@skillpath.ai",
        "teacher": "teacher@skillpath.ai",
        "hod": "hod@skillpath.ai",
        "principal": "principal@skillpath.ai",
        "super_admin": "superadmin@skillpath.ai",
        "admin": "superadmin@skillpath.ai",
        "college_admin": "principal@skillpath.ai"
    }
    target_email = role_email_map.get(role, "student@skillpath.ai")
    user = db.query(User).filter(User.email == target_email).first()
    if not user:
        user = db.query(User).filter(User.role == role).first()
    if not user:
        user = db.query(User).first()
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    if user.role in ["super_admin", "admin"]:
        dest = "/admin"
    elif user.role in ["principal", "college_admin"]:
        dest = "/principal/dashboard"
    elif user.role == "hod":
        dest = "/hod/dashboard"
    elif user.role == "teacher":
        dest = "/teacher/dashboard"
    else:
        dest = "/dashboard"


    response = RedirectResponse(url=dest, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=7200,
        expires=7200,
        samesite="lax",
        secure=False
    )
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    from app.models.models import College, Department
    colleges = db.query(College).all()
    departments = db.query(Department).all()
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "colleges": colleges,
        "departments": departments
    })


@router.post("/register")
def register_api(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("student"),
    phone_number: Optional[str] = Form(None),
    roll_number: Optional[str] = Form(None),
    employee_id: Optional[str] = Form(None),
    college_id: Optional[int] = Form(None),
    department_id: Optional[int] = Form(None),
    custom_college: Optional[str] = Form(None),
    adm_college_name: Optional[str] = Form(None),
    adm_college_website: Optional[str] = Form(None),
    adm_college_location: Optional[str] = Form(None),
    adm_college_image: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        if "application/json" in request.headers.get("accept", ""):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=400, content={"detail": "Email already registered", "success": False})
        return RedirectResponse(url="/auth/register?error=email_exists", status_code=status.HTTP_302_FOUND)
    
    # Validate role - allow all supported roles
    allowed_roles = ["student", "teacher", "hod", "principal", "college_admin", "super_admin", "admin"]
    if role not in allowed_roles:
        role = "student"

    from app.models.models import College, Department
    # If College Admin entered an institutional setup
    if role == "college_admin" and adm_college_name:
        existing_clg = db.query(College).filter(College.name == adm_college_name).first()
        if not existing_clg:
            import re
            code = re.sub(r'[^A-Z0-9]', '', adm_college_name.upper())[:8] or "CAMPUS"
            existing_clg = College(
                name=adm_college_name,
                code=code,
                address=adm_college_location or "Main Campus",
                contact_email=email,
                logo=adm_college_image or "https://cdn-icons-png.flaticon.com/512/2997/2997295.png"
            )
            db.add(existing_clg)
            db.commit()
            db.refresh(existing_clg)
        college_id = existing_clg.id
    elif custom_college and not college_id:
        existing_clg = db.query(College).filter(College.name == custom_college).first()
        if not existing_clg:
            import re
            code = re.sub(r'[^A-Z0-9]', '', custom_college.upper())[:8] or "INST"
            existing_clg = College(name=custom_college, code=code, contact_email=email)
            db.add(existing_clg)
            db.commit()
            db.refresh(existing_clg)
        college_id = existing_clg.id

    hashed_pw = get_password_hash(password)
    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_pw,
        role=role,
        phone_number=phone_number if phone_number else None,
        roll_number=roll_number if (role == "student" and roll_number) else None,
        employee_id=employee_id if (role != "student" and employee_id) else None,
        college_id=college_id if college_id else None,
        department_id=department_id if department_id else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log action
    log = ActivityLog(user_id=new_user.id, action="register", details=f"New user {new_user.email} created with role '{role}'.")
    db.add(log)
    db.commit()

    if "application/json" in request.headers.get("accept", ""):
        from fastapi.responses import JSONResponse
        return JSONResponse(content={"success": True, "redirect": "/auth/login?registered=true"})

    # Redirect to login page with success status
    return RedirectResponse(url="/auth/login?registered=true", status_code=status.HTTP_302_FOUND)


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request})


@router.post("/forgot-password")
def forgot_password_api(email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")
    
    # Generate mock token and log link to console
    mock_token = "mock-reset-token-12345"
    print("\n" + "="*50)
    print(f"PASSWORD RESET REQUEST FOR: {email}")
    print(f"Link: http://127.0.0.1:8000/auth/reset-password?email={email}&token={mock_token}")
    print("="*50 + "\n")

    return RedirectResponse(url="/auth/forgot-password?sent=true", status_code=status.HTTP_302_FOUND)


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, email: str, token: str):
    return templates.TemplateResponse("auth/reset_password.html", {"request": request, "email": email, "token": token})


@router.post("/reset-password")
def reset_password_api(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = get_password_hash(password)
    db.commit()
    
    # Log action
    log = ActivityLog(user_id=user.id, action="reset_password", details="Password reset successful.")
    db.add(log)
    db.commit()

    return RedirectResponse(url="/auth/login?reset=true", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
def logout(response: Response):
    # Clearcookie
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
