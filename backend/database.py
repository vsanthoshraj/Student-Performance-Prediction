import os
import pymysql
import json
import sqlite3
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.db_name = os.getenv('MYSQL_DATABASE', 'edusense_db')
        self.use_mysql = True
        self.sqlite_fallback_path = os.path.join(os.path.dirname(__file__), 'data', 'edusense_fallback.db')

    def get_connection(self):
        """
        Attempts to connect to MySQL. If MySQL is unreachable, seamlessly
        falls back to SQLite so the application never crashes during viva demos.
        """
        if self.use_mysql:
            try:
                # First connect without DB to ensure DB exists
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    autocommit=True
                )
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_name}` DEFAULT CHARACTER SET utf8mb4;")
                conn.close()

                # Reconnect to target database
                return pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.db_name,
                    autocommit=True,
                    cursorclass=pymysql.cursors.DictCursor
                )
            except Exception as e:
                print(f"[Database Warning] MySQL connection failed ({e}). Falling back to SQLite database.")
                self.use_mysql = False

        # Fallback SQLite connection
        os.makedirs(os.path.dirname(self.sqlite_fallback_path), exist_ok=True)
        conn = sqlite3.connect(self.sqlite_fallback_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """
        Creates required tables: `students`, `settings`, `alert_logs`.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS settings (
                            setting_key VARCHAR(50) PRIMARY KEY,
                            setting_value TEXT
                        );
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS alert_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            student_id VARCHAR(50),
                            email VARCHAR(100),
                            message TEXT,
                            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
            else:
                with conn:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS students (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id TEXT UNIQUE NOT NULL,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            department TEXT NOT NULL,
                            year TEXT NOT NULL,
                            attendance REAL DEFAULT 0,
                            marks REAL DEFAULT 0,
                            assignment REAL DEFAULT 0,
                            status TEXT DEFAULT 'Good'
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS settings (
                            setting_key TEXT PRIMARY KEY,
                            setting_value TEXT
                        );
                    """)
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS alert_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id TEXT,
                            email TEXT,
                            message TEXT,
                            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
        finally:
            conn.close()

    def clear_students(self):
        """
        Removes ALL student records from the database.
        Used to ensure only real, official data is present.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM students;")
            else:
                with conn:
                    conn.execute("DELETE FROM students;")
        finally:
            conn.close()

    def save_students(self, students_list):
        """
        Saves or updates student records in MySQL DB.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    for s in students_list:
                        cursor.execute("""
                            INSERT INTO students (student_id, name, email, department, year, attendance, marks, assignment, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                name=VALUES(name), email=VALUES(email), department=VALUES(department),
                                year=VALUES(year), attendance=VALUES(attendance), marks=VALUES(marks),
                                assignment=VALUES(assignment), status=VALUES(status);
                        """, (
                            str(s.get('Student ID')), str(s.get('Name')), str(s.get('Email')),
                            str(s.get('Department')), str(s.get('Year')), float(s.get('Attendance', 0)),
                            float(s.get('Marks', 0)), float(s.get('Assignment', 0)), str(s.get('Status', 'Good'))
                        ))
            else:
                with conn:
                    for s in students_list:
                        conn.execute("""
                            INSERT OR REPLACE INTO students (student_id, name, email, department, year, attendance, marks, assignment, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            str(s.get('Student ID')), str(s.get('Name')), str(s.get('Email')),
                            str(s.get('Department')), str(s.get('Year')), float(s.get('Attendance', 0)),
                            float(s.get('Marks', 0)), float(s.get('Assignment', 0)), str(s.get('Status', 'Good'))
                        ))
        finally:
            conn.close()

    def get_students(self):
        """
        Fetches all student records from DB.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT student_id as `Student ID`, name as `Name`, email as `Email`, department as `Department`, year as `Year`, attendance as `Attendance`, marks as `Marks`, assignment as `Assignment`, status as `Status` FROM students ORDER BY id ASC;")
                    return cursor.fetchall()
            else:
                cursor = conn.execute("SELECT student_id as 'Student ID', name as 'Name', email as 'Email', department as 'Department', year as 'Year', attendance as 'Attendance', marks as 'Marks', assignment as 'Assignment', status as 'Status' FROM students ORDER BY id ASC;")
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_student_by_id(self, student_id):
        """
        Fetches single student record by Student ID.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT student_id as `Student ID`, name as `Name`, email as `Email`, department as `Department`, year as `Year`, attendance as `Attendance`, marks as `Marks`, assignment as `Assignment`, status as `Status` FROM students WHERE student_id = %s;", (str(student_id),))
                    return cursor.fetchone()
            else:
                cursor = conn.execute("SELECT student_id as 'Student ID', name as 'Name', email as 'Email', department as 'Department', year as 'Year', attendance as 'Attendance', marks as 'Marks', assignment as 'Assignment', status as 'Status' FROM students WHERE student_id = ?;", (str(student_id),))
                row = cursor.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    def get_settings(self):
        """
        Retrieves all key-value settings from DB.
        """
        conn = self.get_connection()
        settings_dict = {}
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT setting_key, setting_value FROM settings;")
                    for r in cursor.fetchall():
                        settings_dict[r['setting_key']] = r['setting_value']
            else:
                cursor = conn.execute("SELECT setting_key, setting_value FROM settings;")
                for r in cursor.fetchall():
                    settings_dict[r['setting_key']] = r['setting_value']
        finally:
            conn.close()
        return settings_dict

    def save_setting(self, key, value):
        """
        Saves a key-value setting into DB.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value);", (key, str(value)))
            else:
                with conn:
                    conn.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?);", (key, str(value)))
        finally:
            conn.close()

    def log_alert(self, student_id, email, message):
        """
        Logs sent alert to alert_logs table.
        """
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO alert_logs (student_id, email, message) VALUES (%s, %s, %s);", (str(student_id), str(email), str(message)))
            else:
                with conn:
                    conn.execute("INSERT INTO alert_logs (student_id, email, message) VALUES (?, ?, ?);", (str(student_id), str(email), str(message)))
        finally:
            conn.close()

db = Database()
