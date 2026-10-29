from typing import List
from fastapi import Depends, HTTPException, status
from app.utils.auth import get_current_user
from app.models.models import User

def require_roles(allowed_roles: List[str]):
    """
    FastAPI dependency factory to enforce user role restrictions.
    Allows roles specified in allowed_roles.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "student").lower()
        
        # Mapping alias & legacy support
        if user_role == "admin":
            user_role = "super_admin"
        elif user_role in ["college_admin", "clg_admin"]:
            user_role = "principal"
            
        allowed = [r.lower() for r in allowed_roles]
        
        if user_role not in allowed and "super_admin" not in allowed and current_user.role not in ["super_admin", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["teacher", "hod", "principal", "college_admin", "super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher, HOD, Principal, or Administrator privileges required."
        )
    return current_user

def require_hod(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["hod", "principal", "college_admin", "super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Head of Department, Principal, or Administrator privileges required."
        )
    return current_user

def require_principal(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["principal", "college_admin", "super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal or Administrator privileges required."
        )
    return current_user

# Legacy alias compatibility
require_college_admin = require_principal

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Administrator privileges required."
        )
    return current_user


