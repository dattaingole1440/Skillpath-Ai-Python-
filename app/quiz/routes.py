import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import (
    User, Topic, StudentProgress, Quiz, Question, QuizAttempt, 
    CodingChallenge, CodingSubmission, ActivityLog, Analytics, Roadmap, Career
)
from app.utils.auth import get_current_user
from app.schemas import schemas

router = APIRouter(prefix="/quiz", tags=["Quiz"])
templates = Jinja2Templates(directory="app/templates")


def ensure_quiz_questions(db: Session, quiz: Quiz, topic: Topic):
    """
    Guarantees that every quiz has at least 3-5 high-yield multiple-choice questions
    based on the topic's subject matter so students never encounter an empty or broken quiz.
    """
    existing_count = db.query(Question).filter(Question.quiz_id == quiz.id, Question.is_deleted == False).count()
    if existing_count >= 3:
        return

    title_lower = (topic.title or "").lower()
    
    # Context-aware default question templates
    if "python" in title_lower or "variable" in title_lower or "syntax" in title_lower:
        default_qs = [
            {
                "text": f"In {topic.title}, which keyword is used to define a function in Python?",
                "a": "function", "b": "def", "c": "fun", "d": "define",
                "correct": "B", "exp": "The 'def' keyword is used to create user-defined functions in Python."
            },
            {
                "text": f"What is the output of type([1, 2, 3]) in {topic.title}?",
                "a": "<class 'list'>", "b": "<class 'array'>", "c": "<class 'tuple'>", "d": "<class 'set'>",
                "correct": "A", "exp": "Square brackets define a list object in Python."
            },
            {
                "text": f"Which of the following data structures in {topic.title} is immutable?",
                "a": "List", "b": "Dictionary", "c": "Tuple", "d": "Set",
                "correct": "C", "exp": "Tuples are immutable; their values cannot be modified after assignment."
            },
            {
                "text": f"In {topic.title}, which operator is used for floor division?",
                "a": "/", "b": "//", "c": "%", "d": "^",
                "correct": "B", "exp": "The '//' operator divides and truncates the decimal result to the nearest integer."
            }
        ]
    elif "java" in title_lower or "jvm" in title_lower or "spring" in title_lower or "maven" in title_lower or "gradle" in title_lower:
        default_qs = [
            {
                "text": f"In {topic.title}, which keyword is used to inherit a class in Java?",
                "a": "inherits", "b": "implements", "c": "extends", "d": "super",
                "correct": "C", "exp": "The 'extends' keyword is used to create a subclass that inherits from a parent class in Java."
            },
            {
                "text": f"What is the default value of an int instance variable in Java regarding {topic.title}?",
                "a": "null", "b": "0", "c": "undefined", "d": "-1",
                "correct": "B", "exp": "Primitive int variables are initialized to 0 by default in Java when declared as instance variables."
            },
            {
                "text": f"In {topic.title}, which collection interface does NOT allow duplicate elements?",
                "a": "List", "b": "Queue", "c": "Set", "d": "Deque",
                "correct": "C", "exp": "The Set interface guarantees uniqueness — no duplicate elements are permitted."
            },
            {
                "text": f"Which of the following is true about the 'final' keyword in Java as applied in {topic.title}?",
                "a": "A final class can be extended", "b": "A final method can be overridden",
                "c": "A final variable's value cannot be changed after initialization", "d": "final is used to create abstract classes",
                "correct": "C", "exp": "The 'final' keyword prevents variable reassignment, method overriding, and class inheritance."
            },
            {
                "text": f"In {topic.title}, what does JVM stand for?",
                "a": "Java Virtual Machine", "b": "Java Variable Manager",
                "c": "Java Version Module", "d": "Java Visual Monitor",
                "correct": "A", "exp": "JVM (Java Virtual Machine) executes Java bytecode and provides platform independence."
            }
        ]
    elif "c++" in title_lower or "cpp" in title_lower or "pointer" in title_lower or "stl" in title_lower or "oop" in title_lower:
        default_qs = [
            {
                "text": f"In {topic.title}, what does the '*' operator do when applied to a pointer variable in C++?",
                "a": "Multiplies two numbers", "b": "Dereferences the pointer to access the value it points to",
                "c": "Declares a reference variable", "d": "Creates a new memory block",
                "correct": "B", "exp": "The dereference operator (*) accesses the value stored at the memory address held by the pointer."
            },
            {
                "text": f"Which C++ keyword is used to allocate dynamic memory on the heap in {topic.title}?",
                "a": "malloc", "b": "alloc", "c": "new", "d": "create",
                "correct": "C", "exp": "The 'new' keyword allocates memory on the heap and returns a pointer to it. 'delete' frees it."
            },
            {
                "text": f"In {topic.title}, what is the purpose of the 'virtual' keyword in C++?",
                "a": "To declare a constant function", "b": "To enable runtime polymorphism through dynamic dispatch",
                "c": "To allocate virtual memory", "d": "To create inline functions",
                "correct": "B", "exp": "The 'virtual' keyword enables late binding so derived class methods are called through base class pointers."
            },
            {
                "text": f"Which STL container in {topic.title} provides O(1) average-case lookup?",
                "a": "std::vector", "b": "std::list", "c": "std::unordered_map", "d": "std::set",
                "correct": "C", "exp": "std::unordered_map uses hash tables internally, providing average O(1) lookup, insert, and delete."
            },
            {
                "text": f"In {topic.title}, what happens if you forget to use 'delete' after 'new' in C++?",
                "a": "Compilation error", "b": "Memory leak — the allocated memory is never freed",
                "c": "The program crashes immediately", "d": "The garbage collector handles it automatically",
                "correct": "B", "exp": "C++ has no garbage collector. Forgetting 'delete' causes memory leaks where heap memory is never reclaimed."
            }
        ]
    elif "sql" in title_lower or "database" in title_lower or "data" in title_lower:
        default_qs = [
            {
                "text": f"In {topic.title}, which SQL statement is used to extract data from a table?",
                "a": "GET", "b": "SELECT", "c": "FETCH", "d": "EXTRACT",
                "correct": "B", "exp": "The SELECT statement retrieves rows and columns from one or more database tables."
            },
            {
                "text": f"Which clause in {topic.title} is used to filter records based on a specified condition?",
                "a": "ORDER BY", "b": "GROUP BY", "c": "WHERE", "d": "HAVING",
                "correct": "C", "exp": "The WHERE clause filters rows before any group-by aggregation occurs."
            },
            {
                "text": f"What does ACID stand for in {topic.title} transactional database systems?",
                "a": "Atomicity, Consistency, Isolation, Durability", "b": "Action, Code, Index, Data",
                "c": "Access, Control, Identity, Design", "d": "Algorithm, Cache, Input, Database",
                "correct": "A", "exp": "ACID guarantees transactional safety and reliability in relational databases."
            }
        ]
    elif "web" in title_lower or "html" in title_lower or "css" in title_lower or "react" in title_lower:
        default_qs = [
            {
                "text": f"What is the primary role of CSS in modern web applications regarding {topic.title}?",
                "a": "Manage server-side database connections", "b": "Structure and present visual styles and layouts",
                "c": "Compile backend bytecode", "d": "Encrypt authentication tokens",
                "correct": "B", "exp": "CSS (Cascading Style Sheets) controls presentation, typography, colors, and layout."
            },
            {
                "text": f"In {topic.title}, which HTTP status code represents a successful response?",
                "a": "200 OK", "b": "404 Not Found", "c": "500 Server Error", "d": "301 Redirect",
                "correct": "A", "exp": "HTTP 200 signals that the request has succeeded."
            },
            {
                "text": f"Which protocol ensures secure, encrypted client-server web communications in {topic.title}?",
                "a": "HTTP", "b": "HTTPS", "c": "FTP", "d": "Telnet",
                "correct": "B", "exp": "HTTPS uses SSL/TLS encryption to protect data in transit between browser and server."
            }
        ]
    else:
        default_qs = [
            {
                "text": f"What is the fundamental objective when mastering {topic.title}?",
                "a": "Memorize syntax without understanding theory", "b": "Understand core architectural principles and practical applications",
                "c": "Bypass best practices to write rapid code", "d": "Rely solely on third-party libraries",
                "correct": "B", "exp": "Mastering fundamental principles ensures scalable, maintainable engineering."
            },
            {
                "text": f"Which approach best optimizes algorithmic performance when studying {topic.title}?",
                "a": "Linear search across unsorted datasets", "b": "Analyzing Time and Space Complexity (Big-O)",
                "c": "Ignoring memory constraints", "d": "Writing repetitive code without abstraction",
                "correct": "B", "exp": "Big-O notation allows software engineers to assess algorithm scalability."
            },
            {
                "text": f"What is a standard industry best practice when validating {topic.title} implementations?",
                "a": "Automated unit and integration testing", "b": "Deploying directly to production without testing",
                "c": "Disabling logging and error tracing", "d": "Hardcoding credentials in scripts",
                "correct": "A", "exp": "Automated testing ensures stability, regression safety, and dependable code quality."
            }
        ]

    for item in default_qs:
        q = Question(
            quiz_id=quiz.id,
            question_text=item["text"],
            option_a=item["a"],
            option_b=item["b"],
            option_c=item["c"],
            option_d=item["d"],
            correct_option=item["correct"],
            explanation=item["exp"],
            is_deleted=False
        )
        db.add(q)
    db.commit()


