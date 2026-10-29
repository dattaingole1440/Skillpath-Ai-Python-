# SkillPath AI — Complete Feature Breakdown

> **AI-Powered Adaptive Learning Roadmap Platform** built with FastAPI, SQLAlchemy, Jinja2, and Google Gemini AI.

---

## 🔐 User Roles

The platform has **5 distinct roles**, each with separate dashboards and permissions:

| Role | Description |
|------|-------------|
| **Student** | Primary learner — accesses roadmaps, quizzes, coding, AI tools |
| **Teacher** | Manages assignments, grades, attendance, early warnings |
| **Admin** | Manages careers, roadmaps, topics, quizzes, coding challenges |
| **College Admin** | Creates colleges, departments, imports students via CSV |
| **Super Admin** | Full platform control across all colleges |

---

## 👨‍🎓 Student Features (18 modules)

### 1. Authentication (`/auth`)
- Login / Register / Logout
- Forgot Password & Reset Password flow
- JWT cookie-based sessions (2-hour expiry)
- Role auto-detection (email containing "admin" → admin role)
- Activity logging on every auth event

### 2. Dashboard (`/dashboard`)
- Career path enrollment & switching between multiple paths
- Real-time progress tracking (% completed across all enrolled paths)
- Current topic & next topic display
- Recent activity feed (last 5 actions)
- AI-powered recommendation widget

### 3. Adaptive Learning Roadmap (`/roadmap`)
- Visual roadmap with ordered modules & topics
- **Lock/Unlock system** — topics unlock sequentially as you progress
- Per-topic detail pages with:
  - YouTube video embeds
  - Official documentation links
  - Practice questions
  - Notes & cheat sheets
- **Study heartbeat** — JS pings server every 60 seconds to track active study time
- Manual & auto topic completion (quiz + coding pass = auto-complete)

### 4. Quiz Engine (`/quiz`)
- MCQ quizzes tied to each topic (4 options: A/B/C/D)
- Auto-grading with score calculation
- Explanations shown after submission
- Pass/fail based on configurable passing percentage
- **Adaptive progression** — passing quiz + coding challenges auto-completes topic & unlocks next

### 5. Coding Challenges (`/coding`)
- In-browser code editor with submission
- **Multi-language execution engine**:
  - 🐍 Python — sandboxed `exec()` with stdout capture
  - ☕ Java — `javac` + `java` compilation via subprocess
  - ⚡ C++ — `g++` compilation via subprocess
- Automated test case evaluation against expected outputs
- Score calculation & coding average tracking
- Previous submission history

### 6. AI Chat Assistant (`/chat`, `/api/ai/chat`)
- Real-time AI coding tutor powered by **Google Gemini**
- Per-user conversation history with reset capability
- Dedicated premium chat page
- Both JSON API and form-based endpoints

### 7. Analytics Dashboard (`/analytics`)
- 7-day rolling analytics:
  - Study hours per day
  - Quiz performance scores
  - Coding challenge scores
  - Topics completed count

### 8. AI Resume Builder (`/resume/builder`)
- Form-based resume input (personal info, skills, projects, certificates)
- **Gemini AI generates ATS-optimized resume** text
- Resume stored in database

### 9. AI Resume Analyzer (`/resume/analyzer`)
- Upload resume file or paste text
- AI analyzes and returns:
  - ATS compatibility score
  - Missing skills
  - Recommended skills
  - Improvement suggestions
  - Overall rating

### 10. Mock Interview Simulator (`/mock-interview`)
- Choose interview type (Technical, Behavioral, etc.)
- **AI generates contextual interview questions** via Gemini
- Student answers each question → AI evaluates with score + feedback
- 4-question sessions → overall score + confidence rating
- XP & coin rewards on completion

### 11. Gamification System
- **XP & Coins** — earned for completing quizzes, challenges, interviews, etc.
- **Rank System** — Beginner → Explorer → Developer → Expert → Master → Legend
- **Daily Streak** tracking — consecutive learning days
- **Leaderboard** (`/leaderboard`) — top 20 students by XP
- **Daily Challenges** (`/daily-challenges`) — 3 auto-generated challenges per day (quiz, coding, interview) with XP/coin rewards

### 12. Certificate Generation (`/certificate`)
- PDF certificate generation using **ReportLab**
- QR code verification using **qrcode** library
- **Only unlocked after completing ALL topics** in a career path
- Public verification page for employers (`/certificate/verify/{cert_number}`)
- Download protected — only certificate owner or admin can download

### 13. Discussion Forum (`/forum`)
- Create posts with categories (General, etc.)
- Threaded comments/answers
- Like/unlike comments
- **Best answer** marking (StackOverflow-style)
- Search & category filtering
- View counter on posts
- XP rewards for posting (+10) and commenting (+15)

### 14. Project Recommendations (`/projects`)
- 13 curated projects (Beginner → Intermediate → Advanced)
- GitHub template links for each project
- **AI-powered project recommendations** based on career path & skill level
- Project submission tracking

### 15. Student Assignments (`/student/assignments`)
- View all assignments from teachers
- Submit text, code, or file URL
- Track submission status
- XP reward (+40) for submissions

