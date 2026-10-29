import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Date, Table
from sqlalchemy.orm import relationship
from app.database.connection import Base

student_careers = Table(
    "student_careers",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("career_id", Integer, ForeignKey("careers.id", ondelete="CASCADE"), primary_key=True)
)

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    logo = Column(String(255), nullable=True, default="https://cdn-icons-png.flaticon.com/512/2997/2997295.png")
    address = Column(Text, nullable=True)
    contact_email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    departments = relationship("Department", back_populates="college", cascade="all, delete-orphan")
    users = relationship("User", back_populates="college")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False)
    hod_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    college = relationship("College", back_populates="departments")
    semesters = relationship("Semester", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")
    subjects = relationship("Subject", back_populates="department", cascade="all, delete-orphan")


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    year_label = Column(String(50), nullable=False) # e.g. 2025-2026
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=True)


class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False) # 1, 2, ..., 8
    name = Column(String(50), nullable=False) # Semester 1, Semester 2

    # Relationships
    department = relationship("Department", back_populates="semesters")
    divisions = relationship("Division", back_populates="semester", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="semester", cascade="all, delete-orphan")


class Division(Base):
    __tablename__ = "divisions"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False) # Division A, Division B

    # Relationships
    semester = relationship("Semester", back_populates="divisions")
    users = relationship("User", back_populates="division")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    code = Column(String(50), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="subjects")
    semester = relationship("Semester", back_populates="subjects")
    teacher = relationship("User", foreign_keys=[teacher_id])
    roadmap = relationship("Roadmap")
    assignments = relationship("Assignment", back_populates="subject", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="student") # super_admin, college_admin, hod, teacher, student, admin
    profile_photo = Column(String(255), nullable=True, default="https://cdn-icons-png.flaticon.com/512/3135/3135715.png")
    
    # LMS Organization Foreign Keys
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="SET NULL"), nullable=True)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True)
    roll_number = Column(String(50), nullable=True)
    employee_id = Column(String(50), nullable=True)
    phone_number = Column(String(30), nullable=True)

    current_career_id = Column(Integer, ForeignKey("careers.id", ondelete="SET NULL"), nullable=True)
    daily_streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)
    quiz_avg = Column(Float, default=0.0)
    coding_avg = Column(Float, default=0.0)
    learning_hours = Column(Float, default=0.0)
    xp = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    level = Column(Integer, default=1)
    rank = Column(String(50), default="Beginner")
    language_preference = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    college = relationship("College", back_populates="users")
    department = relationship("Department", back_populates="users")
    semester = relationship("Semester")
    division = relationship("Division", back_populates="users")

    current_career = relationship("Career", back_populates="students")
    enrolled_careers = relationship("Career", secondary=student_careers, back_populates="enrolled_students")
    progress = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")
    coding_submissions = relationship("CodingSubmission", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="student", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="student", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", foreign_keys="AttendanceRecord.student_id", back_populates="student", cascade="all, delete-orphan")
    activity_tracks = relationship("ActivityTrack", back_populates="student", cascade="all, delete-orphan")
    early_warnings = relationship("EarlyWarningAlert", foreign_keys="EarlyWarningAlert.student_id", back_populates="student", cascade="all, delete-orphan")
    placement_record = relationship("PlacementRecord", back_populates="student", uselist=False, cascade="all, delete-orphan")


class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=True)
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(30), default="theory") # coding, pdf, theory, project
    due_date = Column(DateTime, nullable=True)
    max_marks = Column(Integer, default=100)
    attachments = Column(Text, nullable=True) # JSON list or URL
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="assignments")
    teacher = relationship("User")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submission_text = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)
    code = Column(Text, nullable=True)
    marks_obtained = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="assignment_submissions")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, default=datetime.date.today, index=True)
    status = Column(String(20), default="Absent") # Present, Partial, Absent
    study_minutes = Column(Integer, default=0)
    is_manual_override = Column(Boolean, default=False)
    teacher_override_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    override_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="attendance_records")
    subject = relationship("Subject")


