import json
import datetime
from sqlalchemy.orm import Session
from app.models.models import Roadmap, RoadmapVersion, Topic, Video, User

def create_roadmap_version_snapshot(
    db: Session,
    roadmap_id: int,
    user: User = None,
    change_summary: str = "Roadmap configuration update"
) -> RoadmapVersion:
    """
    Captures a full JSON snapshot of the roadmap, its topics, and videos,
    and saves it to the roadmap_versions table with an incremented version number.
    Ensures that historical state is never lost and student progress remains consistent.
    """
    try:
        roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
        if not roadmap:
            return None

        # Determine next version number
        last_version = db.query(RoadmapVersion).filter(
            RoadmapVersion.roadmap_id == roadmap_id
        ).order_by(RoadmapVersion.version_number.desc()).first()

        next_version = (last_version.version_number + 1) if last_version else 1

        # Fetch active topics
        topics = db.query(Topic).filter(
            Topic.roadmap_id == roadmap_id,
            Topic.is_deleted == False
        ).order_by(Topic.order).all()

        topic_data_list = []
        for t in topics:
            videos = db.query(Video).filter(
                Video.topic_id == t.id,
                Video.is_deleted == False
            ).all()

            video_list = [{
                "id": v.id,
                "title": v.title,
                "youtube_url": v.youtube_url,
                "display_order": v.display_order
            } for v in videos]

            topic_data_list.append({
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "order": t.order,
                "difficulty": t.difficulty,
                "estimated_time": t.estimated_time,
                "videos": video_list
            })

        snapshot = {
            "roadmap_id": roadmap.id,
            "career_id": roadmap.career_id,
            "title": roadmap.title,
            "description": roadmap.description,
            "order": roadmap.order,
            "topics": topic_data_list,
            "captured_at": datetime.datetime.utcnow().isoformat()
        }

        version_record = RoadmapVersion(
            career_id=roadmap.career_id,
            roadmap_id=roadmap.id,
            version_number=next_version,
            created_by=user.name if user and hasattr(user, "name") else "Administrator",
            change_summary=change_summary,
            snapshot_data=json.dumps(snapshot, default=str),
            created_at=datetime.datetime.utcnow()
        )
        db.add(version_record)
        db.commit()
        db.refresh(version_record)
        return version_record
    except Exception as e:
        print(f"[VERSIONING ERROR] Failed to create roadmap version snapshot: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return None