# =======================================================
# QUIZ HUB (ALL ROADMAP QUIZZES FOR STUDENT)
# =======================================================
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def quiz_hub(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Renders the Quiz Assessments Hub where students can view all checkpoint quizzes
    associated with their career learning roadmap, track scores, and launch assessments.
    """
    # 1. Determine active career
    career_id = current_user.current_career_id
    if not career_id and current_user.enrolled_careers:
        career_id = current_user.enrolled_careers[0].id

    career = None
    if career_id:
        career = db.query(Career).filter(Career.id == career_id, Career.is_deleted == False).first()
    if not career:
        career = db.query(Career).filter(Career.is_deleted == False).first()

    # 2. Collect topics across active career roadmaps
    topics_list = []
    if career:
        roadmaps = db.query(Roadmap).filter(Roadmap.career_id == career.id, Roadmap.is_deleted == False).order_by(Roadmap.order).all()
        for rm in roadmaps:
            rm_topics = db.query(Topic).filter(Topic.roadmap_id == rm.id, Topic.is_deleted == False).order_by(Topic.order).all()
            topics_list.extend(rm_topics)

    if not topics_list:
        topics_list = db.query(Topic).filter(Topic.is_deleted == False).limit(20).all()

    # 3. Build rich quiz items list
    quiz_items = []
    cleared_count = 0
    total_attempts_count = 0

    for t in topics_list:
        # Find or create quiz
        quiz = db.query(Quiz).filter(Quiz.topic_id == t.id, Quiz.is_deleted == False).first()
        if not quiz:
            quiz = Quiz(
                topic_id=t.id, 
                passing_percentage=75, 
                title=f"{t.title} Checkpoint Quiz", 
                is_deleted=False
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
        
        # Ensure questions exist
        ensure_quiz_questions(db, quiz, t)
        q_count = db.query(Question).filter(Question.quiz_id == quiz.id, Question.is_deleted == False).count()

        # Check student attempts
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == current_user.id,
            QuizAttempt.quiz_id == quiz.id
        ).order_by(QuizAttempt.attempted_at.desc()).all()

        attempts_cnt = len(attempts)
        total_attempts_count += attempts_cnt
        best_score = max([a.score for a in attempts], default=0.0)
        has_passed = any(a.passed for a in attempts)
        if has_passed:
            cleared_count += 1

        # Check progress unlock status
        prog = db.query(StudentProgress).filter(
            StudentProgress.student_id == current_user.id,
            StudentProgress.topic_id == t.id
        ).first()

        status_str = "Unlocked"
        if prog:
            status_str = prog.status
        elif current_user.role in ["admin", "super_admin", "teacher", "hod"]:
            status_str = "Unlocked"

        quiz_items.append({
            "quiz": quiz,
            "topic": t,
            "questions_count": q_count,
            "passing_percentage": quiz.passing_percentage or 75,
            "attempts_count": attempts_cnt,
            "best_score": round(best_score, 1),
            "has_passed": has_passed,
            "status": status_str,
            "last_attempt": attempts[0] if attempts else None
        })

    # Summary metrics
    total_quizzes = len(quiz_items)
    cleared_pct = round((cleared_count / total_quizzes * 100), 1) if total_quizzes > 0 else 0.0

    return templates.TemplateResponse("quiz/index.html", {
        "request": request,
        "user": current_user,
        "career": career,
        "quiz_items": quiz_items,
        "total_quizzes": total_quizzes,
        "cleared_count": cleared_count,
        "cleared_pct": cleared_pct,
        "total_attempts_count": total_attempts_count
    })


# =======================================================
# TAKE SPECIFIC QUIZ (BY QUIZ ID OR TOPIC ID)
# =======================================================
@router.get("/take/{quiz_id}", response_class=HTMLResponse)
def take_quiz(quiz_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Renders quiz checkpoint assessment. Resiliently searches by Quiz ID,
    Topic ID, or creates a ready-to-test quiz so students NEVER see a 404 error.
    """
    # 1. Search by Quiz primary key
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_deleted == False).first()

    # 2. If not found, check if quiz_id is actually a topic_id
    if not quiz:
        quiz = db.query(Quiz).filter(Quiz.topic_id == quiz_id, Quiz.is_deleted == False).first()

    # 3. If still not found, check if topic exists with that ID; create quiz on demand
    topic = None
    if not quiz:
        topic = db.query(Topic).filter(Topic.id == quiz_id, Topic.is_deleted == False).first()
        if topic:
            quiz = Quiz(
                topic_id=topic.id,
                passing_percentage=75,
                title=f"{topic.title} Checkpoint Quiz",
                is_deleted=False
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

    # 4. If neither quiz nor topic exists, render friendly fallback
    if not quiz:
        return templates.TemplateResponse("quiz/quiz_not_found.html", {
            "request": request,
            "user": current_user,
            "requested_id": quiz_id
        }, status_code=200)

    if not topic:
        topic = db.query(Topic).filter(Topic.id == quiz.topic_id).first()

    if not topic:
        return templates.TemplateResponse("quiz/quiz_not_found.html", {
            "request": request,
            "user": current_user,
            "requested_id": quiz_id
        }, status_code=200)

    # 5. Ensure topic is unlocked for student access
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id,
        StudentProgress.topic_id == topic.id
    ).first()

    if not progress:
        progress = StudentProgress(student_id=current_user.id, topic_id=topic.id, status="Unlocked")
        db.add(progress)
        db.commit()
    elif progress.status == "Locked":
        # Automatically unlock on direct quiz launch
        progress.status = "Unlocked"
        db.commit()

    # 6. Ensure questions exist
    ensure_quiz_questions(db, quiz, topic)
    questions = db.query(Question).filter(Question.quiz_id == quiz.id, Question.is_deleted == False).all()

    return templates.TemplateResponse(
        "quiz/take_quiz.html",
        {
            "request": request,
            "user": current_user,
            "quiz": quiz,
            "topic": topic,
            "questions": questions
        }
    )


