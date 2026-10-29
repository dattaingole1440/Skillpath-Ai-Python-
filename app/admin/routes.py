import json
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, status, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import (
    User, Career, Roadmap, Topic, Resource, Quiz, Question, CodingChallenge,
    Certificate, Video, AuditLog, RoadmapVersion, College, Department
)
from app.utils.auth import get_current_admin
from app.utils.audit import log_audit_event
from app.utils.versioning import create_roadmap_version_snapshot

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    total_students = db.query(User).filter(User.role == "student").count()
    total_careers = db.query(Career).filter(Career.is_deleted == False).count()
    total_roadmaps = db.query(Roadmap).filter(Roadmap.is_deleted == False).count()
    total_topics = db.query(Topic).filter(Topic.is_deleted == False).count()
    total_certificates = db.query(Certificate).count()
    total_videos = db.query(Video).filter(Video.is_deleted == False).count()

    recent_students = db.query(User).filter(User.role == "student").order_by(User.created_at.desc()).limit(5).all()
    topics = db.query(Topic).filter(Topic.is_deleted == False).order_by(Topic.id).all()
    quizzes = db.query(Quiz).filter(Quiz.is_deleted == False).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": admin,
            "total_students": total_students,
            "total_careers": total_careers,
            "total_roadmaps": total_roadmaps,
            "total_topics": total_topics,
            "total_certificates": total_certificates,
            "total_videos": total_videos,
            "recent_students": recent_students,
            "topics": topics,
            "quizzes": quizzes
        }
    )


@router.get("/users", response_class=HTMLResponse)
def manage_users(
    request: Request,
    search: Optional[str] = Query(None),
    role_filter: Optional[str] = Query(None),
    college_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    query = db.query(User)
    
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter((User.name.ilike(search_term)) | (User.email.ilike(search_term)))
        
    if role_filter and role_filter != "all":
        query = query.filter(User.role == role_filter)
        
    if college_filter and college_filter.isdigit():
        query = query.filter(User.college_id == int(college_filter))
        
    users = query.order_by(User.created_at.desc()).all()
    colleges = db.query(College).all()
    departments = db.query(Department).all()
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "user": admin,
            "users": users,
            "colleges": colleges,
            "departments": departments,
            "search": search or "",
            "role_filter": role_filter or "all",
            "college_filter": college_filter or ""
        }
    )


