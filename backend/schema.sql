-- EduSense MySQL Database Schema

CREATE DATABASE IF NOT EXISTS `edusense_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `edusense_db`;

-- Users Table (Dual Role Auth: Staff & Student)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'student', -- 'staff' or 'student'
    `student_id` VARCHAR(50) DEFAULT NULL,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Students Table (Student Identity Profile)
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(50) UNIQUE NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` VARCHAR(50) NOT NULL,
    `phone` VARCHAR(30) DEFAULT '+91 98765 43210',
    `attendance` FLOAT DEFAULT 0,
    `marks` FLOAT DEFAULT 0,
    `assignment` FLOAT DEFAULT 0,
    `status` VARCHAR(20) DEFAULT 'Good',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Student Semester Subject Marks Table (Semesters 1-8)
CREATE TABLE IF NOT EXISTS `student_sem_marks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(50) NOT NULL,
    `sem_no` INT NOT NULL,
    `subject_code` VARCHAR(50) NOT NULL,
    `subject_name` VARCHAR(150) NOT NULL,
    `internal_marks` FLOAT DEFAULT 0,
    `external_marks` FLOAT DEFAULT 0,
    `total_marks` FLOAT DEFAULT 0,
    `grade` VARCHAR(10) DEFAULT 'P',
    `attendance` FLOAT DEFAULT 0,
    `credits` INT DEFAULT 3,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `student_sem_sub` (`student_id`, `sem_no`, `subject_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Student Semester Summary Table (Semesters 1-8 Aggregates)
CREATE TABLE IF NOT EXISTS `student_sem_summary` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(50) NOT NULL,
    `sem_no` INT NOT NULL,
    `total_marks` FLOAT DEFAULT 0,
    `avg_marks` FLOAT DEFAULT 0,
    `sgpa` FLOAT DEFAULT 0,
    `attendance` FLOAT DEFAULT 0,
    `status` VARCHAR(20) DEFAULT 'Pass',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `student_sem` (`student_id`, `sem_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Settings Table
CREATE TABLE IF NOT EXISTS `settings` (
    `setting_key` VARCHAR(50) PRIMARY KEY,
    `setting_value` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Alert Logs Table
CREATE TABLE IF NOT EXISTS `alert_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(50),
    `email` VARCHAR(100),
    `message` TEXT,
    `sent_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Staffs Master Table
CREATE TABLE IF NOT EXISTS `staffs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `designation` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Departments Master Table
CREATE TABLE IF NOT EXISTS `departments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `hod` VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Academic Years Master Table
CREATE TABLE IF NOT EXISTS `academic_years` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `year_name` VARCHAR(100) NOT NULL,
    `batch` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

