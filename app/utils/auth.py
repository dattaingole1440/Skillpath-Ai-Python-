from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.models.models import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extracts token from either:
    1. Authorization header (Bearer token)
    2. 'access_token' cookie (Used in Jinja2 template flows)
    """
    # 1. Check cookies
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        # Check if the token has the "Bearer " prefix in cookie, strip it
        if cookie_token.startswith("Bearer "):
            return cookie_token[7:]
        return cookie_token

    # 2. Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = get_token_from_request(request)
    
    # Renders login redirect for page renders, or raw JSON exception for API requests
    credentials_exception = HTTPException(
        status_code=status.HTTP_410_GONE, # We can use 401, but let's handle redirects in middleware or routes
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        # If it's a page render request (accepts HTML), we redirect. We throw a custom HTTP error or redirect directly.
        # Let's raise HTTP 401, and our main app exception handler will redirect to login page.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
        
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token details")
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")
        
    return user

def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Optional user fetch - does not raise HTTP 401 exceptions if user is unauthenticated"""
    try:
        return get_current_user(request, db)
    except Exception:
        return None

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Super Administrator privileges required."
        )
    return current_user