class ActivityTrack(Base):
    __tablename__ = "activity_tracks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), nullable=False) # login, logout, video_watch, pdf_read, quiz, coding, assignment, ai_chat, mock_interview
    duration_minutes = Column(Float, default=0.0)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Relationships
    student = relationship("User", back_populates="activity_tracks")


class EarlyWarningAlert(Base):
    __tablename__ = "early_warning_alerts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    risk_level = Column(String(20), default="medium") # low, medium, high, critical
    trigger_reason = Column(Text, nullable=False)
    ai_analysis = Column(Text, nullable=True)
    status = Column(String(20), default="open") # open, resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="early_warnings")
    teacher = relationship("User", foreign_keys=[teacher_id])


class TeacherNotification(Base):
    __tablename__ = "teacher_notifications"

    id = Column(Integer, primary_key=True, index=True)
    sender_teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50), default="general") # greeting, birthday, congratulations, warning, assignment_reminder, exam_reminder, placement_update
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    sender_teacher = relationship("User", foreign_keys=[sender_teacher_id])
    recipient_student = relationship("User", foreign_keys=[recipient_student_id])


class PlacementRecord(Base):
    __tablename__ = "placement_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    placement_score = Column(Float, default=0.0)
    coding_score = Column(Float, default=0.0)
    quiz_score = Column(Float, default=0.0)
    projects_score = Column(Float, default=0.0)
    attendance_score = Column(Float, default=0.0)
    resume_score = Column(Float, default=0.0)
    interview_score = Column(Float, default=0.0)
    roadmap_completion_score = Column(Float, default=0.0)
    ai_recommendations = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="placement_record")


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(150), nullable=True)
    icon = Column(String(100), nullable=True)
    badge = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    total_topics = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    students = relationship("User", back_populates="current_career")
    enrolled_students = relationship("User", secondary=student_careers, back_populates="enrolled_careers")
    roadmaps = relationship("Roadmap", back_populates="career", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="career", cascade="all, delete-orphan")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=1)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    career = relationship("Career", back_populates="roadmaps")
    topics = relationship("Topic", back_populates="roadmap", cascade="all, delete-orphan")
    versions = relationship("RoadmapVersion", back_populates="roadmap", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True) # Stored as JSON or line-separated text
    youtube_videos = Column(Text, nullable=True) # Stored as JSON array: [{"title": "...", "url": "..."}]
    official_documentation = Column(Text, nullable=True) # JSON array: [{"title": "...", "url": "..."}]
    notes = Column(Text, nullable=True)
    cheat_sheet = Column(Text, nullable=True)
    practice_questions = Column(Text, nullable=True) # JSON array
    mini_project = Column(Text, nullable=True) # JSON object
    difficulty = Column(String(20), default="medium") # easy, medium, hard
    estimated_time = Column(Float, default=1.0) # hours
    order = Column(Integer, default=1)
    is_admin_modified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    roadmap = relationship("Roadmap", back_populates="topics")
    resources = relationship("Resource", back_populates="topic", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")
    coding_challenges = relationship("CodingChallenge", back_populates="topic", cascade="all, delete-orphan")
    progress = relationship("StudentProgress", back_populates="topic", cascade="all, delete-orphan")
    videos_rel = relationship("Video", back_populates="topic", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="SET NULL"), nullable=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    youtube_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    video_type = Column(String(50), default="tutorial")
    display_order = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="videos_rel")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_name = Column(String(150), nullable=True)
    user_role = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    old_data = Column(Text, nullable=True)
    new_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class RoadmapVersion(Base):
    __tablename__ = "roadmap_versions"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=True)
    version_number = Column(Integer, default=1)
    created_by = Column(String(100), nullable=True)
    change_summary = Column(Text, nullable=True)
    snapshot_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    roadmap = relationship("Roadmap", back_populates="versions")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False) # video, doc, notes, cheatsheet
    title = Column(String(150), nullable=False)
    url = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="resources")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)
    passing_score = Column(Integer, default=70)
    passing_percentage = Column(Integer, default=70)
    is_admin_modified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(255), nullable=False)
    option_b = Column(String(255), nullable=False)
    option_c = Column(String(255), nullable=False)
    option_d = Column(String(255), nullable=False)
    correct_option = Column(String(1), nullable=False) # A, B, C, D
    explanation = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class CodingChallenge(Base):
    __tablename__ = "coding_challenges"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium") # easy, medium, hard
    template_code = Column(Text, nullable=True) # Starting code snippet
    language = Column(String(50), nullable=True)
    file_name = Column(String(100), nullable=True)
    lang_label = Column(String(50), nullable=True)
    fn_name = Column(String(100), nullable=True)
    test_cases = Column(Text, nullable=True) # JSON representing input and expected output
    score_points = Column(Integer, default=10)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="coding_challenges")
    submissions = relationship("CodingSubmission", back_populates="challenge", cascade="all, delete-orphan")


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="Locked") # Locked, Unlocked, Completed, Pending
    study_time_minutes = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="progress")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("coding_challenges.id", ondelete="CASCADE"), nullable=False)
    submitted_code = Column(Text, nullable=False)
    status = Column(String(20), default="failed") # passed, failed
    score_earned = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="coding_submissions")
    challenge = relationship("CodingChallenge", back_populates="submissions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False) # next_topic, revision, extra_practice, mini_project, advanced
    content = Column(Text, nullable=False) # The recommendation text details
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="recommendations")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    certificate_number = Column(String(100), unique=True, nullable=False)
    issue_date = Column(Date, default=datetime.date.today)
    file_path = Column(String(255), nullable=False)
    qr_code_path = Column(String(255), nullable=True)
    signature_path = Column(String(255), nullable=True)

    # Relationships
    student = relationship("User", back_populates="certificates")
    career = relationship("Career", back_populates="certificates")


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=datetime.date.today)
    study_time_minutes = Column(Integer, default=0)
    quiz_score = Column(Float, default=0.0)
    coding_score = Column(Float, default=0.0)
    topics_completed = Column(Integer, default=0)

    # Relationships
    student = relationship("User", back_populates="analytics")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(150), nullable=False) # login, view_topic, submit_quiz, submit_code, get_recommendation, etc.
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activity_logs")


