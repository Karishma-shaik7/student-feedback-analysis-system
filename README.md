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


## 🔒 8. Security & Data Protection Highlights

- **SQL Injection Defense**: 100% of user queries pass through parameterized SQL placeholders (`%s`). Raw string formatting is strictly prohibited.
- **Transactional Integrity**: Database operations execute inside atomic `commit()` blocks and roll back on error.
- **Fail-Safe Alerting**: Success notifications are strictly tied to verified database commits.
- **Credentials Protection**: All passwords and keys reside in `.env` and are strictly excluded from version control via `.gitignore`.
