# 🚀 Complete Setup & Deployment Guide

This guide covers running EduSense locally, via Docker, and with Docker Compose.

---

## 1. Running Locally (Development Mode)

### Step 1: Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/vsanthoshraj/Student-Performance-Prediction.git
cd Student-Performance-Prediction

python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### Step 3: Configure Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

*(Optional: Edit `.env` to configure MySQL credentials, Gemini API key, or SMTP email parameters).*

### Step 4: Launch Application

```bash
python run.py
```

- Open **http://localhost:5000** in your browser.
- **Login Credentials**: Username: `admin` | Password: `admin`

---

## 2. Running with Docker Container

EduSense is published as a pre-built Docker image on Docker Hub: **`vsanthoshraj/student-performance-prediction:latest`**.

### Option A: Pull & Run Pre-built Image from Docker Hub

```bash
docker run -d \
  --name edusense_app \
  -p 5000:5000 \
  -e SECRET_KEY="edusense_production_secret" \
  vsanthoshraj/student-performance-prediction:latest
```

### Option B: Build & Run Image Locally

```bash
# Build Docker Image
docker build -t student-performance-prediction:latest .

# Run Container
docker run -d \
  --name edusense_app \
  -p 5000:5000 \
  student-performance-prediction:latest
```

Access the app at **http://localhost:5000**.

---

## 3. Running with Docker Compose (Full Stack with MySQL)

To spin up both the **EduSense Web App** and a dedicated **MySQL 8.0 Database** container simultaneously:

### Step 1: Launch Stack

```bash
docker-compose up -d
```

### Step 2: Check Running Containers

```bash
docker-compose ps
```

### Step 3: View Logs

```bash
docker-compose logs -f web
```

### Step 4: Stop Stack

```bash
docker-compose down
```

Access the application at **http://localhost:5000**.
