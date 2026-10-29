import json
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import (
    User, Career, Roadmap, Topic, Video, Quiz, Question, CodingChallenge,
    StudentProgress, AuditLog, RoadmapVersion
)
from app.utils.auth import get_current_user, get_current_admin
from app.utils.audit import log_audit_event
from app.utils.versioning import create_roadmap_version_snapshot

router = APIRouter(prefix="/api", tags=["SkillPath Core APIs"])

# =======================================================
# PYDANTIC SCHEMAS FOR INPUT VALIDATION
# =======================================================
class RoadmapCreateSchema(BaseModel):
    career_id: int
    title: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = ""
    order: Optional[int] = 1

class RoadmapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    order: Optional[int] = None

class ModuleCreateSchema(BaseModel):
    roadmap_id: int
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = ""
    learning_objectives: Optional[str] = ""
    difficulty: Optional[str] = "medium"
    estimated_time: Optional[float] = 1.0
    order: Optional[int] = 1
    youtube_videos: Optional[str] = "[]"
    official_documentation: Optional[str] = "[]"
    notes: Optional[str] = ""
    cheat_sheet: Optional[str] = ""

class ModuleUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_time: Optional[float] = None
    order: Optional[int] = None
    youtube_videos: Optional[str] = None
    official_documentation: Optional[str] = None
    notes: Optional[str] = None
    cheat_sheet: Optional[str] = None

class VideoCreateSchema(BaseModel):
    topic_id: Optional[int] = None
    roadmap_id: Optional[int] = None
    career_id: Optional[int] = None
    title: str = Field(..., min_length=2, max_length=255)
    youtube_url: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = ""
    thumbnail_url: Optional[str] = ""
    video_type: Optional[str] = "tutorial"
    display_order: Optional[int] = 1
    is_active: Optional[bool] = True

class VideoUpdateSchema(BaseModel):
    title: Optional[str] = None
    youtube_url: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_type: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class QuestionUpdateSchema(BaseModel):
    question_text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: Optional[str] = None
    explanation: Optional[str] = None