# ==========================================
# 1. AI STUDY PLANNER MODELS
# ==========================================
class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hours_per_day = Column(Float, default=2.0)
    target_date = Column(Date, nullable=False)
    plan_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tasks = relationship("StudyTask", back_populates="plan", cascade="all, delete-orphan")


class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_date = Column(Date, nullable=False)
    hours_estimated = Column(Float, default=1.0)
    status = Column(String(20), default="pending") # pending, completed, missed
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    plan = relationship("StudyPlan", back_populates="tasks")


# ==========================================
# 2. AI DOUBT SOLVER CHAT HISTORY MODELS
# ==========================================
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), default="New Chat")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False) # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


# ==========================================
# 3. AI CODE REVIEWER MODEL
# ==========================================
class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(50), default="python")
    code = Column(Text, nullable=False)
    score = Column(Integer, default=0)
    bugs = Column(Text, nullable=True)
    complexity = Column(Text, nullable=True)
    readability = Column(Text, nullable=True)
    performance = Column(Text, nullable=True)
    security = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    improved_code = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ==========================================
# 5 & 6. AI RESUME BUILDER & ANALYZER MODELS
# ==========================================
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), default="My Resume")
    personal_info = Column(Text, nullable=True) # JSON string
    skills = Column(Text, nullable=True) # JSON string
    projects = Column(Text, nullable=True) # JSON string
    certificates = Column(Text, nullable=True) # JSON string
    achievements = Column(Text, nullable=True) # JSON string
    generated_ats_resume = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=True)
    ats_score = Column(Integer, default=0)
    missing_skills = Column(Text, nullable=True) # JSON list string
    improvement_suggestions = Column(Text, nullable=True)
    rating = Column(String(50), default="Good")
    recommended_skills = Column(Text, nullable=True)
    raw_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ==========================================
