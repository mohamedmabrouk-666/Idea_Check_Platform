-- ============================================================
-- schema.sql — Database Structure
-- Run this file once to create all tables from scratch
-- Command: mysql -u root -p similarity_checker < database/schema.sql
-- ============================================================

-- Create the database if it doesn't exist yet
CREATE DATABASE IF NOT EXISTS similarity_checker;
USE similarity_checker;

-- ── Table: users ────────────────────────────────────────────
-- Stores all registered users (students and admins)
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,  -- Unique ID for each user
    name       VARCHAR(100) NOT NULL,            -- Full name of the user
    email      VARCHAR(150) NOT NULL UNIQUE,     -- Email (used for login, must be unique)
    password   VARCHAR(255) NOT NULL,            -- Hashed password (never plain text)
    role       ENUM('student', 'admin') DEFAULT 'student',  -- User type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- When they registered
);

-- ── Table: old_projects ─────────────────────────────────────
-- Stores the database of previous graduation projects
-- This is what new ideas are compared against
CREATE TABLE IF NOT EXISTS old_projects (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,    -- Project title
    description TEXT NOT NULL,            -- Project description (used in NLP)
    department  VARCHAR(100),             -- Engineering department (e.g. Computer, Electrical)
    year        YEAR,                     -- Year the project was submitted
    keywords    VARCHAR(255),             -- Optional keywords for better matching
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Table: submissions ──────────────────────────────────────
-- Stores every idea a student submits for checking
CREATE TABLE IF NOT EXISTS submissions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,           -- Which student submitted this
    title           VARCHAR(255) NOT NULL,  -- Their project title
    description     TEXT NOT NULL,          -- Their project description
    department      VARCHAR(100),           -- Their department
    similarity_score FLOAT DEFAULT 0,       -- The similarity percentage (0 to 100)
    top_matches     TEXT,                   -- JSON string of top 5 similar projects
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Index for faster search ─────────────────────────────────
CREATE INDEX idx_department ON old_projects(department);  -- Speed up department filter
CREATE INDEX idx_year       ON old_projects(year);        -- Speed up year filter
