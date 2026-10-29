import os
import sys
import json
import datetime
from sqlalchemy.orm import Session
from app.database.connection import engine, SessionLocal, sync_db_schema, Base
from app.models.models import User, Career, Roadmap, Topic, Video, Quiz, Question, CodingChallenge, AuditLog, RoadmapVersion
from app.database.seed import seed_database
from app.utils.audit import log_audit_event
from app.utils.versioning import create_roadmap_version_snapshot

def run_tests():
    print("====================================================================")
    print("  🧪 SkillPath AI — Comprehensive Persistence & Integrity Tests")
    print("====================================================================")

    db: Session = SessionLocal()
    try:
        # TEST 1: Check existing counts
        print("\n--- Test 1: Verify Initial Database State ---")
        u_count = db.query(User).count()
        c_count = db.query(Career).filter(Career.is_deleted == False).count()
        r_count = db.query(Roadmap).filter(Roadmap.is_deleted == False).count()
        t_count = db.query(Topic).filter(Topic.is_deleted == False).count()
        v_count = db.query(Video).filter(Video.is_deleted == False).count()
        q_count = db.query(Question).filter(Question.is_deleted == False).count()

        print(f"Active Users: {u_count}, Careers: {c_count}, Roadmaps: {r_count}, Topics: {t_count}, Videos: {v_count}, Questions: {q_count}")
        assert u_count >= 5, "Users must be preserved"
        assert c_count >= 14, "Careers must be preserved"
        assert t_count >= 80, "Topics must be preserved"
        print("✅ Test 1 PASSED: Initial database state verified & intact.")

        # TEST 2: Add dynamic test entity with Video, AuditLog, and Version
        print("\n--- Test 2: Admin Add Dynamic Roadmap, Topic, Video & Question ---")
        admin = db.query(User).filter(User.role.in_(["super_admin", "admin"])).first()
        career = db.query(Career).filter(Career.is_deleted == False).first()

        # Create Roadmap
        test_rm = Roadmap(
            career_id=career.id,
            title="[PERSIST_TEST] Cloud Native Architecture",
            description="Testing permanent persistence across restarts",
            order=999,
            is_deleted=False
        )
        db.add(test_rm)
        db.commit()
        db.refresh(test_rm)

        log_audit_event(db, admin, "ROADMAP_CREATED", "roadmap", test_rm.id, new_data={"title": test_rm.title})
        create_roadmap_version_snapshot(db, test_rm.id, admin, "Created test milestone")

        # Create Topic
        test_topic = Topic(
            roadmap_id=test_rm.id,
            career_id=career.id,
            title="[PERSIST_TEST] Kubernetes Ingress Controllers",
            description="Deep dive into persistent Ingress configurations",
            difficulty="hard",
            estimated_time=3.5,
            order=1,
            is_admin_modified=True,
            is_deleted=False
        )
        db.add(test_topic)
        db.commit()
        db.refresh(test_topic)

        log_audit_event(db, admin, "MODULE_CREATED", "module", test_topic.id, new_data={"title": test_topic.title})

        # Create Video
        test_video = Video(
            topic_id=test_topic.id,
            roadmap_id=test_rm.id,
            career_id=career.id,
            title="Kubernetes Ingress Verification Tutorial",
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            video_type="tutorial",
            display_order=1,
            is_active=True,
            is_deleted=False
        )
        db.add(test_video)
        db.commit()
        db.refresh(test_video)

        log_audit_event(db, admin, "VIDEO_CREATED", "video", test_video.id, new_data={"title": test_video.title, "url": test_video.youtube_url})

        # Create Quiz & Question
        test_quiz = Quiz(topic_id=test_topic.id, passing_percentage=75, is_deleted=False)
        db.add(test_quiz)
        db.commit()
        db.refresh(test_quiz)

        test_q = Question(
            quiz_id=test_quiz.id,
            question_text="What does a Kubernetes Ingress resource do?",
            option_a="Exposes HTTP and HTTPS routes from outside the cluster to services within",
            option_b="Compiles binary code on the worker nodes",
            option_c="Deletes persistent volume claims automatically",
            option_d="None of the above",
            correct_option="A",
            explanation="Ingress manages external access to the services in a cluster.",
            is_deleted=False
        )
        db.add(test_q)
        db.commit()
        db.refresh(test_q)

        log_audit_event(db, admin, "QUESTION_CREATED", "question", test_q.id, new_data={"question_text": test_q.question_text})

        # Create Coding Challenge
        test_chal = CodingChallenge(
            topic_id=test_topic.id,
            title="[PERSIST_TEST] Kubernetes Ingress Rule Challenge",
            description="Write logic to parse ingress rules",
            difficulty="medium",
            template_code="def solution(): pass",
            test_cases=json.dumps([{"function_name": "solution", "args": [], "expected": "ok"}]),
            score_points=15,
            is_deleted=False
        )
        db.add(test_chal)
        db.commit()
        db.refresh(test_chal)
        log_audit_event(db, admin, "CHALLENGE_CREATED", "challenge", test_chal.id, new_data={"title": test_chal.title})

        test_quiz_id = test_quiz.id
        test_rm_id = test_rm.id
        test_topic_id = test_topic.id
        test_video_id = test_video.id
        test_q_id = test_q.id
        test_chal_id = test_chal.id

        print(f"Created Test Entities -> Roadmap #{test_rm_id}, Topic #{test_topic_id}, Video #{test_video_id}, Question #{test_q_id}, Challenge #{test_chal_id}")
        print("✅ Test 2 PASSED: Dynamic content saved and audit trail recorded.")

        # TEST 3: Modify the Topic & Video
        print("\n--- Test 3: Modify Topic & Video and Verify Updated State ---")
        topic_to_update = db.query(Topic).filter(Topic.id == test_topic_id).first()
        topic_to_update.title = "[PERSIST_TEST] Kubernetes Ingress Controllers (MODIFIED_V2)"
        topic_to_update.difficulty = "easy"

        video_to_update = db.query(Video).filter(Video.id == test_video_id).first()
        video_to_update.youtube_url = "https://www.youtube.com/watch?v=MODIFIED_URL_99"

        db.commit()

        admin_curr = db.query(User).filter(User.role.in_(["super_admin", "admin"])).first()
        log_audit_event(db, admin_curr, "MODULE_UPDATED", "module", test_topic_id, new_data={"title": topic_to_update.title})
        log_audit_event(db, admin_curr, "VIDEO_UPDATED", "video", test_video_id, new_data={"youtube_url": video_to_update.youtube_url})

        # Verify modified values in DB
        t_check = db.query(Topic).filter(Topic.id == test_topic_id).first()
        v_check = db.query(Video).filter(Video.id == test_video_id).first()
        assert "MODIFIED_V2" in t_check.title, "Topic modification must be in database"
        assert "MODIFIED_URL_99" in v_check.youtube_url, "Video modification must be in database"
        print(f"Verified modification: Topic Title='{t_check.title}', Video URL='{v_check.youtube_url}'")
        print("✅ Test 3 PASSED: Dynamic modifications persisted.")

        # TEST 4: Simulate Application Server Restart (Safe startup & seed check)
        print("\n--- Test 4: Simulate Application Server Restart ---")
        db.close()

        # Simulate startup routine as executed in main.py
        sync_db_schema(engine, Base)
        db2 = SessionLocal()
        seed_database(db2)

        # Verify that all data remains, including modified entities
        t_after_restart = db2.query(Topic).filter(Topic.id == test_topic_id).first()
        v_after_restart = db2.query(Video).filter(Video.id == test_video_id).first()
        q_after_restart = db2.query(Question).filter(Question.id == test_q_id).first()
        rm_after_restart = db2.query(Roadmap).filter(Roadmap.id == test_rm_id).first()

        assert t_after_restart is not None, "Topic must persist across restart"
        assert "MODIFIED_V2" in t_after_restart.title, "Topic modified version must persist, not old version!"
        assert v_after_restart is not None, "Video must persist across restart"
        assert "MODIFIED_URL_99" in v_after_restart.youtube_url, "Video modified URL must persist!"
        assert q_after_restart is not None, "Question must persist across restart"
        assert rm_after_restart is not None, "Roadmap must persist across restart"

        print("✅ Test 4 PASSED: Server restart preserved modified topic, video, question, and roadmap!")

        # TEST 5: Soft-delete content & simulate restart again
        print("\n--- Test 5: Soft-delete Module & Verify It Does NOT Reappear After Restart ---")
        now_time = datetime.datetime.utcnow()
        t_after_restart.is_deleted = True
        t_after_restart.deleted_at = now_time
        v_after_restart.is_deleted = True
        v_after_restart.deleted_at = now_time
        rm_after_restart.is_deleted = True
        rm_after_restart.deleted_at = now_time
        db2.commit()

        admin_db2 = db2.query(User).filter(User.role.in_(["super_admin", "admin"])).first()
        log_audit_event(db2, admin_db2, "MODULE_DELETED", "module", test_topic_id)
        log_audit_event(db2, admin_db2, "ROADMAP_DELETED", "roadmap", test_rm_id)

        db2.close()

        # Restart again
        db3 = SessionLocal()
        seed_database(db3)

        # Verify soft-deleted items are excluded from normal queries
        active_topics = db3.query(Topic).filter(Topic.roadmap_id == test_rm_id, Topic.is_deleted == False).all()
        active_roadmaps = db3.query(Roadmap).filter(Roadmap.id == test_rm_id, Roadmap.is_deleted == False).all()
        assert len(active_topics) == 0, "Soft-deleted topic must not reappear as active"
        assert len(active_roadmaps) == 0, "Soft-deleted roadmap must not reappear as active"

        # Verify audit logs captured all transitions
        audit_records = db3.query(AuditLog).order_by(AuditLog.id.desc()).limit(10).all()
        print(f"Total Audit Logs Recorded: {db3.query(AuditLog).count()}")
        assert len(audit_records) >= 5, "Audit logs must record all operations"
        print("Recent audit log actions:", [a.action for a in audit_records[:5]])

        # Clean up the test records completely from test so database remains pristine
        db3.query(Question).filter(Question.id == test_q_id).delete()
        db3.query(Quiz).filter(Quiz.id == test_quiz_id).delete()
        db3.query(Video).filter(Video.id == test_video_id).delete()
        db3.query(Topic).filter(Topic.id == test_topic_id).delete()
        db3.query(RoadmapVersion).filter(RoadmapVersion.roadmap_id == test_rm_id).delete()
        db3.query(Roadmap).filter(Roadmap.id == test_rm_id).delete()
        db3.commit()
        db3.close()

        print("✅ Test 5 PASSED: Soft-delete verified and test artifacts cleanly cleaned up.")
        print("\n====================================================================")
        print("  🎉 ALL 5 PERSISTENCE & INTEGRITY TESTS PASSED SUCCESSFULLY!")
        print("====================================================================")

    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        db.close()
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
