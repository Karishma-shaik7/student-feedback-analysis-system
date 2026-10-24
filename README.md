# 🎓 Student Feedback Analysis System

A modern, production-ready Full-Stack Web Application built with **Python (Flask)**, **MySQL**, **Pandas**, and **Matplotlib**, featuring a premium responsive dark dashboard styled with custom modern CSS and vanilla JavaScript.

---

## 🌟 Key Features

1. **Student Feedback Submission**:
   - Database-backed course selector.
   - Interactive, accessible 5-star rating component with live visual hover preview.
   - Optional detailed feedback comments with anti-XSS sanitization.
   - Instant client-side validation and debounced submission to prevent accidental double-submits.
   - Server-side validation with explicit bounds checking (1–5 ratings).

2. **Executive Analytics Dashboard**:
   - Real-time KPI summary cards: Total Feedback, Overall Average Rating, Total Active Courses, Highest Rated Course.
   - **Pandas** data analysis engine computing distribution percentiles and course-level metrics.
   - Beautiful **Matplotlib** visualizations rendered with a cohesive dark-navy violet theme:
     - *Average Rating by Course* (horizontal bar chart with labeled data values).
     - *Rating Distribution Breakdown* (1★ to 5★ proportional distribution).
     - *Student Feedback Volume per Course* (comparative response counts).
   - Recent feedback timeline table displaying star ratings, sanitized student comments, and timestamps.
   - Graceful, informative empty states with action triggers when no records exist yet.

3. **Enterprise Architecture & Security**:
   - Centralized configuration via `config.py` and `.env` variables.
   - 100% Parameterized SQL queries using `mysql-connector-python` to prevent SQL Injection.
   - Explicit database transactions with safe commits and error rollbacks.
   - Passwords never hardcoded, exposed, or committed to Git.
   - Full automated test suite verifying form validation, calculations, charts, and database reliability.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Responsive dark UI, star rating picker, validation, animations |
| **Backend** | Python 3.10+, Flask | HTTP routing, server validation, session messaging, templating |
| **Database** | MySQL Server 8.0, `mysql-connector-python` | Relational storage, foreign keys, constraints, transactions |
| **Analytics** | Pandas | Course score aggregation, summary metrics, statistical distributions |
| **Charts** | Matplotlib (Agg backend) | High-DPI headless chart rendering aligned to the dark UI theme |
| **Testing** | Pytest | Unit and integration testing across routes, database, and calculations |

---

## 📋 Prerequisites

Before setting up the project, ensure you have installed on your computer:
1. **Python 3.10 or higher**: Verify in PowerShell with `python --version`.
2. **MySQL Server 8.0+**: Verify in PowerShell with `mysql --version`. Ensure the MySQL Windows Service is running (`Get-Service MySQL80`).
3. **Git**: Verify in PowerShell with `git --version`.

---

## 🚀 Step-by-Step Installation & Setup (Windows PowerShell)

Open **Windows PowerShell** as Administrator or standard user, and navigate to the project directory:

```powershell
cd C:\Users\shaik\Downloads\student-feedback-analysis-new
```

### 1. Create and Activate a Virtual Environment

It is best practice to keep Python packages isolated:

```powershell
# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

> *Tip: If PowerShell displays a script execution policy error, run:*
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 2. Install Project Dependencies

Install all required packages from `requirements.txt`:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🗄️ MySQL Database Setup

### 1. Initialize the Database and Tables

Open PowerShell and execute the provided `database/schema.sql` script through the MySQL client:

```powershell
# Replace 'root' with your MySQL username if different
mysql -u root -p < database/schema.sql
```
*(Enter your MySQL password when prompted.)*

This script:
- Creates the `student_feedback_db` database if it doesn't already exist.
- Creates the `courses` table with constraints and indexes.
- Creates the `feedback` table linked by a foreign key constraint with cascade actions.
- Seeds 6 initial sample courses (e.g., CS101, CS201, CS301) without any artificial feedback responses.

### 2. Configure Environment Variables

1. Copy `.env.example` to create your local `.env` file:

```powershell
Copy-Item .env.example .env
```

2. Open `.env` in your text editor (such as VS Code or Notepad):

```powershell
notepad .env
```

3. Update the credentials with your actual local MySQL password:

```ini
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_SECRET_KEY=enter-a-unique-secret-key-here

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_mysql_password
MYSQL_DATABASE=student_feedback_db
```

Save and close the file.

---

## ▶️ Running the Application

With your virtual environment activated, run the application:

```powershell
python app.py
```

You should see output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

### Local Browser URLs:
- **Student Feedback Form**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Analytics Dashboard**: [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

---

## 🧪 Running Automated Tests

Run the full automated test suite using `pytest`:

```powershell
# Run all tests with verbose summary
pytest -v

# Run with output print statements enabled
pytest -v -s
```

The test suite covers:
- Flask application factory & route availability.
- Course dropdown data loading.
- Rating bounds rejection (rejecting ratings < 1, > 5, or invalid types).
- Unknown course rejection (invalid foreign keys).
- Successful feedback persistence and transaction commits.
- Failure handling (ensuring no false-positive success toasts when db operations fail).
- Pandas metric calculations (mean rating, response count, top-rated course logic).
- Matplotlib headless chart generation.
- Empty database resilience (ensures dashboard renders clean zero-state without crashing).

---

## 🔍 Common Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `Access denied for user 'root'@'localhost'` | Incorrect password in `.env` | Verify your password in MySQL Workbench or CLI, then update `MYSQL_PASSWORD` in `.env`. |
| `Can't connect to MySQL server on 'localhost'` | MySQL service stopped | Start MySQL service via PowerShell: `Start-Service MySQL80`. |
| `Unknown database 'student_feedback_db'` | Schema script not executed | Run `mysql -u root -p < database/schema.sql` to initialize the database. |
| `Script execution is disabled on this system` | PowerShell ExecutionPolicy | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. |
| Matplotlib GUI thread error | GUI backend attempted in web server | Ensure `matplotlib.use('Agg')` is initialized at the top of the analytics module (already handled). |

---

## 🌐 Publishing to GitHub

To publish this project to GitHub without committing local secrets:

```powershell
# 1. Initialize git repository
git init

# 2. Verify that .env is ignored
git status

# 3. Add files and make initial commit
git add .
git commit -m "Initial commit: Complete Student Feedback Analysis System"

# 4. Create repository on GitHub and link remote
git branch -M main
git remote add origin https://github.com/<your-username>/student-feedback-analysis.git
git push -u origin main
```
*(Ensure `.env` was never tracked or pushed.)*
