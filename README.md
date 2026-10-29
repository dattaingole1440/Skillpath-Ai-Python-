# SkillPath AI: AI Powered Adaptive Learning Roadmap Platform

SkillPath AI is a modern, intelligent web platform designed to help students master technical engineering career tracks through personalized, adaptive learning roadmaps. 

Unlike static tutorial repositories, SkillPath AI tracks learning hours, streaks, quiz averages, and programming test case outputs, leveraging Google Gemini AI (with local fallback rules) to generate tailored recommendations on next topics, revisions, code practices, and mini-projects.

---

## 🚀 Key Features

* **Adaptive Milestones**: Sequential roadmap nodes that unlock automatically upon clearing assessment checkpoints.
* **In-Browser Code Workspace**: Write Python code directly in a built-in code editor workspace, running compilation and unit test diagnostics.
* **Interactive MCQ Quizzes**: Checkpoint assessments with instant reviews, grading, and explanations.
* **Gemini AI Coaching**: Direct analysis of student progress datasets (quiz scores, coding correctness, study hours) providing targeted advice.
* **Verified QR Certificates**: PDF certificate generation complete with issues dates, serial IDs, and scanned verification QR codes.
* **Admin Dashboard**: Manage user profiles, careers, milestone roadmaps, topics, quizzes, and coding test cases.
* **Dual Theme Layout**: White dashboard theme with professional blue accents and a persistent Dark Mode toggler.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.12, FastAPI, SQLAlchemy ORM, Jinja2 Templates, PyMySQL, Pydantic, Passlib (BCrypt), PyJWT.
* **Frontend**: HTML5, CSS3, ES6 JavaScript, Bootstrap 5, Bootstrap Icons, Chart.js.
* **Database**: MySQL (SQLite supported via automatic fallback).
* **Document Generation**: ReportLab PDF library, Python `qrcode` library.
* **AI Engine**: Google Gemini API (`google-generativeai`).

---

## ⚙️ Project Setup

### Prerequisites
* Python 3.12 installed.
* MySQL running (optional, SQLite database `skillpath_ai.db` will be auto-generated as fallback if MySQL is unreachable).

### Local Installation

1. **Extract and Navigate to Directory**:
   ```bash
   cd finalstudent
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   A default `.env` file has been prepared. If you want to use the Gemini AI features:
   * Open the `.env` file and insert your API key:
     ```env
     GEMINI_API_KEY=your_actual_google_gemini_api_key
     ```
   * *Note: If this key is blank, the app uses an intelligent rule-based recommendation engine so everything remains functional offline.*

5. **Run the Application**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🐳 Docker Deployment

The project includes pre-configured Docker environments for multi-container orchestration (FastAPI + MySQL).

1. **Start Containers**:
   ```bash
   docker-compose up --build
   ```

2. **Access App**:
   Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000). The database will automatically initialize and seed initial data.

---

## 🔑 Seeding & Credentials

Upon initial launch, the system automatically checks the tables and seeds initial data (Python Developer, Frontend Developer, and Backend Developer tracks with milestones, topics, MCQ quizzes, and coding unit test cases).

Use these default credentials to evaluate the platform immediately:

### 👤 Student Account (Jane Student)
* **Email**: `student@skillpath.ai`
* **Password**: `student123`
* *Use this to view the dashboard, take quizzes, write code, get AI advice, and generate certificates.*

### 🛠️ Admin Account (Admin User)
* **Email**: `admin@skillpath.ai`
* **Password**: `admin123`
* *Use this to manage student tables, add topics, edit MCQs, and configure coding test cases.*
