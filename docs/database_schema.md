# 🗄️ Database Architecture & Fallback Mechanics

## 🛡️ Multi-Engine Persistent Storage Architecture

EduSense features a database service abstraction (`backend/database.py`) designed for safety, high reliability, and zero-downtime operation. It uses **MySQL Server** (`edusense_db`) as the primary storage engine and incorporates a seamless **SQLite fallback** (`edusense_fallback.db`).

```
                    ┌────────────────────────┐
                    │ Flask API & Services   │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Database.get_conn()    │
                    └───────────┬────────────┘
                                │
             ┌──────────────────┴──────────────────┐
             │ Attempts MySQL Server Connection   │
             └──────────┬─────────────────┬────────┘
         Success        │                 │ Failure
                        ▼                 ▼
             ┌────────────────────┐   ┌─────────────────────────┐
             │ MySQL 8.0 Server   │   │ SQLite Fallback DB      │
             │ (edusense_db)      │   │ (edusense_fallback.db)  │
             └────────────────────┘   └─────────────────────────┘
```

---

## 📋 Database Tables & DDL Schema

### 1. `students` Table
Stores student Demographic details, performance metrics, and evaluation status.

```sql
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    year VARCHAR(50) NOT NULL,
    attendance FLOAT DEFAULT 0,
    marks FLOAT DEFAULT 0,
    assignment FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Good',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2. `staffs` Table
Stores teaching faculty, lab instructors, and departmental designations.

```sql
CREATE TABLE IF NOT EXISTS staffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);
```

### 3. `departments` Table
Stores academic department branches and assigned Head of Department (HOD) faculty.

```sql
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL,
    hod VARCHAR(100) NOT NULL
);
```

### 4. `academic_years` Table
Stores active academic terms and student graduation batches.

```sql
CREATE TABLE IF NOT EXISTS academic_years (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_name VARCHAR(100) NOT NULL,
    batch VARCHAR(50) NOT NULL
);
```

### 5. `settings` Table
Stores dynamic threshold parameters, Gemini API keys, and SMTP configuration.

```sql
CREATE TABLE IF NOT EXISTS settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value TEXT
);
```

### 6. `alert_logs` Table
Audit trail of dispatched warning emails.

```sql
CREATE TABLE IF NOT EXISTS alert_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50),
    email VARCHAR(100),
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