@router.post("/users/add")
def add_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    college_id: Optional[str] = Form(None),
    department_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    from app.utils.security import get_password_hash
    
    email_clean = email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        return RedirectResponse(url="/admin/users?error=email_exists", status_code=status.HTTP_303_SEE_OTHER)
        
    parsed_college_id = int(college_id) if college_id and college_id.strip().isdigit() else None
    parsed_dept_id = int(department_id) if department_id and department_id.strip().isdigit() else None

    new_user = User(
        name=name.strip(),
        email=email_clean,
        password_hash=get_password_hash(password),
        role=role,
        college_id=parsed_college_id,
        department_id=parsed_dept_id
    )
    db.add(new_user)
    db.commit()
    
    log_audit_event(
        db, admin,
        action="USER_CREATED",
        entity_type="user",
        entity_id=new_user.id,
        new_data={"email": email_clean, "role": role}
    )
    return RedirectResponse(url="/admin/users?success=user_created", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/edit/{user_id}")
def edit_user(
    user_id: int,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    college_id: Optional[str] = Form(None),
    department_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user_to_edit = db.query(User).filter(User.id == user_id).first()
    if not user_to_edit:
        raise HTTPException(status_code=404, detail="User not found")
        
    parsed_college_id = int(college_id) if college_id and college_id.strip().isdigit() else None
    parsed_dept_id = int(department_id) if department_id and department_id.strip().isdigit() else None

    old_data = {"email": user_to_edit.email, "role": user_to_edit.role}
    user_to_edit.name = name.strip()
    user_to_edit.email = email.strip().lower()
    user_to_edit.role = role
    user_to_edit.college_id = parsed_college_id
    user_to_edit.department_id = parsed_dept_id
    db.commit()
    
    log_audit_event(
        db, admin,
        action="USER_UPDATED",
        entity_type="user",
        entity_id=user_to_edit.id,
        old_data=old_data,
        new_data={"email": email.strip().lower(), "role": role}
    )
    return RedirectResponse(url="/admin/users?success=user_updated", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/delete/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
        
    old_data = {"email": user_to_delete.email, "role": user_to_delete.role}
    db.delete(user_to_delete)
    db.commit()
    
    log_audit_event(
        db, admin,
        action="USER_DELETED",
        entity_type="user",
        entity_id=user_id,
        old_data=old_data,
        new_data={}
    )
    return RedirectResponse(url="/admin/users?success=user_deleted", status_code=status.HTTP_303_SEE_OTHER)



# =======================================================
# CAREERS MANAGEMENT
# =======================================================
@router.get("/careers", response_class=HTMLResponse)
def manage_careers(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    careers = db.query(Career).filter(Career.is_deleted == False).order_by(Career.id).all()
    return templates.TemplateResponse("admin/careers.html", {"request": request, "user": admin, "careers": careers})


@router.post("/careers/add")
def add_career(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    career = Career(name=name, description=description, is_deleted=False)
    db.add(career)
    db.commit()
    db.refresh(career)

    log_audit_event(
        db, admin,
        action="CAREER_CREATED",
        entity_type="career",
        entity_id=career.id,
        new_data={"name": career.name, "description": career.description}
    )

    return RedirectResponse(url="/admin/careers", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/careers/edit/{career_id}")
def edit_career(
    career_id: int,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    career = db.query(Career).filter(Career.id == career_id, Career.is_deleted == False).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    old_data = {"name": career.name, "description": career.description}
    career.name = name
    career.description = description
    db.commit()

    log_audit_event(
        db, admin,
        action="CAREER_UPDATED",
        entity_type="career",
        entity_id=career.id,
        old_data=old_data,
        new_data={"name": career.name, "description": career.description}
    )

    return RedirectResponse(url="/admin/careers", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/careers/delete/{career_id}")
def delete_career(
    career_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    career = db.query(Career).filter(Career.id == career_id, Career.is_deleted == False).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    old_data = {"name": career.name}
    career.is_deleted = True
    career.deleted_at = datetime.datetime.utcnow()

    # Soft delete related roadmaps
    roadmaps = db.query(Roadmap).filter(Roadmap.career_id == career_id).all()
    for rm in roadmaps:
        rm.is_deleted = True
        rm.deleted_at = datetime.datetime.utcnow()

    db.commit()

    log_audit_event(
        db, admin,
        action="CAREER_DELETED",
        entity_type="career",
        entity_id=career.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(career.deleted_at)}
    )

    return RedirectResponse(url="/admin/careers", status_code=status.HTTP_303_SEE_OTHER)


# =======================================================
# ROADMAPS / MILESTONES MANAGEMENT
# =======================================================
@router.get("/roadmaps/{career_id}", response_class=HTMLResponse)
def manage_roadmaps(career_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    career = db.query(Career).filter(Career.id == career_id, Career.is_deleted == False).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    roadmaps = db.query(Roadmap).filter(
        Roadmap.career_id == career_id,
        Roadmap.is_deleted == False
    ).order_by(Roadmap.order).all()

    return templates.TemplateResponse(
        "admin/roadmaps.html",
        {"request": request, "user": admin, "career": career, "roadmaps": roadmaps}
    )


@router.post("/roadmaps/add")
def add_roadmap(
    career_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    order: int = Form(1),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    roadmap = Roadmap(career_id=career_id, title=title, description=description, order=order, is_deleted=False)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    log_audit_event(
        db, admin,
        action="ROADMAP_CREATED",
        entity_type="roadmap",
        entity_id=roadmap.id,
        new_data={"title": roadmap.title, "career_id": roadmap.career_id, "order": roadmap.order}
    )
    create_roadmap_version_snapshot(db, roadmap.id, admin, "Initial milestone created")

    return RedirectResponse(url=f"/admin/roadmaps/{career_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/roadmaps/edit/{roadmap_id}")
def edit_roadmap(
    roadmap_id: int,
    title: str = Form(...),
    description: str = Form(""),
    order: int = Form(1),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    old_data = {"title": roadmap.title, "description": roadmap.description, "order": roadmap.order}
    roadmap.title = title
    roadmap.description = description
    roadmap.order = order
    roadmap.updated_at = datetime.datetime.utcnow()
    db.commit()

    log_audit_event(
        db, admin,
        action="ROADMAP_UPDATED",
        entity_type="roadmap",
        entity_id=roadmap.id,
        old_data=old_data,
        new_data={"title": roadmap.title, "description": roadmap.description, "order": roadmap.order}
    )
    create_roadmap_version_snapshot(db, roadmap.id, admin, f"Updated roadmap: {roadmap.title}")

    return RedirectResponse(url=f"/admin/roadmaps/{roadmap.career_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/roadmaps/delete/{roadmap_id}")
def delete_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    career_id = roadmap.career_id
    old_data = {"title": roadmap.title, "career_id": roadmap.career_id}

    # Soft delete milestone
    roadmap.is_deleted = True
    roadmap.deleted_at = datetime.datetime.utcnow()

    # Soft delete related topics & videos
    topics = db.query(Topic).filter(Topic.roadmap_id == roadmap_id).all()
    for t in topics:
        t.is_deleted = True
        t.deleted_at = datetime.datetime.utcnow()

    videos = db.query(Video).filter(Video.roadmap_id == roadmap_id).all()
    for v in videos:
        v.is_deleted = True
        v.deleted_at = datetime.datetime.utcnow()

    db.commit()

    log_audit_event(
        db, admin,
        action="ROADMAP_DELETED",
        entity_type="roadmap",
        entity_id=roadmap.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(roadmap.deleted_at)}
    )

    return RedirectResponse(url=f"/admin/roadmaps/{career_id}", status_code=status.HTTP_303_SEE_OTHER)


# =======================================================
# TOPICS / MODULES MANAGEMENT
# =======================================================
@router.get("/topics/{roadmap_id}", response_class=HTMLResponse)
def manage_topics(roadmap_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    topics = db.query(Topic).filter(
        Topic.roadmap_id == roadmap_id,
        Topic.is_deleted == False
    ).order_by(Topic.order).all()

    return templates.TemplateResponse(
        "admin/topics.html",
        {"request": request, "user": admin, "roadmap": roadmap, "topics": topics}
    )


def format_youtube_videos(input_str: str, topic_title: str) -> str:
    raw = (input_str or "").strip()
    if not raw:
        return "[]"
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return json.dumps(data)
    except Exception:
        pass
    urls = [line.strip() for line in raw.splitlines() if line.strip()]
    video_list = []
    for idx, u in enumerate(urls):
        if "youtube.com" in u or "youtu.be" in u or u.startswith("http"):
            label = f"{topic_title} Tutorial" if len(urls) == 1 else f"{topic_title} Video Part {idx+1}"
            video_list.append({"title": label, "url": u})
    if video_list:
        return json.dumps(video_list)
    return "[]"


def format_official_docs(input_str: str, topic_title: str) -> str:
    raw = (input_str or "").strip()
    if not raw:
        return "[]"
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return json.dumps(data)
    except Exception:
        pass
    docs = [line.strip() for line in raw.splitlines() if line.strip()]
    doc_list = []
    for idx, d in enumerate(docs):
        if d.startswith("http"):
            label = f"{topic_title} Official Guide" if len(docs) == 1 else f"{topic_title} Guide Part {idx+1}"
            doc_list.append({"title": label, "url": d})
    if doc_list:
        return json.dumps(doc_list)
    return "[]"


def sync_videos_for_topic(db: Session, topic: Topic, youtube_videos_json: str):
    """Synchronizes topic videos into the persistent videos table in MySQL."""
    try:
        v_list = json.loads(youtube_videos_json) if youtube_videos_json else []
        if isinstance(v_list, list):
            # Soft delete old active videos for this topic
            db.query(Video).filter(Video.topic_id == topic.id).update({
                Video.is_deleted: True,
                Video.deleted_at: datetime.datetime.utcnow()
            })
            for idx, v in enumerate(v_list):
                url = v.get("url") if isinstance(v, dict) else str(v)
                v_title = v.get("title", f"{topic.title} Tutorial") if isinstance(v, dict) else f"{topic.title} Tutorial"
                if url:
                    vid = Video(
                        topic_id=topic.id,
                        roadmap_id=topic.roadmap_id,
                        career_id=topic.career_id,
                        title=v_title,
                        youtube_url=url,
                        video_type="tutorial",
                        display_order=idx + 1,
                        is_active=True,
                        is_deleted=False
                    )
                    db.add(vid)
            db.commit()
    except Exception as ex:
        print(f"[VIDEO SYNC WARNING] {ex}")


@router.post("/videos/upload")
def upload_video_file(
    topic_id: int = Form(...),
    title: str = Form(...),
    video_source: str = Form("youtube"),
    youtube_url: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    import os
    import shutil
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    final_url = ""
    if video_source == "local" and video_file and video_file.filename:
        os.makedirs("app/static/uploads/videos", exist_ok=True)
        file_ext = os.path.splitext(video_file.filename)[1]
        saved_filename = f"video_topic_{topic_id}_{int(datetime.datetime.utcnow().timestamp())}{file_ext}"
        saved_path = os.path.join("app/static/uploads/videos", saved_filename)
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        final_url = f"/static/uploads/videos/{saved_filename}"
    else:
        final_url = youtube_url or ""

    if final_url:
        vid = Video(
            topic_id=topic.id,
            roadmap_id=topic.roadmap_id,
            career_id=topic.career_id,
            title=title,
            youtube_url=final_url,
            video_type="local" if video_source == "local" else "tutorial",
            is_active=True,
            is_deleted=False
        )
        db.add(vid)
        db.commit()

        log_audit_event(
            db, admin,
            action="VIDEO_UPLOADED",
            entity_type="video",
            entity_id=vid.id,
            new_data={"title": title, "topic_id": topic_id, "url": final_url, "source": video_source}
        )

    return RedirectResponse(url=f"/admin/topics/{topic.roadmap_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/topics/add")
def add_topic(
    roadmap_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    learning_objectives: str = Form(""),
    difficulty: str = Form("medium"),
    estimated_time: float = Form(1.0),
    order: int = Form(1),
    youtube_videos: str = Form("[]"),
    official_documentation: str = Form("[]"),
    notes: str = Form(""),
    cheat_sheet: str = Form(""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    formatted_youtube = format_youtube_videos(youtube_videos, title)
    formatted_docs = format_official_docs(official_documentation, title)

    topic = Topic(
        roadmap_id=roadmap_id,
        career_id=roadmap.career_id,
        title=title,
        description=description,
        learning_objectives=learning_objectives,
        difficulty=difficulty,
        estimated_time=estimated_time,
        order=order,
        youtube_videos=formatted_youtube,
        official_documentation=formatted_docs,
        notes=notes,
        cheat_sheet=cheat_sheet,
        is_admin_modified=True,
        is_deleted=False
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    # Sync persistent videos table
    sync_videos_for_topic(db, topic, formatted_youtube)

    log_audit_event(
        db, admin,
        action="MODULE_CREATED",
        entity_type="module",
        entity_id=topic.id,
        new_data={"title": topic.title, "roadmap_id": topic.roadmap_id, "difficulty": topic.difficulty}
    )
    create_roadmap_version_snapshot(db, topic.roadmap_id, admin, f"Added topic: {topic.title}")

    return RedirectResponse(url=f"/admin/topics/{roadmap_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/topics/edit/{topic_id}")
def edit_topic(
    topic_id: int,
    title: str = Form(...),
    description: str = Form(""),
    learning_objectives: str = Form(""),
    difficulty: str = Form("medium"),
    estimated_time: float = Form(1.0),
    order: int = Form(1),
    youtube_videos: str = Form(""),
    official_documentation: str = Form(""),
    notes: str = Form(""),
    cheat_sheet: str = Form(""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    old_data = {"title": topic.title, "difficulty": topic.difficulty, "order": topic.order}

    formatted_youtube = format_youtube_videos(youtube_videos, title)
    formatted_docs = format_official_docs(official_documentation, title)

    topic.title = title
    topic.description = description
    topic.learning_objectives = learning_objectives
    topic.difficulty = difficulty
    topic.estimated_time = estimated_time
    topic.order = order
    topic.youtube_videos = formatted_youtube
    topic.official_documentation = formatted_docs
    topic.notes = notes
    topic.cheat_sheet = cheat_sheet
    topic.is_admin_modified = True
    topic.updated_at = datetime.datetime.utcnow()
    db.commit()

    # Sync persistent videos table
    sync_videos_for_topic(db, topic, formatted_youtube)

    log_audit_event(
        db, admin,
        action="MODULE_UPDATED",
        entity_type="module",
        entity_id=topic.id,
        old_data=old_data,
        new_data={"title": topic.title, "difficulty": topic.difficulty, "order": topic.order}
    )
    create_roadmap_version_snapshot(db, topic.roadmap_id, admin, f"Edited topic: {topic.title}")

    return RedirectResponse(url=f"/admin/topics/{topic.roadmap_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/videos/add")
async def add_admin_video(
    title: str = Form(...),
    topic_id: int = Form(...),
    youtube_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    video_link = (youtube_url or "").strip()
    if file and file.filename:
        import os, shutil
        os.makedirs("app/static/uploads/videos", exist_ok=True)
        filename = f"admin_vid_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join("app/static/uploads/videos", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        video_link = f"/static/uploads/videos/{filename}"
    elif "youtube.com/watch?v=" in video_link:
        vid_id = video_link.split("watch?v=")[1].split("&")[0]
        video_link = f"https://www.youtube.com/embed/{vid_id}"
    elif "youtu.be/" in video_link:
        vid_id = video_link.split("youtu.be/")[1].split("?")[0]
        video_link = f"https://www.youtube.com/embed/{vid_id}"

    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    vid = Video(
        topic_id=topic_id,
        roadmap_id=topic.roadmap_id if topic else None,
        career_id=topic.career_id if topic else None,
        title=title,
        youtube_url=video_link or "/static/uploads/videos/default.mp4",
        description=description,
        is_active=True
    )
    db.add(vid)
    db.commit()
    db.refresh(vid)

    log_audit_event(
        db, admin,
        action="VIDEO_CREATED",
        entity_type="video",
        entity_id=vid.id,
        new_data={"title": title, "topic_id": topic_id}
    )
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/topics/delete/{topic_id}")
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    roadmap_id = topic.roadmap_id
    old_data = {"title": topic.title, "roadmap_id": topic.roadmap_id}

    # Soft delete topic and its videos
    topic.is_deleted = True
    topic.deleted_at = datetime.datetime.utcnow()

    db.query(Video).filter(Video.topic_id == topic_id).update({
        Video.is_deleted: True,
        Video.deleted_at: datetime.datetime.utcnow()
    })
    db.commit()

    log_audit_event(
        db, admin,
        action="MODULE_DELETED",
        entity_type="module",
        entity_id=topic.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(topic.deleted_at)}
    )
    create_roadmap_version_snapshot(db, roadmap_id, admin, f"Deleted topic: {topic.title}")

    return RedirectResponse(url=f"/admin/topics/{roadmap_id}", status_code=status.HTTP_303_SEE_OTHER)


# =======================================================
# QUIZZES & QUESTIONS MANAGEMENT
# =======================================================
@router.get("/quizzes", response_class=HTMLResponse)
def list_all_quizzes_admin(request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    topics = db.query(Topic).filter(Topic.is_deleted == False).order_by(Topic.id).all()
    quizzes = db.query(Quiz).filter(Quiz.is_deleted == False).all()
    
    # Ensure topics have a quiz
    topic_ids_with_quiz = {q.topic_id for q in quizzes}
    for t in topics:
        if t.id not in topic_ids_with_quiz:
            q = Quiz(topic_id=t.id, passing_percentage=75, title=f"{t.title} Checkpoint Quiz", is_deleted=False)
            db.add(q)
    db.commit()
    quizzes = db.query(Quiz).filter(Quiz.is_deleted == False).all()

    quiz_data = []
    for q in quizzes:
        t = db.query(Topic).filter(Topic.id == q.topic_id).first()
        q_count = db.query(Question).filter(Question.quiz_id == q.id, Question.is_deleted == False).count()
        quiz_data.append({
            "quiz": q,
            "topic": t,
            "questions_count": q_count
        })

    return templates.TemplateResponse(
        "admin/quizzes_all.html",
        {"request": request, "user": admin, "quiz_data": quiz_data, "topics": topics}
    )


@router.get("/quizzes/{topic_id}", response_class=HTMLResponse)
def manage_quizzes(topic_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    quizzes = db.query(Quiz).filter(Quiz.topic_id == topic_id, Quiz.is_deleted == False).all()
    return templates.TemplateResponse(
        "admin/quizzes.html",
        {"request": request, "user": admin, "topic": topic, "quizzes": quizzes}
    )


@router.post("/quizzes/add")
def add_quiz(
    topic_id: int = Form(...),
    passing_percentage: int = Form(70),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    quiz = Quiz(topic_id=topic_id, passing_percentage=passing_percentage, is_deleted=False)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    log_audit_event(
        db, admin,
        action="QUIZ_CREATED",
        entity_type="quiz",
        entity_id=quiz.id,
        new_data={"topic_id": topic_id, "passing_percentage": passing_percentage}
    )
    return RedirectResponse(url=f"/admin/quizzes/{topic_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/quizzes/edit/{quiz_id}")
def edit_quiz(
    quiz_id: int,
    passing_percentage: int = Form(70),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_deleted == False).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    old_data = {"passing_percentage": quiz.passing_percentage}
    quiz.passing_percentage = passing_percentage
    quiz.passing_score = passing_percentage
    quiz.is_admin_modified = True
    db.commit()

    log_audit_event(
        db, admin,
        action="QUIZ_UPDATED",
        entity_type="quiz",
        entity_id=quiz.id,
        old_data=old_data,
        new_data={"passing_percentage": passing_percentage}
    )

    return RedirectResponse(url=f"/admin/quizzes/{quiz.topic_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/quizzes/delete/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_deleted == False).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    topic_id = quiz.topic_id
    old_data = {"topic_id": topic_id, "passing_percentage": quiz.passing_percentage}

    quiz.is_deleted = True
    quiz.deleted_at = datetime.datetime.utcnow()

    # Also soft delete related questions
    db.query(Question).filter(Question.quiz_id == quiz_id).update({
        Question.is_deleted: True,
        Question.deleted_at: datetime.datetime.utcnow()
    })
    db.commit()

    log_audit_event(
        db, admin,
        action="QUIZ_DELETED",
        entity_type="quiz",
        entity_id=quiz.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(quiz.deleted_at)}
    )

    return RedirectResponse(url=f"/admin/quizzes/{topic_id}", status_code=status.HTTP_303_SEE_OTHER)



@router.get("/questions/{quiz_id}", response_class=HTMLResponse)
def manage_questions(quiz_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_deleted == False).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    topic = db.query(Topic).filter(Topic.id == quiz.topic_id).first()
    questions = db.query(Question).filter(Question.quiz_id == quiz_id, Question.is_deleted == False).all()

    return templates.TemplateResponse(
        "admin/questions.html",
        {"request": request, "user": admin, "quiz": quiz, "topic": topic, "questions": questions}
    )


@router.post("/questions/add")
def add_question(
    quiz_id: int = Form(...),
    question_text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_option: str = Form(...),
    explanation: str = Form(""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option.upper(),
        explanation=explanation,
        is_deleted=False
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    log_audit_event(
        db, admin,
        action="QUESTION_CREATED",
        entity_type="question",
        entity_id=question.id,
        new_data={"question_text": question.question_text, "quiz_id": quiz_id, "correct_option": question.correct_option}
    )

    return RedirectResponse(url=f"/admin/questions/{quiz_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/questions/edit/{question_id}")
def edit_question(
    question_id: int,
    question_text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_option: str = Form(...),
    explanation: str = Form(""),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    question = db.query(Question).filter(Question.id == question_id, Question.is_deleted == False).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    old_data = {"question_text": question.question_text, "correct_option": question.correct_option}

    question.question_text = question_text
    question.option_a = option_a
    question.option_b = option_b
    question.option_c = option_c
    question.option_d = option_d
    question.correct_option = correct_option.upper()
    question.explanation = explanation
    db.commit()

    log_audit_event(
        db, admin,
        action="QUESTION_UPDATED",
        entity_type="question",
        entity_id=question.id,
        old_data=old_data,
        new_data={"question_text": question.question_text, "correct_option": question.correct_option}
    )

    return RedirectResponse(url=f"/admin/questions/{question.quiz_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/questions/delete/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    question = db.query(Question).filter(Question.id == question_id, Question.is_deleted == False).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    quiz_id = question.quiz_id
    old_data = {"question_text": question.question_text, "quiz_id": quiz_id}

    question.is_deleted = True
    question.deleted_at = datetime.datetime.utcnow()
    db.commit()

    log_audit_event(
        db, admin,
        action="QUESTION_DELETED",
        entity_type="question",
        entity_id=question.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(question.deleted_at)}
    )

    return RedirectResponse(url=f"/admin/questions/{quiz_id}", status_code=status.HTTP_303_SEE_OTHER)


# =======================================================
# CODING CHALLENGES
# =======================================================
@router.get("/challenges/{topic_id}", response_class=HTMLResponse)
def manage_challenges(topic_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    challenges = db.query(CodingChallenge).filter(CodingChallenge.topic_id == topic_id, CodingChallenge.is_deleted == False).all()
    return templates.TemplateResponse(
        "admin/challenges.html",
        {"request": request, "user": admin, "topic": topic, "challenges": challenges}
    )


@router.post("/challenges/add")
def add_challenge(
    topic_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    difficulty: str = Form("medium"),
    template_code: str = Form(""),
    test_cases: str = Form("[]"),
    score_points: int = Form(10),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    try:
        json.loads(test_cases)
    except Exception:
        test_cases = "[]"

    challenge = CodingChallenge(
        topic_id=topic_id,
        title=title,
        description=description,
        difficulty=difficulty,
        template_code=template_code,
        test_cases=test_cases,
        score_points=score_points,
        is_deleted=False
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    log_audit_event(
        db, admin,
        action="CHALLENGE_CREATED",
        entity_type="challenge",
        entity_id=challenge.id,
        new_data={"title": challenge.title, "topic_id": topic_id, "score_points": score_points}
    )
    return RedirectResponse(url=f"/admin/challenges/{topic_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/challenges/edit/{challenge_id}")
def edit_challenge(
    challenge_id: int,
    title: str = Form(...),
    description: str = Form(...),
    difficulty: str = Form("medium"),
    template_code: str = Form(""),
    test_cases: str = Form("[]"),
    score_points: int = Form(10),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id, CodingChallenge.is_deleted == False).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Coding challenge not found")

    try:
        json.loads(test_cases)
    except Exception:
        test_cases = challenge.test_cases or "[]"

    old_data = {"title": challenge.title, "difficulty": challenge.difficulty, "score_points": challenge.score_points}

    challenge.title = title
    challenge.description = description
    challenge.difficulty = difficulty
    challenge.template_code = template_code
    challenge.test_cases = test_cases
    challenge.score_points = score_points
    db.commit()

    log_audit_event(
        db, admin,
        action="CHALLENGE_UPDATED",
        entity_type="challenge",
        entity_id=challenge.id,
        old_data=old_data,
        new_data={"title": challenge.title, "difficulty": challenge.difficulty, "score_points": challenge.score_points}
    )

    return RedirectResponse(url=f"/admin/challenges/{challenge.topic_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/challenges/delete/{challenge_id}")
def delete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id, CodingChallenge.is_deleted == False).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Coding challenge not found")

    topic_id = challenge.topic_id
    old_data = {"title": challenge.title, "topic_id": topic_id}

    challenge.is_deleted = True
    challenge.deleted_at = datetime.datetime.utcnow()
    db.commit()

    log_audit_event(
        db, admin,
        action="CHALLENGE_DELETED",
        entity_type="challenge",
        entity_id=challenge.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(challenge.deleted_at)}
    )

    return RedirectResponse(url=f"/admin/challenges/{topic_id}", status_code=status.HTTP_303_SEE_OTHER)



# =======================================================
# AUDIT LOGS VIEWER
# =======================================================
@router.get("/audit-logs", response_class=HTMLResponse)
def view_audit_logs(
    request: Request,
    entity_filter: str = "",
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    query = db.query(AuditLog)
    if entity_filter:
        query = query.filter(AuditLog.entity_type == entity_filter)

    logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()

    return templates.TemplateResponse(
        "admin/audit_logs.html",
        {
            "request": request,
            "user": admin,
            "logs": logs,
            "active_filter": entity_filter
        }
    )


@router.get("/export/students")
def export_students_report(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    from fastapi.responses import Response
    students = db.query(User).filter(User.role == "student").all()

    csv_lines = ["ID,Name,Email,Streak,Quiz_Avg,Coding_Avg,Learning_Hours,XP,Rank,Created_At"]
    for s in students:
        csv_lines.append(f'{s.id},"{s.name}","{s.email}",{s.daily_streak},{s.quiz_avg},{s.coding_avg},{s.learning_hours},{s.xp},"{s.rank}","{s.created_at}"')

    csv_content = "\n".join(csv_lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_report.csv"}
    )
