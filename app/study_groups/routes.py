from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, StudyGroup, GroupMember, GroupMessage, GroupNote, ActivityLog
from app.utils.auth import get_current_user

router = APIRouter(prefix="/study-groups", tags=["Study Groups"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_study_groups_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    groups = db.query(StudyGroup).all()
    user_group_ids = [m.group_id for m in db.query(GroupMember).filter(GroupMember.student_id == current_user.id).all()]

    return templates.TemplateResponse(
        "study_groups/index.html",
        {
            "request": request,
            "user": current_user,
            "groups": groups,
            "user_group_ids": user_group_ids
        }
    )

@router.get("/{group_id}", response_class=HTMLResponse)
def get_study_group_detail(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found.")

    member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.student_id == current_user.id).first()
    if not member and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You must join this study group first.")

    messages = db.query(GroupMessage).filter(GroupMessage.group_id == group_id).order_by(GroupMessage.created_at).all()
    notes = db.query(GroupNote).filter(GroupNote.group_id == group_id).order_by(GroupNote.created_at.desc()).all()
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

    return templates.TemplateResponse(
        "study_groups/detail.html",
        {
            "request": request,
            "user": current_user,
            "group": group,
            "messages": messages,
            "notes": notes,
            "members": members
        }
    )

@router.post("/create")
def create_study_group(
    name: str = Form(...),
    description: str = Form(""),
    category: str = Form("General"),
    max_members: int = Form(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    group = StudyGroup(
        name=name,
        description=description,
        category=category,
        created_by=current_user.id,
        max_members=max_members
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    # Add creator as admin member
    member = GroupMember(group_id=group.id, student_id=current_user.id, role="admin")
    db.add(member)
    db.commit()

    return JSONResponse({"status": "success", "group_id": group.id})

@router.post("/{group_id}/join")
def join_study_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    existing = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.student_id == current_user.id).first()
    if existing:
        return JSONResponse({"status": "already_joined", "message": "Already a member of this group."})

    member = GroupMember(group_id=group_id, student_id=current_user.id, role="member")
    db.add(member)
    db.commit()

    return JSONResponse({"status": "success", "message": "Joined study group!"})

@router.post("/{group_id}/message")
def send_group_message(
    group_id: int,
    message: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = GroupMessage(
        group_id=group_id,
        student_id=current_user.id,
        message=message
    )
    db.add(msg)
    db.commit()

    return JSONResponse({"status": "success", "user_name": current_user.name, "message": message, "created_at": msg.created_at.strftime("%H:%M")})

@router.post("/{group_id}/note")
def share_group_note(
    group_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = GroupNote(
        group_id=group_id,
        student_id=current_user.id,
        title=title,
        content=content
    )
    db.add(note)
    db.commit()

    return JSONResponse({"status": "success", "message": "Note shared with group!"})
