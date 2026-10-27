# 🎓 EduPulse: Student Feedback Analysis System

A modern, production-grade Full-Stack Academic Analytics Web Application built with **Python (Flask)**, **MySQL Server 8.0**, **Pandas**, and **Matplotlib (Agg)**, featuring an interactive student evaluation portal and an executive real-time analytics dashboard with custom modern CSS and vanilla JavaScript.

---

## 🌟 1. Project Overview & Key Features

### ✍️ Student Feedback Portal
- **Database-Driven Course Catalog**: Course dropdown dynamically populated from active MySQL catalog records (e.g., CS101, CS201, CS301).
- **Interactive 5-Star Rating Control**: Custom accessible star rating component with real-time hover glow, dynamic text descriptors, and keyboard navigation.
- **Accidental Double-Submission Prevention**: Client-side debounce automatically disables submit buttons during transmission to eliminate duplicate records.
- **Defense-in-Depth Validation**: Multi-layer bounds checking ($1 \le \text{rating} \le 5$) on the client, server, and SQL schema levels.
- **Anti-XSS Sanitization**: User comments are stripped, bounded, and auto-escaped via Jinja2 to prevent Cross-Site Scripting vulnerabilities.

### 📊 Executive Analytics Dashboard
- **Real-Time KPI Cards**:
  - Total Feedback Responses
  - Overall Average Satisfaction Rating ($/ 5.0$) with dynamic gold star badges
  - Total Active Courses
  - Highest-Rated Course (with real-time tie-breaking and score calculation)
- **Headless Server-Side Matplotlib Charts (`Agg` Backend)**:
  - *Course Satisfaction Comparison*: Horizontal bar chart displaying mean scores per course.
  - *Rating Star Distribution*: Color-coded frequency breakdown of 1★ through 5★ reviews.
  - *Feedback Volume by Course*: Comparative response count bar chart.
- **Recent Feedback Feed**: Chronological timeline showing course codes, instructors, star ratings, sanitized comments, and formatted timestamps.
- **Zero-Record Resilience**: Polite, professional empty-state card rendered when zero submissions exist, preventing `ZeroDivisionError` crashes.

---

## 🛠️ 2. Technology Stack & Architecture

| Layer | Technology | Role & Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JS | Accessible UI, star rating picker, form debouncing, dark-navy design system |
| **Backend** | Python 3.10+, Flask 3.1+ | REST routing, server-side validation, session flash messages, templating |
| **Database** | MySQL Server 8.0 | Normalized relational schema, foreign keys, cascades, CHECK constraints |
| **Connector** | `mysql-connector-python` | Parameterized SQL query execution preventing SQL Injection |
| **Analytics** | Pandas 3.0+ | DataFrame group-by aggregations, mean scores, and frequency distributions |
| **Visualization**| Matplotlib 3.11+ (Agg) | Headless, thread-safe, in-memory Base64 image stream generation |
| **Testing** | Pytest 9.0+ | 23 automated tests covering routes, validation, transactions, and UI |
| **Deployment** | Gunicorn | Production WSGI HTTP server for Linux cloud environments |

---

## 📁 3. Project Directory Structure

```
student-feedback-analysis-new/
│
├── .env.example                                      # Environment variables template
├── .gitignore                                         # Protects credentials, venv, and cache
├── README.md                                          # Complete system documentation
├── requirements.txt                                   # Python dependencies
├── config.py                                          # Centralized configuration manager
├── app.py                                             # Main Flask web application
├── setup_db.py                                        # Automated database initializer
├── generate_presentation.py                           # Generates 10-slide PowerPoint file
├── presentation_deck.md                               # Slide-by-slide speaker notes & script
├── Student_Feedback_Analysis_System_Presentation.pptx # Editable PowerPoint presentation
│
├── database/
│   ├── schema.sql                                     # DDL schema for courses and feedback
│   └── db.py                                          # Parameterized queries & transactions
│
├── analytics/
│   └── engine.py                                      # Pandas aggregations & Matplotlib engine
│
├── templates/
│   ├── base.html                                      # Layout shell, sidebar, and flash alerts
│   ├── index.html                                     # Student feedback submission portal
│   ├── dashboard.html                                 # Executive analytics dashboard
│   ├── 404.html                                       # Custom 404 error page
│   └── 500.html                                       # Custom 500 error page
│
├── static/
│   ├── css/style.css                                  # Custom dark-theme CSS design system
│   ├── js/main.js                                     # Star ratings, validation, and drawer
│   └── images/charts/                                 # Exported Matplotlib chart cache
│
└── tests/
    ├── conftest.py                                    # Shared test fixtures & mock datasets
    ├── test_config.py                                 # Configuration & secret masking tests
    ├── test_db.py                                     # DB constraints, checks & transactions
    ├── test_routes.py                                 # Route validation, bounds & error pages
    ├── test_analytics.py                              # Pandas metrics, empty state & charts
    └── test_ui_responsive.py                          # Responsive viewport & table tests
```

---

## 🚀 4. Step-by-Step Installation & Local Setup (Windows PowerShell)

### Step 1: Open Terminal in Project Directory
```powershell
cd C:\Users\shaik\Downloads\student-feedback-analysis-new
```

### Step 2: Set Up Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Database Password
1. Create your local `.env` file from the provided template:
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```
2. Set your MySQL root password:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_actual_mysql_password
   MYSQL_DATABASE=student_feedback_db
   FLASK_SECRET_KEY=dev-secret-key-change-this-in-production
   ```
3. Save and close Notepad.

### Step 5: Initialize MySQL Schema & Seed Courses
Make sure your MySQL80 service is running, then execute:
```powershell
python setup_db.py
```
*This automatically creates `student_feedback_db`, initializes the tables, and seeds the 6 initial academic courses without any fake student reviews.*

