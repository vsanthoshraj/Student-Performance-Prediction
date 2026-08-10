import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

load_dotenv(os.path.join(ROOT_DIR, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'edusense_super_secret_key_2026')
    TEMPLATE_FOLDER = os.path.join(ROOT_DIR, 'frontend', 'templates')
    STATIC_FOLDER = os.path.join(ROOT_DIR, 'frontend', 'static')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')

    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'edusense_db')

    # Gemini & SMTP Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')

    # Default Rule Thresholds
    ATTENDANCE_THRESHOLD = int(os.getenv('ATTENDANCE_THRESHOLD', 75))
    MARKS_THRESHOLD = int(os.getenv('MARKS_THRESHOLD', 50))
    ASSIGNMENT_THRESHOLD = int(os.getenv('ASSIGNMENT_THRESHOLD', 50))
