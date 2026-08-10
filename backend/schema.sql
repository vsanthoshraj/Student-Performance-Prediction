-- EduSense MySQL Database Schema

CREATE DATABASE IF NOT EXISTS `edusense_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `edusense_db`;

-- Students Table
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` VARCHAR(50) UNIQUE NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` VARCHAR(50) NOT NULL,
    `attendance` FLOAT DEFAULT 0,
    `marks` FLOAT DEFAULT 0,
    `assignment` FLOAT DEFAULT 0,
    `status` VARCHAR(20) DEFAULT 'Good',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