### 16. Placement Readiness (`/student/placement`)
- Composite placement score calculated from 7 metrics (coding, quiz, projects, attendance, resume, interview, roadmap completion)
- **AI-generated placement recommendations** via Gemini

### 17. Student Notifications (`/student/notifications`)
- Receive notifications from teachers (greetings, birthdays, warnings, reminders)
- Broadcast + targeted notifications

### 18. Activity-Based Attendance
- **Automated attendance** based on daily study time:
  - ≥ 30 min → Present
  - 10–30 min → Partial
  - < 10 min → Absent
- Manual override support by teachers

---

## 🧑‍🏫 Teacher Features (6 modules)

### 1. Teacher Dashboard (`/teacher/dashboard`)
- Class overview with subjects taught
- Pending submissions counter
- Early warning alerts
- Total student count

### 2. Assignment Management (`/teacher/assignments`)
- Create assignments (theory, coding, PDF, project types)
- Configurable due dates & max marks
- View all submissions per assignment
- **Manual grading** with marks & feedback
- **AI-powered auto-grading** — Gemini evaluates student submissions and suggests marks

### 3. Resource Management (`/teacher/resources`)
- Upload learning resources (videos, docs, notes, cheatsheets)
- Linked to topics in the roadmap

### 4. Notifications (`/teacher/notifications`)
- Send notifications to individual students or broadcast to all
- Types: general, greeting, birthday, congratulations, warning, assignment/exam reminders

### 5. Early Warning System (`/teacher/early-warning`)
- **AI-powered risk analysis** per student using Gemini
- Evaluates: study time, attendance %, quiz avg, coding avg, missing assignments
- Generates risk level (low/medium/high) with AI analysis & trigger reason

### 6. Reports Hub (`/reports`)
- Download **PDF reports** (via ReportLab):
  - Student Performance Report
  - Attendance Activity Report
  - Placement Readiness Report
- Download **CSV/Excel reports** for student data

---

## 🔧 Admin Panel Features

### Admin Dashboard (`/admin`)
- Stats overview: total students, careers, roadmaps, topics, certificates
- Recent student signups

### Content Management
- **Manage Careers** — Add career paths (Python Developer, Java Developer, C++ Developer, etc.)
- **Manage Roadmaps** — Ordered learning modules within each career
- **Manage Topics** — Add topics with description, difficulty, estimated time, YouTube videos, docs, notes, cheat sheets
- **Manage Quizzes** — Create quizzes per topic with configurable passing %
- **Manage Questions** — Add MCQ questions (A/B/C/D with correct answer + explanation)
- **Manage Coding Challenges** — Add challenges with template code, test cases (JSON), difficulty, score points
- **View Students** — List all registered students
- **Export Students CSV** — Download all student data as CSV

---

## 🏫 College Management (`/college`)
- **Create Colleges** with name, code, email, address (super_admin only)
- **Create Departments** — auto-generates 8 semesters + Division A/B per semester
- **Bulk Student Import** via CSV (columns: name, email, roll_number, phone_number) with default password

---

## 🤖 AI/ML Features (Powered by Google Gemini)
| Feature | Module |
|---------|--------|
| AI Chat Tutor | Real-time doubt solving |
| AI Resume Builder | ATS-optimized resume generation |
| AI Resume Analyzer | Score, missing skills, suggestions |
| AI Mock Interview | Dynamic question generation + answer evaluation |
| AI Assignment Grading | Auto-evaluation with marks suggestion |
| AI Early Warning | Student risk analysis |
| AI Placement Readiness | Composite score + recommendations |
| AI Project Recommendations | Career-based project suggestions |
| AI Performance Summary | Teacher performance insights |

---

## ⚙️ Additional Modules

| Module | Route | Description |
|--------|-------|-------------|
| Study Planner | `/study-planner` | AI-powered study schedule |
| Code Reviewer | `/code-reviewer` | AI code review & suggestions |
| Code Editor | `/code-editor` | In-browser code editor |
| Study Groups | `/study-groups` | Collaborative study groups |
| Notes | `/notes` | Personal note-taking |
| Resource Library | `/resource-library` | Centralized learning resources |
| Search | `/search` | Global search across platform |
| Notifications | `/notifications` | System notifications |
| Portfolio | `/portfolio` | Student portfolio showcase |
| PWA Support | `/pwa` | Progressive Web App manifest |
| Recommendations | `/recommendation` | AI-driven learning recommendations |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.111, Python 3.12 |
| Database | MySQL (primary) / SQLite (fallback) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (PyJWT) + bcrypt + cookie-based sessions |
| AI Engine | Google Gemini (`gemini-3.6-flash`) |
| Templates | Jinja2 |
| PDF Generation | ReportLab |
| QR Codes | qrcode[pil] |
| Containerization | Docker + Docker Compose |

---

## 📊 Summary

| Category | Count |
|----------|-------|
| Total Modules | **30+** |
| User Roles | **5** (Student, Teacher, Admin, College Admin, Super Admin) |
| AI-Powered Features | **9** |
| Supported Languages (Coding) | **3** (Python, Java, C++) |
| Report Formats | **3** (PDF, CSV, Excel) |
