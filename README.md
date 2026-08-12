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
    �| Layer | Technology & Tools |
|-------|-------------------|
| **Web Server / Reverse Proxy** | **NGINX 1.25** (Reverse Proxy, SSL/TLS Termination, Gzip Compression, Request Buffering) |
| **Typography & UI** | **Plus Jakarta Sans**, Modern Glassmorphic Design System, HSL Color Palettes, Micro-animations |
| **Frontend Framework** | HTML5, Vanilla CSS3, JavaScript (ES6+), Chart.js 4.x, Lucide Vector Icons |
| **Backend API & WSGI** | Python 3.10+, Flask REST API framework, **Gunicorn** production WSGI server |
| **Database** | MySQL 8.0 (PyMySQL with automatic zero-downtime SQLite fallback) |
| **AI Reasoning Engine**| Google Gemini API (`gemini-2.5-flash`) with offline rule engine fallback |
| **Email Dispatcher** | Python `smtplib`, `email.mime` (TLS/SSL multi-provider support) |
| **Data Ingestion** | Pandas, OpenPyXL (Multi-sheet markbook parser) |
| **Containerization** | Multi-container production stack (`nginx` + `web` + `db`) with multi-stage `Dockerfile` |

---

## 📁 Project Structure

```
Student-Performance-Prediction/
├── run.py                          # Application entry point (Gunicorn / Flask)
├── Dockerfile                      # Multi-stage production build for Flask app
├── docker-compose.yml              # Multi-container stack (Nginx + Flask + MySQL 8.0)
├── .dockerignore                   # Excludes build context noise & virtual environments
├── README.md                       # Main documentation guide
│
├── nginx/                          # Nginx Web Server Configuration
│   ├── default.conf                # Reverse proxy config (Port 80 -> Port 5000)
│   └── Dockerfile                  # Nginx Docker image build spec
│
├── frontend/                       # Web UI Layer
│   ├── templates/                  # Jinja2 templates (dashboard, alerts, settings, etc.)
│   └── static/                     # CSS design system & JavaScript modules
│
├── backend/                        # Core Engine & Services
│   ├── app.py                      # Flask routes & REST endpoints
│   ├── config.py                   # System configuration & environment paths
│   ├── database.py                 # MySQL persistent layer with SQLite fallback
│   ├── schema.sql                  # MySQL database DDL definitions
│   ├── requirements.txt            # Python dependencies (Flask, Gunicorn, PyMySQL)
│   └── services/                   # Excel parsing, Risk evaluation, Gemini AI, Email services
│
└── docs/                           # Technical documentation suite
```

---

## 🚀 Quick Start & Deployment

### 1. Multi-Container Production Stack with Nginx (Docker Compose)

Spin up the entire stack—**NGINX Web Server**, **EduSense Application**, and persistent **MySQL 8.0 Database**:

```bash
# Clone repository
git clone https://github.com/vsanthoshraj/Student-Performance-Prediction.git
cd Student-Performance-Prediction

# Build and launch background services (Nginx on Port 80, App on Port 5000, MySQL on 3306)
docker-compose up -d --build

# Verify container status and health
docker-compose ps
```
Access at: **`http://<YOUR_SERVER_IP>`** or **`http://localhost`** (Port 80).

### 2. Pulling and Running Pre-Built Images from Docker Hub

```bash
# Pull web app & nginx images from Docker Hub
docker pull vsanthoshraj/student-performance-prediction:latest
docker pull vsanthoshraj/student-performance-prediction-nginx:latest

# Run using docker-compose
docker-compose up -d
```
txt

# Start application (requires sudo on Linux for port 80, or set PORT env)
sudo python run.py
```
Access at: **`http://localhost`** or **`http://<YOUR_VM_IP>`** (Port 80) | Default Login: `admin` / `admin`.

---

### 2. Multi-Container Production Stack (Docker Compose on VM)

Spin up both the **EduSense Web Application** and a persistent **MySQL 8.0 Database** container bound to `0.0.0.0:80`:

```bash
# Build and launch background services on Port 80
docker-compose up -d --build

# Verify container health
docker-compose ps
```
Access at: **`http://<YOUR_VM_IP>`** (Port 80).


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