# 7. MOCK INTERVIEW SYSTEM MODELS
# ==========================================
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interview_type = Column(String(50), nullable=False) # Technical, HR, Behavioral, Coding
    status = Column(String(20), default="in_progress") # in_progress, completed
    overall_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    confidence_rating = Column(String(50), default="Moderate")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    qas = relationship("InterviewQA", back_populates="session", cascade="all, delete-orphan")


class InterviewQA(Base):
    __tablename__ = "interview_qas"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="qas")


# ==========================================
# 8 & 9. GAMIFICATION & DAILY CHALLENGES MODELS
# ==========================================
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="bi-trophy")
    category = Column(String(50), default="general")
    xp_reward = Column(Integer, default=50)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.datetime.utcnow)


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="bi-patch-check")
    min_level = Column(Integer, default=1)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime, default=datetime.datetime.utcnow)


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.date.today, index=True)
    challenge_type = Column(String(50), nullable=False) # quiz, coding, interview, revision
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    content_json = Column(Text, nullable=True) # JSON payload for question/code
    reward_xp = Column(Integer, default=30)
    reward_coins = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UserDailyChallenge(Base):
    __tablename__ = "user_daily_challenges"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("daily_challenges.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)


# ==========================================
# 10. PROJECTS MODEL
# ==========================================
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(String(30), nullable=False) # Beginner, Intermediate, Advanced
    category = Column(String(50), default="Web Development")
    tech_stack = Column(String(255), nullable=True)
    github_template = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UserProjectSubmission(Base):
    __tablename__ = "user_project_submissions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    github_url = Column(String(255), nullable=True)
    live_demo_url = Column(String(255), nullable=True)
    status = Column(String(20), default="submitted") # submitted, approved
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)


# ==========================================
# 12. DISCUSSION FORUM MODELS
# ==========================================
class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="General")
    views = Column(Integer, default=0)
    is_resolved = Column(Boolean, default=False)
    best_answer_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    comments = relationship("ForumComment", back_populates="post", cascade="all, delete-orphan")


class ForumComment(Base):
    __tablename__ = "forum_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, default=0)
    is_best_answer = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    post = relationship("ForumPost", back_populates="comments")


class ForumLike(Base):
    __tablename__ = "forum_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("forum_comments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


# ==========================================
# 13. STUDY GROUPS MODELS
# ==========================================
class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="General")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    max_members = Column(Integer, default=20)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    messages = relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")
    notes = relationship("GroupNote", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="member") # admin, member
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("StudyGroup", back_populates="members")


class GroupMessage(Base):
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("StudyGroup", back_populates="messages")


class GroupNote(Base):
    __tablename__ = "group_notes"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("StudyGroup", back_populates="notes")


# ==========================================
# 14 & 15. NOTES & BOOKMARKS MODELS
# ==========================================
class StudentNote(Base):
    __tablename__ = "student_notes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    is_private = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ResourceBookmark(Base):
    __tablename__ = "resource_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(String(50), nullable=False) # topic, project, resource, challenge
    resource_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ==========================================
# 17. NOTIFICATION SYSTEM MODEL
# ==========================================
class SystemNotification(Base):
    __tablename__ = "system_notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="general") # quiz, study, certificate, leaderboard, challenge, achievement
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ==========================================
# 18. EXTRA KNOWLEDGE IMPROVEMENT VIDEOS MODEL (TEACHER / HOD)
# ==========================================
class KnowledgeVideo(Base):
    __tablename__ = "knowledge_videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=False)
    category = Column(String(100), default="Knowledge Booster") # Knowledge Booster, Concept Mastery, Exam Prep, Industry Insights, Interview Prep
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_hod_recommended = Column(Boolean, default=False)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    teacher = relationship("User", foreign_keys=[teacher_id])
    subject = relationship("Subject", foreign_keys=[subject_id])
    topic = relationship("Topic", foreign_keys=[topic_id])


