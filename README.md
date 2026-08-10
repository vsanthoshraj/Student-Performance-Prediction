# 🎓 EduSense — AI Student Performance Monitoring & Early Alert System

> **Jayaraj Annapackiam C. S. I. College of Engineering, Nazareth**  
> Department of Artificial Intelligence and Data Science  
> Course: **CW3551 Data and Information Security** | Batch: **2023–2027** | Sem: **05**  
> Instructor: **G. Alisha Evangeline, AP/ADS**

---

## 📌 Project Overview

**EduSense** is a production-quality web application that monitors student academic performance, detects at-risk students using rule-based evaluation, provides AI-powered insights via Google Gemini, and dispatches automated SMTP email alerts — all from a single uploaded Excel markbook.

### Core Workflow

```
Upload Excel Markbook → Parse & Store in MySQL → Dashboard Analytics
→ Rule-Based Risk Detection → Gemini AI Chatbot → SMTP Email Alerts
```

---

## 🖥️ Screenshots

| Dashboard | Student Directory | AI Chatbot |
|-----------|-------------------|------------|
| KPI cards, Charts, At-Risk table | Searchable, filterable student list | Natural language dataset queries |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3 (Apple Design System), JavaScript, Chart.js, Lucide Icons |
| **Backend** | Python, Flask |
| **Database** | MySQL (with automatic SQLite fallback) |
| **AI Engine** | Google Gemini API (gemini-2.5-flash) |
| **Email** | SMTP (Gmail / configurable) |
| **Data Processing** | Pandas, OpenPyXL |

---

## 📁 Project Structure

```
Student-Performance-Prediction/
├── run.py                          # Root launcher script
├── .env                            # Environment configuration
├── .env.example                    # Template for environment variables
├── README.md
│
├── frontend/                       # UI Layer
│   ├── templates/
│   │   ├── base.html               # Master layout + AI chatbot drawer
│   │   ├── login.html              # Sign-in page
│   │   ├── dashboard.html          # KPI overview + Chart.js charts
│   │   ├── students.html           # Searchable student directory
│   │   ├── analytics.html          # Score distributions + dept matrix
│   │   ├── alerts.html             # Email alert management
│   │   ├── settings.html           # Thresholds & API configuration
│   │   └── upload.html             # Drag-and-drop Excel import
│   └── static/
│       ├── css/style.css           # Apple-inspired design system
│       └── js/
│           ├── dashboard.js        # Charts, modals, filters
│           └── chatbot.js          # Floating AI assistant controller
│
├── backend/                        # Business Logic Layer
│   ├── app.py                      # Flask server + REST API routes
│   ├── config.py                   # Environment & path configuration
│   ├── database.py                 # MySQL + SQLite fallback engine
│   ├── schema.sql                  # MySQL DDL script
│   ├── requirements.txt            # Python dependencies
│   ├── data/                       # Real dataset + fallback DB
│   │   └── Document from Santhosh Raj V.xlsx
│   ├── uploads/                    # User-uploaded Excel files
│   └── services/
│       ├── excel_service.py        # Multi-sheet markbook parser
│       ├── risk_service.py         # Rule-based risk evaluator
│       ├── gemini_service.py       # Gemini AI + offline fallback
│       └── email_service.py        # SMTP alert dispatcher
│
└── Document from Santhosh Raj V.xlsx   # Original source data
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- MySQL Server (optional — app auto-falls back to SQLite)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vsanthoshraj/Student-Performance-Prediction.git
cd Student-Performance-Prediction

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Configure environment (optional)
cp .env.example .env
# Edit .env with your MySQL, Gemini API, and SMTP credentials

# 5. Run the application
python run.py
```

### Access
- **URL**: http://localhost:5000
- **Login**: Username: `admin` | Password: `admin`

---

## 🗄️ Database

### MySQL Configuration
Set these in your `.env` file:
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=edusense_db
```

### Auto-Fallback
If MySQL is unavailable, EduSense automatically uses an embedded **SQLite** database (`backend/data/edusense_fallback.db`). This ensures the app **never crashes** during live demonstrations.

### Schema (3 tables)
| Table | Purpose |
|-------|---------|
| `students` | Student records (ID, name, email, dept, attendance, marks, assignment, status) |
| `settings` | Dynamic threshold parameters and API credentials |
| `alert_logs` | Email dispatch audit trail |

---

## 📊 Features

### 1. Excel Markbook Parser
- Supports **multi-sheet college markbooks** (I1, I2, I3, RUBRICS, IAT-REPORT)
- Also supports standard flat Excel files with column headers
- Auto-detects format and extracts student data

### 2. Rule-Based Risk Detection
Students are classified using configurable thresholds:
| Status | Condition |
|--------|-----------|
| **At Risk** | Attendance < 75% AND Marks < 50 |
| **Warning** | Attendance < 75% OR Marks < 50 |
| **Good** | All metrics above thresholds |

### 3. AI-Powered Chatbot (Gemini)
- Natural language queries: *"Which students are at risk?"*, *"Who scored highest?"*
- Answers strictly from loaded dataset — no hallucination
- Falls back to built-in analytics engine if API key is absent

### 4. SMTP Email Alerts
- Individual or bulk email dispatch to at-risk students
- Configurable SMTP server (Gmail, Outlook, etc.)
- Alert logs stored in database

### 5. Interactive Dashboard
- KPI cards (Total, Good, Warning, At Risk)
- Performance distribution donut chart
- Attendance distribution bar chart
- Department-wise risk breakdown

---

## 📋 Dataset

This project uses **real academic data** from:
- **College**: Jayaraj Annapackiam C. S. I. College of Engineering
- **Course**: CW3551 Data and Information Security
- **Class**: III ADS (57 students)
- **Batch**: 2023–2027
- **Semester**: 05 (Odd Sem, AY 2025–26)

The data is sourced from the official markbook: `Document from Santhosh Raj V.xlsx`

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | `edusense_super_secret_key_2026` |
| `MYSQL_HOST` | MySQL server host | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | *(empty)* |
| `MYSQL_DATABASE` | MySQL database name | `edusense_db` |
| `GEMINI_API_KEY` | Google Gemini API key | *(optional)* |
| `SMTP_SERVER` | SMTP mail server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USERNAME` | SMTP login email | *(optional)* |
| `SMTP_PASSWORD` | SMTP app password | *(optional)* |
| `SENDER_EMAIL` | Sender email address | *(optional)* |
| `ATTENDANCE_THRESHOLD` | Risk threshold for attendance | `75` |
| `MARKS_THRESHOLD` | Risk threshold for marks | `50` |
| `ASSIGNMENT_THRESHOLD` | Risk threshold for assignment | `50` |

---

## 👨‍💻 Author

**Santhosh Raj V**  
Department of AI & Data Science  
Jayaraj Annapackiam C. S. I. College of Engineering, Nazareth

---

## 📄 License

This project is developed as a final-year academic project. All rights reserved.
