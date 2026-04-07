# CyberShield Lab

CyberShield Lab is a full-stack cybersecurity operations platform designed to look and feel like a modern Security Operations Center (SOC) dashboard. It combines a **malware analysis lab**, a **website vulnerability scanner**, and a **secure web app demo** with modern UI/UX and security best practices.

--- 


 
## ✅ Key Modules

### 🔬 Module 1 — Malware Analysis Lab

- Upload suspicious files (.exe, .pdf, .doc, .zip, etc.)
- Generate SHA256 / MD5 / SHA1 hashes
- Compare against a malware hash database
- Detect high entropy and suspicious indicators
- Classify files as **SAFE / SUSPICIOUS / MALICIOUS**
- Store scan history in the database
- Download scan report (JSON)

### 🕵️ Module 2 — Website Vulnerability Scanner

- Crawl a target URL for internal links
- Test for:
  - SQL Injection patterns
  - Cross Site Scripting (XSS)
  - Missing security headers (CSP, HSTS, etc.)
  - Open ports on the target host
  - Directory exposure (e.g. /admin, /.git)
  - Basic SSL/TLS certificate validation
- Generate a risk-level dashboard (Low / Medium / High / Critical)

### 🛡️ Module 3 — Secure Web Application Demo

- User registration and login (bcrypt password hashing)
- JWT authentication with expiration
- Role-based access control (user/admin)
- SQL Injection prevention via parameterized queries
- CSRF protection via Flask-WTF
- Rate limiting with Flask-Limiter
- Input validation and secure session handling

---

## 🧱 Tech Stack

- **Frontend:** React.js, Bootstrap 5, Chart.js
- **Backend:** Python Flask (REST API)
- **Database:** PostgreSQL (preferred) or SQLite fallback

---

## 📁 Project Structure

```
frontend/
  public/
  src/
backend/
  api/
    malware.py
    vuln.py
    stats.py
  auth/
    routes.py
  malware_analyzer/
    __init__.py
  scanner/
    vuln_scan.py
  database.py
  extensions.py
  app.py
database/
  schema.sql
  malware_hashes.txt
requirements.txt
README.md
```

---

## 🛠️ Installation Guide

### 1) Clone the repository

```bash
git clone <repo> cybershield
cd cybershield/tools-scanners-website
```

### 2) Backend (Python) Setup

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

### 3) Database Setup

#### PostgreSQL (recommended)

- Set `DATABASE_URL` in `.env`
- Apply schema:

```bash
psql $DATABASE_URL -f database/schema.sql
```

#### SQLite (fallback)

- No configuration needed; the app will create `app.db` automatically.

### 4) Environment variables

Create a `.env` file in the project root (example):

```ini
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### 5) Run Backend

```bash
cd backend
python app.py
```

### 6) Run Frontend

```bash
cd frontend
npm install
npm start
```

### 7) Access

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000/api/...`

---

## 📌 API Overview

### Malware Module

- `POST /api/malware/scan` — upload file and run analysis
- `GET /api/malware/history` — list recent scans
- `GET /api/malware/report/<id>` — fetch/download scan report

### Vulnerability Module

- `POST /api/vuln/scan` — run vulnerability scan for a URL
- `GET /api/vuln/history` — list saved vulnerability reports
- `GET /api/vuln/report/<id>` — retrieve a saved report

### Auth Module

- `POST /api/auth/register` — create a new user
- `POST /api/auth/login` — log in and receive JWT
- `GET /api/auth/me` — current user profile (requires JWT header)
- `GET /api/auth/admin/users` — admin-only endpoint

### Dashboard Stats

- `GET /api/stats/summary` — quick metrics for the dashboard

---

## 🔐 Security & Best Practices (Implemented)

- ✅ File upload validation & secure filenames
- ✅ Hashing & entropy analysis for file inspection
- ✅ JWT auth w/ expiration and role claims
- ✅ Password hashing using bcrypt
- ✅ Parameterized SQL queries (prevents SQL injection)
- ✅ CSRF protection (Flask-WTF)
- ✅ Rate limiting (Flask-Limiter)
- ✅ CORS configuration for safe frontend access
- ✅ Scan result storage and audit logging

---

## 📘 Cybersecurity Concepts

- **Hashing:** One-way fingerprinting (SHA256/MD5/SHA1) to detect known malware.
- **Entropy:** High entropy often indicates compressed/encrypted payloads, common in malware.
- **SQL Injection:** Malicious injection of SQL tokens; prevented with parameterized queries.
- **XSS:** Injection of scripts into pages; mitigated with sanitized output and CSP.
- **Security Headers:** HTTP headers that instruct browsers to enforce security policies.
- **JWT:** Token-based auth; securely sign/verify tokens using a secret.
- **bcrypt:** A secure, adaptive password hashing function.

---

## 🚀 Next Enhancements

- Add pagination + filters for scan history
- Build a full admin dashboard for user management
- Improve scan reporting (PDF / scheduled emails)
- Add real-time alerting and log aggregation
- Expand vulnerability scanner to cover OWASP Top 10

---

This project is intended as a production-quality demo and a learning sandbox for teams building SOC dashboards and cyber tooling.