# =======================================================
# 1. ROADMAPS & MILESTONES APIS
# =======================================================
@router.get("/roadmaps")
def list_roadmaps(career_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Fetch all active roadmaps (milestones) directly from MySQL single source of truth."""
    query = db.query(Roadmap).filter(Roadmap.is_deleted == False)
    if career_id:
        query = query.filter(Roadmap.career_id == career_id)
    roadmaps = query.order_by(Roadmap.order).all()

    result = []
    for rm in roadmaps:
        topics_count = db.query(Topic).filter(
            Topic.roadmap_id == rm.id,
            Topic.is_deleted == False
        ).count()
        result.append({
            "id": rm.id,
            "career_id": rm.career_id,
            "title": rm.title,
            "description": rm.description,
            "order": rm.order,
            "topics_count": topics_count,
            "created_at": rm.created_at
        })
    return {"roadmaps": result}


@router.get("/roadmaps/{roadmap_id}")
def get_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    """Fetch a single roadmap with its modules and videos."""
    rm = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not rm:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    topics = db.query(Topic).filter(
        Topic.roadmap_id == rm.id,
        Topic.is_deleted == False
    ).order_by(Topic.order).all()

    topics_data = []
    for t in topics:
        videos = db.query(Video).filter(Video.topic_id == t.id, Video.is_deleted == False).all()
        topics_data.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "difficulty": t.difficulty,
            "estimated_time": t.estimated_time,
            "order": t.order,
            "videos": [{
                "id": v.id,
                "title": v.title,
                "youtube_url": v.youtube_url,
                "display_order": v.display_order
            } for v in videos]
        })

    return {
        "id": rm.id,
        "career_id": rm.career_id,
        "title": rm.title,
        "description": rm.description,
        "order": rm.order,
        "modules": topics_data
    }


@router.get("/milestones/{milestone_id}")
def get_milestone_alias(milestone_id: int, db: Session = Depends(get_db)):
    """Alias for roadmap detail endpoint."""
    return get_roadmap(milestone_id, db)


@router.post("/roadmaps")
def create_roadmap(payload: RoadmapCreateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Create a new roadmap milestone (Admin only). Persists to MySQL & creates audit log."""
    career = db.query(Career).filter(Career.id == payload.career_id, Career.is_deleted == False).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")

    roadmap = Roadmap(
        career_id=payload.career_id,
        title=payload.title,
        description=payload.description,
        order=payload.order,
        is_deleted=False
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    # Log audit & create version
    log_audit_event(
        db, admin,
        action="ROADMAP_CREATED",
        entity_type="roadmap",
        entity_id=roadmap.id,
        new_data={"title": roadmap.title, "career_id": roadmap.career_id, "order": roadmap.order}
    )
    create_roadmap_version_snapshot(db, roadmap.id, admin, "Initial milestone creation")

    return {
        "message": "Roadmap created successfully",
        "roadmap": {
            "id": roadmap.id,
            "career_id": roadmap.career_id,
            "title": roadmap.title,
            "description": roadmap.description,
            "order": roadmap.order,
            "created_at": roadmap.created_at
        }
    }


@router.put("/roadmaps/{roadmap_id}")
def update_roadmap(roadmap_id: int, payload: RoadmapUpdateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Update roadmap details (Admin only). Persists to MySQL & creates audit log."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    old_data = {"title": roadmap.title, "description": roadmap.description, "order": roadmap.order}

    if payload.title is not None:
        roadmap.title = payload.title
    if payload.description is not None:
        roadmap.description = payload.description
    if payload.order is not None:
        roadmap.order = payload.order

    roadmap.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(roadmap)

    log_audit_event(
        db, admin,
        action="ROADMAP_UPDATED",
        entity_type="roadmap",
        entity_id=roadmap.id,
        old_data=old_data,
        new_data={"title": roadmap.title, "description": roadmap.description, "order": roadmap.order}
    )
    create_roadmap_version_snapshot(db, roadmap.id, admin, f"Updated title/order: {roadmap.title}")

    return {
        "message": "Roadmap updated successfully",
        "roadmap": {
            "id": roadmap.id,
            "career_id": roadmap.career_id,
            "title": roadmap.title,
            "description": roadmap.description,
            "order": roadmap.order,
            "updated_at": roadmap.updated_at
        }
    }


@router.delete("/roadmaps/{roadmap_id}")
def delete_roadmap(roadmap_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Soft delete a roadmap milestone (Admin only). Preserves student progress history."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    old_data = {"title": roadmap.title, "career_id": roadmap.career_id}

    roadmap.is_deleted = True
    roadmap.deleted_at = datetime.datetime.utcnow()

    # Soft delete all child topics and videos
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

    return {"message": "Roadmap and associated topics soft-deleted successfully", "id": roadmap_id}


# =======================================================
# 2. MODULES / TOPICS APIS
# =======================================================
@router.get("/modules/{module_id}")
def get_module(module_id: int, db: Session = Depends(get_db)):
    """Fetch module details, associated videos, quizzes, and challenges."""
    topic = db.query(Topic).filter(Topic.id == module_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Module not found")

    videos = db.query(Video).filter(
        Video.topic_id == topic.id,
        Video.is_deleted == False
    ).order_by(Video.display_order).all()

    quizzes = db.query(Quiz).filter(Quiz.topic_id == topic.id, Quiz.is_deleted == False).all()
    challenges = db.query(CodingChallenge).filter(CodingChallenge.topic_id == topic.id, CodingChallenge.is_deleted == False).all()

    return {
        "id": topic.id,
        "roadmap_id": topic.roadmap_id,
        "title": topic.title,
        "description": topic.description,
        "learning_objectives": topic.learning_objectives,
        "difficulty": topic.difficulty,
        "estimated_time": topic.estimated_time,
        "order": topic.order,
        "videos": [{
            "id": v.id,
            "title": v.title,
            "youtube_url": v.youtube_url,
            "description": v.description,
            "thumbnail_url": v.thumbnail_url,
            "display_order": v.display_order
        } for v in videos],
        "quizzes_count": len(quizzes),
        "challenges_count": len(challenges)
    }


@router.post("/modules")
def create_module(payload: ModuleCreateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Create a new module/topic (Admin only). Persists to MySQL, syncs videos & audit log."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == payload.roadmap_id, Roadmap.is_deleted == False).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    topic = Topic(
        roadmap_id=payload.roadmap_id,
        career_id=roadmap.career_id,
        title=payload.title,
        description=payload.description,
        learning_objectives=payload.learning_objectives,
        difficulty=payload.difficulty,
        estimated_time=payload.estimated_time,
        order=payload.order,
        youtube_videos=payload.youtube_videos,
        official_documentation=payload.official_documentation,
        notes=payload.notes,
        cheat_sheet=payload.cheat_sheet,
        is_admin_modified=True,
        is_deleted=False
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    # Automatically parse and insert videos into the persistent videos table
    if payload.youtube_videos:
        try:
            v_list = json.loads(payload.youtube_videos)
            if isinstance(v_list, list):
                for idx, v in enumerate(v_list):
                    url = v.get("url") if isinstance(v, dict) else str(v)
                    v_title = v.get("title", f"{topic.title} Tutorial") if isinstance(v, dict) else f"{topic.title} Tutorial"
                    if url:
                        vid = Video(
                            topic_id=topic.id,
                            roadmap_id=topic.roadmap_id,
                            career_id=roadmap.career_id,
                            title=v_title,
                            youtube_url=url,
                            display_order=idx + 1,
                            is_active=True,
                            is_deleted=False
                        )
                        db.add(vid)
                db.commit()
        except Exception as ex:
            print(f"[VIDEO SYNC WARNING] Could not parse videos: {ex}")

    log_audit_event(
        db, admin,
        action="MODULE_CREATED",
        entity_type="module",
        entity_id=topic.id,
        new_data={"title": topic.title, "roadmap_id": topic.roadmap_id, "difficulty": topic.difficulty}
    )
    create_roadmap_version_snapshot(db, topic.roadmap_id, admin, f"Added module: {topic.title}")

    return {"message": "Module created successfully", "module": {"id": topic.id, "title": topic.title}}


@router.put("/modules/{module_id}")
def update_module(module_id: int, payload: ModuleUpdateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Update module details (Admin only). Persists to MySQL, syncs videos & audit log."""
    topic = db.query(Topic).filter(Topic.id == module_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Module not found")

    old_data = {
        "title": topic.title,
        "description": topic.description,
        "difficulty": topic.difficulty,
        "estimated_time": topic.estimated_time,
        "order": topic.order
    }

    if payload.title is not None:
        topic.title = payload.title
    if payload.description is not None:
        topic.description = payload.description
    if payload.learning_objectives is not None:
        topic.learning_objectives = payload.learning_objectives
    if payload.difficulty is not None:
        topic.difficulty = payload.difficulty
    if payload.estimated_time is not None:
        topic.estimated_time = payload.estimated_time
    if payload.order is not None:
        topic.order = payload.order
    if payload.notes is not None:
        topic.notes = payload.notes
    if payload.cheat_sheet is not None:
        topic.cheat_sheet = payload.cheat_sheet
    if payload.official_documentation is not None:
        topic.official_documentation = payload.official_documentation

    if payload.youtube_videos is not None:
        topic.youtube_videos = payload.youtube_videos
        # Update persistent videos table
        try:
            v_list = json.loads(payload.youtube_videos)
            if isinstance(v_list, list):
                # Mark old videos as soft deleted
                db.query(Video).filter(Video.topic_id == topic.id).update({
                    Video.is_deleted: True,
                    Video.deleted_at: datetime.datetime.utcnow()
                })
                # Add/restore new videos
                for idx, v in enumerate(v_list):
                    url = v.get("url") if isinstance(v, dict) else str(v)
                    v_title = v.get("title", f"{topic.title} Video") if isinstance(v, dict) else f"{topic.title} Video"
                    if url:
                        vid = Video(
                            topic_id=topic.id,
                            roadmap_id=topic.roadmap_id,
                            career_id=topic.career_id,
                            title=v_title,
                            youtube_url=url,
                            display_order=idx + 1,
                            is_active=True,
                            is_deleted=False
                        )
                        db.add(vid)
        except Exception as ex:
            print(f"[VIDEO SYNC WARNING] {ex}")

    topic.is_admin_modified = True
    topic.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(topic)

    log_audit_event(
        db, admin,
        action="MODULE_UPDATED",
        entity_type="module",
        entity_id=topic.id,
        old_data=old_data,
        new_data={"title": topic.title, "difficulty": topic.difficulty, "order": topic.order}
    )
    create_roadmap_version_snapshot(db, topic.roadmap_id, admin, f"Updated module: {topic.title}")

    return {"message": "Module updated successfully", "module": {"id": topic.id, "title": topic.title}}


@router.delete("/modules/{module_id}")
def delete_module(module_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Soft delete a module (Admin only). Preserves student completion history."""
    topic = db.query(Topic).filter(Topic.id == module_id, Topic.is_deleted == False).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Module not found")

    old_data = {"title": topic.title, "roadmap_id": topic.roadmap_id}

    topic.is_deleted = True
    topic.deleted_at = datetime.datetime.utcnow()

    # Soft delete related videos
    db.query(Video).filter(Video.topic_id == module_id).update({
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
    create_roadmap_version_snapshot(db, topic.roadmap_id, admin, f"Deleted module: {topic.title}")

    return {"message": "Module soft-deleted successfully", "id": module_id}


# =======================================================
# 3. VIDEOS APIS
# =======================================================
@router.get("/videos")
def list_videos(
    topic_id: Optional[int] = None,
    career_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Fetch persistent videos directly from MySQL videos table."""
    query = db.query(Video).filter(Video.is_deleted == False, Video.is_active == True)
    if topic_id:
        query = query.filter(Video.topic_id == topic_id)
    if career_id:
        query = query.filter(Video.career_id == career_id)

    videos = query.order_by(Video.display_order).all()
    return {
        "videos": [{
            "id": v.id,
            "topic_id": v.topic_id,
            "roadmap_id": v.roadmap_id,
            "career_id": v.career_id,
            "title": v.title,
            "youtube_url": v.youtube_url,
            "description": v.description,
            "thumbnail_url": v.thumbnail_url,
            "display_order": v.display_order,
            "created_at": v.created_at,
            "updated_at": v.updated_at
        } for v in videos]
    }


@router.get("/videos/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    """Fetch single video by ID."""
    v = db.query(Video).filter(Video.id == video_id, Video.is_deleted == False).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "id": v.id,
        "topic_id": v.topic_id,
        "roadmap_id": v.roadmap_id,
        "career_id": v.career_id,
        "title": v.title,
        "youtube_url": v.youtube_url,
        "description": v.description,
        "thumbnail_url": v.thumbnail_url,
        "display_order": v.display_order,
        "is_active": v.is_active,
        "created_at": v.created_at,
        "updated_at": v.updated_at
    }


@router.post("/videos")
def create_video(payload: VideoCreateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Create a persistent video record in MySQL (Admin only)."""
    vid = Video(
        topic_id=payload.topic_id,
        roadmap_id=payload.roadmap_id,
        career_id=payload.career_id,
        title=payload.title,
        youtube_url=payload.youtube_url,
        description=payload.description,
        thumbnail_url=payload.thumbnail_url,
        video_type=payload.video_type or "tutorial",
        display_order=payload.display_order or 1,
        is_active=payload.is_active if payload.is_active is not None else True,
        is_deleted=False
    )
    db.add(vid)
    db.commit()
    db.refresh(vid)

    log_audit_event(
        db, admin,
        action="VIDEO_CREATED",
        entity_type="video",
        entity_id=vid.id,
        new_data={"title": vid.title, "youtube_url": vid.youtube_url, "topic_id": vid.topic_id}
    )

    return {"message": "Video created successfully", "video": {"id": vid.id, "title": vid.title, "youtube_url": vid.youtube_url}}


@router.put("/videos/{video_id}")
def update_video(video_id: int, payload: VideoUpdateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Update video details (Admin only)."""
    vid = db.query(Video).filter(Video.id == video_id, Video.is_deleted == False).first()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")

    old_data = {"title": vid.title, "youtube_url": vid.youtube_url}

    if payload.title is not None:
        vid.title = payload.title
    if payload.youtube_url is not None:
        vid.youtube_url = payload.youtube_url
    if payload.description is not None:
        vid.description = payload.description
    if payload.thumbnail_url is not None:
        vid.thumbnail_url = payload.thumbnail_url
    if payload.video_type is not None:
        vid.video_type = payload.video_type
    if payload.display_order is not None:
        vid.display_order = payload.display_order
    if payload.is_active is not None:
        vid.is_active = payload.is_active

    vid.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(vid)

    log_audit_event(
        db, admin,
        action="VIDEO_UPDATED",
        entity_type="video",
        entity_id=vid.id,
        old_data=old_data,
        new_data={"title": vid.title, "youtube_url": vid.youtube_url}
    )

    return {"message": "Video updated successfully", "video": {"id": vid.id, "title": vid.title, "youtube_url": vid.youtube_url}}


@router.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Soft delete a video (Admin only)."""
    vid = db.query(Video).filter(Video.id == video_id, Video.is_deleted == False).first()
    if not vid:
        raise HTTPException(status_code=404, detail="Video not found")

    old_data = {"title": vid.title, "youtube_url": vid.youtube_url}

    vid.is_deleted = True
    vid.deleted_at = datetime.datetime.utcnow()
    db.commit()

    log_audit_event(
        db, admin,
        action="VIDEO_DELETED",
        entity_type="video",
        entity_id=vid.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(vid.deleted_at)}
    )

    return {"message": "Video soft-deleted successfully", "id": video_id}


# =======================================================
# 4. QUESTIONS APIS
# =======================================================
@router.get("/questions/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Fetch single MCQ question details."""
    q = db.query(Question).filter(Question.id == question_id, Question.is_deleted == False).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    return {
        "id": q.id,
        "quiz_id": q.quiz_id,
        "question_text": q.question_text,
        "option_a": q.option_a,
        "option_b": q.option_b,
        "option_c": q.option_c,
        "option_d": q.option_d,
        "correct_option": q.correct_option,
        "explanation": q.explanation
    }


@router.put("/questions/{question_id}")
def update_question(question_id: int, payload: QuestionUpdateSchema, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Update MCQ question details (Admin only)."""
    q = db.query(Question).filter(Question.id == question_id, Question.is_deleted == False).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    old_data = {"question_text": q.question_text, "correct_option": q.correct_option}

    if payload.question_text is not None:
        q.question_text = payload.question_text
    if payload.option_a is not None:
        q.option_a = payload.option_a
    if payload.option_b is not None:
        q.option_b = payload.option_b
    if payload.option_c is not None:
        q.option_c = payload.option_c
    if payload.option_d is not None:
        q.option_d = payload.option_d
    if payload.correct_option is not None:
        q.correct_option = payload.correct_option.upper()
    if payload.explanation is not None:
        q.explanation = payload.explanation

    db.commit()
    db.refresh(q)

    log_audit_event(
        db, admin,
        action="QUESTION_UPDATED",
        entity_type="question",
        entity_id=q.id,
        old_data=old_data,
        new_data={"question_text": q.question_text, "correct_option": q.correct_option}
    )

    return {"message": "Question updated successfully", "question": {"id": q.id, "question_text": q.question_text}}


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Soft delete a question (Admin only)."""
    q = db.query(Question).filter(Question.id == question_id, Question.is_deleted == False).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    old_data = {"question_text": q.question_text, "quiz_id": q.quiz_id}

    q.is_deleted = True
    q.deleted_at = datetime.datetime.utcnow()
    db.commit()

    log_audit_event(
        db, admin,
        action="QUESTION_DELETED",
        entity_type="question",
        entity_id=q.id,
        old_data=old_data,
        new_data={"is_deleted": True, "deleted_at": str(q.deleted_at)}
    )

    return {"message": "Question soft-deleted successfully", "id": question_id}


# =======================================================
# 5. AUDIT LOGS & ROADMAP VERSIONS APIS
# =======================================================
@router.get("/audit-logs")
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieve historical audit logs (Admin only)."""
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return {
        "audit_logs": [{
            "id": l.id,
            "user_id": l.user_id,
            "user_name": l.user_name,
            "user_role": l.user_role,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "old_data": l.old_data,
            "new_data": l.new_data,
            "created_at": l.created_at
        } for l in logs]
    }


@router.get("/roadmap-versions/{roadmap_id}")
def list_roadmap_versions(
    roadmap_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieve version history for a given roadmap milestone."""
    versions = db.query(RoadmapVersion).filter(
        RoadmapVersion.roadmap_id == roadmap_id
    ).order_by(RoadmapVersion.version_number.desc()).all()

    return {
        "versions": [{
            "id": v.id,
            "roadmap_id": v.roadmap_id,
            "version_number": v.version_number,
            "created_by": v.created_by,
            "change_summary": v.change_summary,
            "created_at": v.created_at
        } for v in versions]
    }
