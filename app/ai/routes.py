import logging
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.utils.auth import get_current_user
from app.models.models import User
from app.ai.service import gemini_chat_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Assistant"])
templates = Jinja2Templates(directory="app/templates")

class ChatRequest(BaseModel):
    message: str

@router.post("/api/ai/chat")
def api_ai_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Sends the student's question to the Google Gemini API.
    Does not use placeholders or hardcoded responses.
    On failure, returns the actual Gemini API error.
    """
    try:
        reply = gemini_chat_service.get_chat_reply(current_user.id, payload.message)
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Error in api_ai_chat: {e}")
        # Ensure we return the actual error message
        err_msg = getattr(e, "message", str(e))
        if hasattr(e, "detail"):
            err_msg = e.detail
        raise HTTPException(status_code=500, detail=err_msg)

@router.post("/api/ai/chat/reset")
def reset_ai_chat(
    current_user: User = Depends(get_current_user)
):
    """
    Resets the conversation history for the current user.
    """
    try:
        gemini_chat_service.reset_chat(current_user.id)
        return {"status": "success", "message": "Conversation history reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat", response_class=HTMLResponse)
def get_chat_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Renders the premium dedicated AI Coding Tutor page.
    """
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user})

@router.post("/ai/chat")
def ai_chat_assistant(
    prompt: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Legacy Form-based endpoint for backward compatibility.
    """
    try:
        reply = gemini_chat_service.get_chat_reply(current_user.id, prompt)
        return {"response": reply}
    except Exception as e:
        logger.error(f"Error in legacy ai_chat_assistant: {e}")
        err_msg = getattr(e, "message", str(e))
        if hasattr(e, "detail"):
            err_msg = e.detail
        raise HTTPException(status_code=500, detail=err_msg)

