from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Resource, Topic
from app.utils.auth import get_current_user

router = APIRouter(prefix="/resources", tags=["Resource Library"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def get_resources_page(
    request: Request,
    q: str = "",
    type_filter: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Resource).join(Topic)
    if q:
        query = query.filter(Resource.title.contains(q) | Resource.content.contains(q) | Topic.title.contains(q))
    if type_filter and type_filter != "All":
        query = query.filter(Resource.type == type_filter)

    resources = query.all()

    # Seed resources ONLY if entire Resource table is genuinely empty
    if db.query(Resource).count() == 0:
        topics = db.query(Topic).limit(5).all()
        seed_res = []
        for t in topics:
            seed_res.append(Resource(topic_id=t.id, type="video", title=f"{t.title} Video Tutorial", url="https://www.youtube.com/watch?v=vLqTf2b6GZw", content="Comprehensive video guide."))
            seed_res.append(Resource(topic_id=t.id, type="doc", title=f"{t.title} Official Documentation", url="https://docs.python.org/3/", content="Official language documentation."))
            seed_res.append(Resource(topic_id=t.id, type="cheatsheet", title=f"{t.title} Quick Cheat Sheet", url="", content="Key syntax and quick reference snippet."))
        if seed_res:
            db.add_all(seed_res)
            db.commit()
            resources = query.all()

    return templates.TemplateResponse(
        "resources/index.html",
        {
            "request": request,
            "user": current_user,
            "resources": resources,
            "search_query": q,
            "active_type": type_filter
        }
    )
