-- PostgreSQL schema for CyberShield Lab

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    full_name VARCHAR(150),
    bio TEXT,
    avatar_url TEXT,
    google_url TEXT,
    facebook_url TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS malware_scans (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    username VARCHAR(150),
    filename TEXT,
    size INTEGER,
    sha256 VARCHAR(64),
    md5 VARCHAR(32),
    sha1 VARCHAR(40),
    status VARCHAR(20),
    entropy FLOAT,
    fraud_detected BOOLEAN DEFAULT FALSE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vuln_reports (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    username VARCHAR(150),
    url TEXT,
    report JSONB,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_scam_checks (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    username VARCHAR(150),
    title TEXT,
    content TEXT,
    score INTEGER,
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
