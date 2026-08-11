# 🎓 EduSense — AI Student Performance Monitoring & Master Data Management System

> **Jayaraj Annapackiam C. S. I. College of Engineering, Nazareth**  
> Department of Artificial Intelligence and Data Science  
> Course: **CW3551 Data and Information Security** | Batch: **2023–2027** | Sem: **05**  
> Instructor: **G. Alisha Evangeline, AP/ADS** | Developer: **Santhosh Raj V**

---

## 📚 Documentation Directory

Detailed technical documentation is available in the [`docs/`](./docs) directory:

- 📘 **[Project Overview & Architecture](./docs/overview.md)** — Workflow, AI integration, and core capabilities.
- 🛠️ **[Tech Stack & Design System](./docs/tech_stack.md)** — Plus Jakarta Sans typography, glassmorphism, and component system.
- 🚀 **[Setup & Deployment Guide](./docs/setup_guide.md)** — Multi-stage Docker, Docker Compose, and local execution.
- 🗄️ **[Database Architecture & Schema](./docs/database_schema.md)** — MySQL 8.0 schema DDL, multi-table CRUD, and SQLite fallback.

---

## 📌 Project Overview

**EduSense** is an enterprise-grade academic analytics platform designed to monitor student performance, detect academic risks, manage institution master data (staff, departments, academic terms), query insights using Google Gemini AI, and dispatch automated SMTP email notifications.

### Core End-to-End Workflow

```
Excel Markbook Upload ➔ Multi-Sheet Parsing ➔ MySQL Database Storage
                                                      │
    ┌─────────────────────────────────────────────────┴─────────────────────────────────────────────────┐
    ▼                                                 ▼                                                 ▼
Early Warning Rule Engine                     Master Data Manager                             Google Gemini AI Assistant
(Attendance, Marks, Assignment Cut-offs)      (Staffs, Depts, Academic Years)                 (Dataset RAG & Offline Rules)
    │                                                 │                                                 │
    ▼                                                 ▼                                                 ▼
Interactive Analytics Dashboard               Departmental & Staff Rosters                    Automated SMTP Email Alerts
```

---

## 🛠️ Technology Stack

| Layer | Technology & Tools |
|-------|-------------------|
| **Typography & UI** | **Plus Jakarta Sans**, Modern Glassmorphic Design System, HSL Color Palettes, Micro-animations |
| **Frontend Framework** | HTML5, Vanilla CSS3, JavaScript (ES6+), Chart.js 4.x, Lucide Vector Icons |
| **Backend API** | Python 3.10+, Flask REST API framework |
| **Database** | MySQL 8.0 (PyMySQL with automatic zero-downtime SQLite fallback) |
| **AI Reasoning Engine**| Google Gemini API (`gemini-2.5-flash`) with offline rule engine fallback |
| **Email Dispatcher** | Python `smtplib`, `email.mime` (TLS/SSL multi-provider support) |
| **Data Ingestion** | Pandas, OpenPyXL (Multi-sheet markbook parser) |
| **Containerization** | Multi-stage production `Dockerfile` (Non-root `appuser`, health checks, layer caching) |

---

## 📁 Project Structure

```
Student-Performance-Prediction/
├── run.py                          # Application entry point (PORT configurable)
├── Dockerfile                      # Optimized multi-stage production build
├── docker-compose.yml              # Multi-container stack (Flask + MySQL 8.0)
├── .dockerignore                   # Excludes build context noise & virtual environments
├── .env.example                    # Environment variable template
├── README.md                       # Main documentation guide
│
├── frontend/                       # Web UI Layer
│   ├── templates/
│   │   ├── base.html               # Main layout drawer & navigation
│   │   ├── login.html              # Modern glassmorphic authentication screen
│   │   ├── dashboard.html          # Dynamic KPI cards & Chart.js visualizations
│   │   ├── students.html           # Searchable & filterable student registry
│   │   ├── analytics.html          # Performance matrix & departmental insights
│   │   ├── alerts.html             # SMTP email notification audit logs
│   │   ├── management.html         # Master Data Manager (Staffs, Depts, Academic Years)
│   │   ├── settings.html           # Threshold range sliders & API key controls
│   │   └── upload.html             # Drag-and-drop Excel markbook importer
│   └── static/
│       ├── css/style.css           # Modern design system & token definitions
│       └── js/
│           ├── dashboard.js        # Dynamic charts, modal triggers, filters
│           └── chatbot.js          # Interactive Gemini AI assistant drawer
│
├── backend/                        # Core Engine & Services
│   ├── app.py                      # Flask routes & REST endpoints
│   ├── config.py                   # System configuration & environment paths
│   ├── database.py                 # MySQL persistent layer with SQLite fallback
│   ├── schema.sql                  # MySQL database DDL definitions
│   ├── requirements.txt            # Python dependencies
│   ├── data/                       # Official dataset & SQLite fallback database
│   └── services/
│       ├── excel_service.py        # College markbook parser (I1, I2, I3, RUBRICS)
│       ├── risk_service.py         # Configurable early warning risk calculator
│       ├── gemini_service.py       # Google Gemini LLM service with RAG prompt
│       └── email_service.py        # Automated SMTP notification manager
│
└── docs/                           # Technical documentation suite
    ├── overview.md
    ├── tech_stack.md
    ├── setup_guide.md
    └── database_schema.md
```

---

## 🚀 Quick Start & Deployment

### 1. Local Development Mode

```bash
# Clone repository
git clone https://github.com/vsanthoshraj/Student-Performance-Prediction.git
cd Student-Performance-Prediction

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start application
python run.py
```
Access at: **`http://localhost:5000`** (Default Login: `admin` / `admin`).

---

### 2. Multi-Container Production Stack (Docker Compose)

Spin up both the **EduSense Web Application** and a persistent **MySQL 8.0 Database** container:

```bash
# Build and launch background services
docker-compose up -d --build

# Verify container health
docker-compose ps
```

---

## 🗄️ Database Architecture (MySQL + Safety Fallback)

All student, staff, department, and academic year records are safely stored in **MySQL** (`edusense_db`).

| Table Name | Primary Purpose | Key Fields |
|------------|-----------------|------------|
| `students` | Student academic performance records | `student_id`, `name`, `email`, `department`, `year`, `attendance`, `marks`, `assignment`, `status` |
| `staffs` | Faculty and teaching staff roster | `id`, `name`, `designation`, `department`, `email` |
| `departments` | Academic department branches | `id`, `name`, `code`, `hod` |
| `academic_years` | Active academic terms and batches | `id`, `year_name`, `batch` |
| `settings` | Dynamic threshold rules & API credentials | `setting_key`, `setting_value` |
| `alert_logs` | Audit trail of sent notification emails | `id`, `student_id`, `email`, `message`, `sent_at` |

---

## 👨‍💻 Author & Project Context

- **Author**: Santhosh Raj V
- **Institution**: Jayaraj Annapackiam C. S. I. College of Engineering, Nazareth
- **Department**: Artificial Intelligence & Data Science
- **Course**: CW3551 Data and Information Security (Semester 05)
