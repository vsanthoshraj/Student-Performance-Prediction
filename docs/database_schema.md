# 🗄️ Database Architecture & Fallback Mechanics

## 🛡️ Transparent Multi-Engine Architecture

EduSense implements a resilient database abstraction layer in `backend/database.py`. It prioritizes **MySQL Server** for production durability, while incorporating an automatic, zero-configuration **SQLite fallback** to ensure zero downtime during vivas or offline deployments.

```
                  ┌──────────────────────┐
                  │ Flask Request / Service│
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Database.get_conn()  │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            │ Attempts MySQL Connection      │
            └────────┬───────────────┬────────┘
        Success      │               │ Failure
                     ▼               ▼
           ┌────────────────┐  ┌─────────────────────┐
           │ MySQL Database │  │ SQLite Fallback DB  │
           │ (edusense_db)  │  │ (edusense_fallback) │
           └────────────────┘  └─────────────────────┘
```

---

## 📋 Database Tables DDL

### 1. `students` Table

Stores student demographic data, performance scores, and rule-evaluated status.

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

### 2. `settings` Table

Stores dynamic threshold configurations, Gemini API keys, and SMTP server details.

```sql
CREATE TABLE IF NOT EXISTS settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value TEXT
);
```

### 3. `alert_logs` Table

Records an audit trail of dispatched SMTP email alerts.

```sql
CREATE TABLE IF NOT EXISTS alert_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50),
    email VARCHAR(100),
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
