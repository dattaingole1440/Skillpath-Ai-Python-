from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, ForumPost, ForumComment, ForumLike, ActivityLog
from app.utils.auth import get_current_user

router = APIRouter(prefix="/forum", tags=["Discussion Forum"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_forum_page(
    request: Request,
    search: str = "",
    category: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ForumPost)
    if search:
        query = query.filter(ForumPost.title.contains(search) | ForumPost.content.contains(search))
    if category and category != "All":
        query = query.filter(ForumPost.category == category)

    posts = query.order_by(ForumPost.created_at.desc()).all()

    return templates.TemplateResponse(
        "forum/index.html",
        {
            "request": request,
            "user": current_user,
            "posts": posts,
            "search_query": search,
            "active_category": category
        }
    )

@router.get("/post/{post_id}", response_class=HTMLResponse)
def get_post_detail(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.views += 1
    db.commit()

    comments = db.query(ForumComment).filter(ForumComment.post_id == post_id).order_by(ForumComment.is_best_answer.desc(), ForumComment.created_at).all()

    return templates.TemplateResponse(
        "forum/post.html",
        {
            "request": request,
            "user": current_user,
            "post": post,
            "comments": comments
        }
    )

@router.post("/create")
def create_forum_post(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("General"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = ForumPost(
        student_id=current_user.id,
        title=title,
        content=content,
        category=category
    )
    db.add(post)
    current_user.xp += 10
    db.commit()
    db.refresh(post)

    return JSONResponse({"status": "success", "post_id": post.id})

@router.post("/post/{post_id}/comment")
def add_forum_comment(
    post_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    comment = ForumComment(
        post_id=post_id,
        student_id=current_user.id,
        content=content
    )
    db.add(comment)
    current_user.xp += 15
    db.commit()

    return JSONResponse({"status": "success", "message": "Answer submitted!"})

@router.post("/comment/{comment_id}/like")
def like_forum_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(ForumComment).filter(ForumComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    existing_like = db.query(ForumLike).filter(ForumLike.comment_id == comment_id, ForumLike.student_id == current_user.id).first()
    if existing_like:
        db.delete(existing_like)
        comment.likes_count = max(0, comment.likes_count - 1)
        db.commit()
        return JSONResponse({"status": "unliked", "likes": comment.likes_count})
    else:
        like = ForumLike(comment_id=comment_id, student_id=current_user.id)
        db.add(like)
        comment.likes_count += 1
        db.commit()
        return JSONResponse({"status": "liked", "likes": comment.likes_count})

@router.post("/comment/{comment_id}/best-answer")
def mark_best_answer(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(ForumComment).filter(ForumComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    post = db.query(ForumPost).filter(ForumPost.id == comment.post_id).first()
    if post.student_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only post author can select best answer.")

    # Reset existing best answers
    db.query(ForumComment).filter(ForumComment.post_id == post.id).update({"is_best_answer": False})
    
    comment.is_best_answer = True
    post.is_resolved = True
    post.best_answer_id = comment.id
    db.commit()

    return JSONResponse({"status": "success", "message": "Marked as best answer!"})