# =======================================================
# SUBMIT QUIZ ANSWERS (BY QUIZ ID OR TOPIC ID)
# =======================================================
@router.post("/submit/{quiz_id}", response_model=schemas.QuizResultResponse)
def submit_quiz(
    quiz_id: int,
    submission: schemas.QuizSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Support lookup by Quiz ID or Topic ID
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_deleted == False).first()
    if not quiz:
        quiz = db.query(Quiz).filter(Quiz.topic_id == quiz_id, Quiz.is_deleted == False).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz checkpoint not found.")

    questions = db.query(Question).filter(Question.quiz_id == quiz.id, Question.is_deleted == False).all()
    correct_count = 0
    total_questions = len(questions)
    answers_review = []

    # Map student answers
    submitted_answers_map = {ans.question_id: ans.selected_option.upper() for ans in submission.answers}

    for q in questions:
        selected = submitted_answers_map.get(q.id, "")
        is_correct = (selected == q.correct_option.upper()) if q.correct_option else False
        if is_correct:
            correct_count += 1
            
        answers_review.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "selected_option": selected,
            "correct_option": q.correct_option,
            "is_correct": is_correct,
            "explanation": q.explanation
        })

    score = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0
    passing_threshold = max(75.0, float(quiz.passing_percentage or 75))
    passed = score >= passing_threshold

    # 1. Store Quiz Attempt
    attempt = QuizAttempt(
        student_id=current_user.id,
        quiz_id=quiz.id,
        score=score,
        passed=passed
    )
    db.add(attempt)

    # Award XP
    xp_bonus = 30 if passed else 10
    current_user.xp = (current_user.xp or 0) + xp_bonus
    db.commit()

    # 2. Recalculate Student Quiz Average
    all_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == current_user.id).all()
    if all_attempts:
        current_user.quiz_avg = round(sum(att.score for att in all_attempts) / len(all_attempts), 1)

    # 3. Log Activity and Analytics
    log = ActivityLog(
        user_id=current_user.id,
        action="submit_quiz",
        details=f"Completed quiz for topic_id {quiz.topic_id} with score {score}% (Passed: {passed})."
    )
    db.add(log)
    
    today = datetime.date.today()
    analytic_rec = db.query(Analytics).filter(
        Analytics.student_id == current_user.id,
        Analytics.date == today
    ).first()
    if not analytic_rec:
        analytic_rec = Analytics(student_id=current_user.id, date=today, quiz_score=score)
        db.add(analytic_rec)
    else:
        analytic_rec.quiz_score = score
        
    db.commit()

    # 4. Adaptive Logic: Mark topic completed and unlock next topic if passed
    if passed:
        progress = db.query(StudentProgress).filter(
            StudentProgress.student_id == current_user.id,
            StudentProgress.topic_id == quiz.topic_id
        ).first()
        if progress:
            progress.status = "Completed"
            progress.completed_at = datetime.datetime.utcnow()
            if analytic_rec:
                analytic_rec.topics_completed += 1
            db.commit()

        # Unlock subsequent topic in roadmap
        current_topic = db.query(Topic).filter(Topic.id == quiz.topic_id).first()
        if current_topic:
            roadmap_topics = db.query(Topic).filter(
                Topic.roadmap_id == current_topic.roadmap_id,
                Topic.is_deleted == False
            ).order_by(Topic.order).all()
            
            next_t = None
            for idx, t in enumerate(roadmap_topics):
                if t.id == current_topic.id and idx + 1 < len(roadmap_topics):
                    next_t = roadmap_topics[idx + 1]
                    break
            
            if not next_t:
                current_roadmap = db.query(Roadmap).filter(Roadmap.id == current_topic.roadmap_id).first()
                if current_roadmap:
                    next_roadmap = db.query(Roadmap).filter(
                        Roadmap.career_id == current_roadmap.career_id,
                        Roadmap.order > current_roadmap.order,
                        Roadmap.is_deleted == False
                    ).order_by(Roadmap.order).first()
                    if next_roadmap:
                        next_t = db.query(Topic).filter(Topic.roadmap_id == next_roadmap.id, Topic.is_deleted == False).order_by(Topic.order).first()
            
            if next_t:
                next_progress = db.query(StudentProgress).filter(
                    StudentProgress.student_id == current_user.id,
                    StudentProgress.topic_id == next_t.id
                ).first()
                if not next_progress:
                    next_progress = StudentProgress(
                        student_id=current_user.id,
                        topic_id=next_t.id,
                        status="Unlocked"
                    )
                    db.add(next_progress)
                elif next_progress.status == "Locked":
                    next_progress.status = "Unlocked"
                db.commit()

    return {
        "score": score,
        "passing_percentage": quiz.passing_percentage,
        "passed": passed,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "answers_review": answers_review
    }