### Step 6: Launch the Web Application
```powershell
python app.py
```

### Step 7: Open in Browser
- ✍️ **Student Feedback Form**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- 📊 **Executive Analytics Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)
- 🩺 **Health Check API**: [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health)

---

## 🧪 5. Automated Testing & Verification

Run the full automated test suite using `pytest`:

```powershell
pytest -v
```

All **23 automated tests pass** across:
- Route accessibility and form validation.
- Rejection of out-of-bounds ratings ($< 1$ or $> 5$) and non-existent course IDs.
- Parameterized database insertion and explicit transaction commits.
- Failure resilience (guaranteeing success alerts are never shown on database errors).
- Mathematical correctness of Pandas averages, counts, and top-course logic.
- Headless Matplotlib chart rendering as valid Base64 data streams.
- Zero-record empty-state fallback handling.
- Mobile viewport scaling and responsive breakpoint styles.

---

## 🌐 6. Beginner-Friendly Guide: Uploading to GitHub

Follow these steps to publish your project cleanly to GitHub **without exposing passwords**:

### 1. Verify Security Exclusion First
Check that `.env` is properly ignored by Git:
```powershell
git status
```
*(Verify that `.env` does **not** appear in the list of tracked files. Only `.env.example` should be tracked!)*

### 2. Create a New Repository on GitHub
1. Open your browser and go to [https://github.com/new](https://github.com/new).
2. Enter repository name: `student-feedback-analysis-system`.
3. Choose **Public** (or Private).
4. Leave "Add a README file", "Add .gitignore", and "Choose a license" **UNCHECKED** (we already have them).
5. Click **Create repository**.

### 3. Push Your Local Code to GitHub
In Windows PowerShell inside the project directory, run:
```powershell
# 1. Stage all project files
git add .

# 2. Commit the files
git commit -m "feat: complete Student Feedback Analysis System with real-time analytics"

# 3. Ensure branch is named main
git branch -M main

# 4. Link your remote GitHub repository (replace with your actual GitHub URL)
git remote add origin https://github.com/<your-username>/student-feedback-analysis-system.git

# 5. Push code to GitHub
git push -u origin main
```

---

## ☁️ 7. Live Production Deployment Guide

To deploy this project to the internet and get a public HTTPS link for your presentation:

### Recommended Free/Low-Cost Architecture: **Render + Aiven MySQL**
- **Web App**: Hosted on [Render.com](https://render.com) (Free Web Service tier).
- **Database**: Free Managed Cloud MySQL on [Aiven.io](https://aiven.io) or [Railway.app](https://railway.app).

### Step-by-Step Cloud Deployment:

#### 1. Create a Free Cloud MySQL Database (e.g. on Aiven.io or Railway)
1. Sign up at [Aiven.io](https://aiven.io) (offers free trial / free tier MySQL).
2. Create a new service: **MySQL 8.0**.
3. Once running, copy the connection details:
   - Host (e.g., `mysql-xxxx.aivencloud.com`)
   - Port (e.g., `12345`)
   - User (e.g., `avnadmin`)
   - Password (auto-generated secret)
   - Database (e.g., `defaultdb` or `student_feedback_db`)
4. In Aiven's Web Console or MySQL Workbench, execute the DDL script in [`database/schema.sql`](file:///c:/Users/shaik/Downloads/student-feedback-analysis-new/database/schema.sql) to create the `courses` and `feedback` tables.

#### 2. Deploy the Web App on Render.com
1. Sign up at [Render.com](https://render.com) and click **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository: `student-feedback-analysis-system`.
3. Configure the build parameters:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Add your **Environment Variables** in the Render Dashboard:
   - `FLASK_ENV`: `production`
   - `FLASK_SECRET_KEY`: *(Generate a 64-char random string via `python -c "import secrets; print(secrets.token_hex(32))"`)*
   - `MYSQL_HOST`: *(Your cloud MySQL host)*
   - `MYSQL_PORT`: *(Your cloud MySQL port)*
   - `MYSQL_USER`: *(Your cloud MySQL user)*
   - `MYSQL_PASSWORD`: *(Your cloud MySQL password)*
   - `MYSQL_DATABASE`: *(Your cloud MySQL database name)*
5. Click **Create Web Service**.
6. Render will build the application, install requirements, start Gunicorn, and provide you with an **official public HTTPS URL** (e.g., `https://student-feedback-analysis.onrender.com`).

---

## 📊 8. Project Presentation Resources

This repository includes full presentation materials ready for college reviews and vivas:
- **Editable PowerPoint Deck**: [`Student_Feedback_Analysis_System_Presentation.pptx`](file:///c:/Users/shaik/Downloads/student-feedback-analysis-new/Student_Feedback_Analysis_System_Presentation.pptx)  
  *(10 professionally formatted slides in 16:9 widescreen dark theme with embedded speaker notes)*
- **Speaker Notes & Script**: [`presentation_deck.md`](file:///c:/Users/shaik/Downloads/student-feedback-analysis-new/presentation_deck.md)  
  *(Word-for-word spoken script for each slide, covering problem, architecture, innovation, and future scope)*
- **Re-generate Deck Script**: Run `python generate_presentation.py` to regenerate the PPTX anytime.

---

## 🔒 9. Security & Data Protection Highlights

- **SQL Injection Defense**: 100% of user queries pass through parameterized SQL placeholders (`%s`). Raw string formatting is strictly prohibited.
- **Transactional Integrity**: Database operations execute inside atomic `commit()` blocks and roll back on error.
- **Fail-Safe Alerting**: Success notifications are strictly tied to verified database commits.
- **Credentials Protection**: All passwords and keys reside in `.env` and are strictly excluded from version control via `.gitignore`.
