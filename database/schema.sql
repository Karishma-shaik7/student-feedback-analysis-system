-- ==============================================================================
-- DATABASE SCHEMA: Student Feedback Analysis System
-- Target Database: student_feedback_db
-- Engine: InnoDB | Charset: utf8mb4 | Collation: utf8mb4_unicode_ci
-- ==============================================================================

-- 1. Create Database if not exists
CREATE DATABASE IF NOT EXISTS student_feedback_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_feedback_db;

-- 2. Create Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    instructor_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL DEFAULT 'Computer Science',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_course_code (course_code),
    INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Create Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    rating TINYINT NOT NULL,
    comment TEXT NULL,
    student_name VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_feedback_rating
        CHECK (rating >= 1 AND rating <= 5),
    INDEX idx_feedback_course_id (course_id),
    INDEX idx_feedback_rating (rating),
    INDEX idx_feedback_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Seed Initial Sample Courses (Only inserted if course_code doesn't already exist)
-- Note: No fake student feedback is inserted here, keeping analytics completely clean.
INSERT IGNORE INTO courses (course_code, course_name, instructor_name, department) VALUES
('CS101', 'Introduction to Computer Science', 'Dr. Alan Turing', 'Computer Science'),
('CS201', 'Data Structures and Algorithms', 'Dr. Ada Lovelace', 'Computer Science'),
('CS301', 'Database Management Systems', 'Dr. Edgar Codd', 'Data Science & Databases'),
('CS401', 'Web Architecture & Cloud Engineering', 'Prof. Tim Berners-Lee', 'Software Engineering'),
('CS501', 'Artificial Intelligence & Deep Learning', 'Dr. Geoffrey Hinton', 'Artificial Intelligence'),
('CS601', 'Software Engineering Practices & DevOps', 'Prof. Margaret Hamilton', 'Software Engineering');
