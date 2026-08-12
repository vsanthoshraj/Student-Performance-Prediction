# 🚀 Complete Setup & Deployment Guide

This guide covers local development, multi-stage Docker containerization, and multi-service Docker Compose deployment.

---

## 1. Local Development Setup

### Step 1: Clone Repository & Virtual Environment
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

### Step 3: Environment Configuration
Copy environment variable template:
```bash
cp .env.example .env
```
*(Optionally configure `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `GEMINI_API_KEY`, and `SMTP_SERVER` parameters in `.env`).*

### Step 4: Run Application
```bash
sudo python run.py
```
Open **http://<YOUR_VM_IP>** or **http://localhost** in your browser.  
Default login: **`admin`** / **`admin`**.

---

## 2. Docker Container Deployment

EduSense includes an optimized multi-stage `Dockerfile` with non-root security (`appuser` UID 10001) and health checks.

### Build and Run Image
```bash
# Build Docker image
docker build -t student-performance-prediction:latest .

# Run container on Port 80 bound to 0.0.0.0
docker run -d \
  --name edusense_app \
  -p 80:80 \
  -e PORT=80 \
  student-performance-prediction:latest
```

---

## 3. Full-Stack Production Deployment (Docker Compose + MySQL)

To launch the web application alongside a dedicated **MySQL 8.0** database container bound to port 80 on all network interfaces (`0.0.0.0`):

### Launch Stack
```bash
docker-compose up -d --build
```

### Monitor Services & Logs
```bash
docker-compose ps
docker-compose logs -f web
```

### Tear Down Stack
```bash
docker-compose down
```

Access at **http://<YOUR_VM_IP>** (Port 80).

