import json
import datetime
from sqlalchemy.orm import Session
from app.models.models import AuditLog, User

def log_audit_event(
    db: Session,
    user: User = None,
    action: str = "UNKNOWN_ACTION",
    entity_type: str = "general",
    entity_id: int = None,
    old_data: dict = None,
    new_data: dict = None
) -> AuditLog:
    """
    Safely records an audit entry into the persistent audit_logs table.
    Tracks changes to roadmaps, milestones, modules, videos, and questions.
    """
    try:
        user_id = user.id if user and hasattr(user, "id") else None
        user_name = user.name if user and hasattr(user, "name") else "System/Admin"
        user_role = user.role if user and hasattr(user, "role") else "system"

        old_json = json.dumps(old_data, default=str) if old_data else None
        new_json = json.dumps(new_data, default=str) if new_data else None

        audit = AuditLog(
            user_id=user_id,
            user_name=user_name,
            user_role=user_role,
            action=action.upper(),
            entity_type=entity_type.lower(),
            entity_id=entity_id,
            old_data=old_json,
            new_data=new_json,
            created_at=datetime.datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to record audit event: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None
