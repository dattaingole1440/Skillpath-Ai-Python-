from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, StudentNote, ResourceBookmark
from app.utils.auth import get_current_user

router = APIRouter(tags=["Notes & Bookmarks"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/notes", response_class=HTMLResponse)
def get_notes_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notes = db.query(StudentNote).filter(StudentNote.student_id == current_user.id).order_by(StudentNote.updated_at.desc()).all()
    bookmarks = db.query(ResourceBookmark).filter(ResourceBookmark.student_id == current_user.id).order_by(ResourceBookmark.created_at.desc()).all()

    return templates.TemplateResponse(
        "notes/index.html",
        {
            "request": request,
            "user": current_user,
            "notes": notes,
            "bookmarks": bookmarks
        }
    )

@router.post("/api/notes")
def create_or_update_note(
    title: str = Form(...),
    content: str = Form(...),
    note_id: int = Form(None),
    is_private: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if note_id:
        note = db.query(StudentNote).filter(StudentNote.id == note_id, StudentNote.student_id == current_user.id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found.")
        note.title = title
        note.content = content
        note.is_private = is_private
        db.commit()
        return JSONResponse({"status": "success", "message": "Note updated successfully!"})
    else:
        note = StudentNote(
            student_id=current_user.id,
            title=title,
            content=content,
            is_private=is_private
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return JSONResponse({"status": "success", "note_id": note.id, "message": "Note created successfully!"})

@router.delete("/api/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(StudentNote).filter(StudentNote.id == note_id, StudentNote.student_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    db.delete(note)
    db.commit()
    return JSONResponse({"status": "success", "message": "Note deleted."})

@router.post("/api/bookmarks")
def add_bookmark(
    resource_type: str = Form(...),
    resource_id: int = Form(...),
    title: str = Form(...),
    url: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmark = ResourceBookmark(
        student_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
        title=title,
        url=url
    )
    db.add(bookmark)
    db.commit()
    return JSONResponse({"status": "success", "message": "Bookmarked resource!"})
