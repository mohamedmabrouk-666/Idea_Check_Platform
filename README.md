# IdeaCheck — Graduation Project Similarity Checker
### Faculty of Engineering

A web platform that allows engineering students to check how similar
their graduation project idea is to previous projects using NLP (Natural Language Processing).

---

## How It Works

1. Student submits a project title and description
2. The system compares it against a database of old projects using **TF-IDF + Cosine Similarity**
3. Returns a similarity percentage with the most similar past projects
4. Provides personalized suggestions to help improve and differentiate the idea

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask |
| Database | MySQL 8 |
| NLP Engine | scikit-learn (TF-IDF + Cosine Similarity) |
| Frontend | HTML + CSS + Vanilla JavaScript |
| PDF Export | ReportLab |
| Security | Flask-WTF (CSRF) + Flask-Limiter (Rate Limiting) |
| Deployment | Docker + docker-compose |

---

## Quick Start — Docker (Recommended)

### Step 1: Clone or extract the project
```bash
cd project-similarity-checker
```

### Step 2: Start the application
```bash
cd docker
docker-compose up --build
```
Wait until you see:
```
web-1 | * Running on http://0.0.0.0:5000
```

### Step 3: Open the browser
```
http://localhost:5000
```

### Step 4: First-time setup
- You will be redirected to `/admin/setup` automatically
- Enter your admin name, email, password
- Enter the **Setup Code**: `ENG-SETUP-2024`
- After setup — the page locks forever

---

## Quick Start — Without Docker

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create the database
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p similarity_checker < database/seed.sql
```

### Step 3: Configure environment
Edit `.env` file:
```
SECRET_KEY=your_random_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DB=similarity_checker
SETUP_CODE=ENG-SETUP-2024
```

### Step 4: Run the app
```bash
python app.py
```
Open: `http://localhost:5000`

---

## All Routes

| Route | Who Can Access | Description |
|---|---|---|
| `/` | Everyone | Landing page |
| `/register` | Visitors | Create student account |
| `/login` | Visitors | Log in |
| `/logout` | Logged in | Log out |
| `/check` | Students | Submit project idea |
| `/result/<id>` | Students | View similarity result |
| `/result/<id>/pdf` | Students | Download result as PDF |
| `/history` | Students | View past submissions |
| `/admin/setup` | First run only | Create first admin account |
| `/admin/dashboard` | Admin | Statistics overview |
| `/admin/projects` | Admin | Manage old projects database |
| `/admin/projects/add` | Admin | Add new project |
| `/admin/projects/edit/<id>` | Admin | Edit existing project |
| `/admin/projects/delete/<id>` | Admin | Delete project |

---

## Default Setup Code
```
ENG-SETUP-2024
```
> Change this in `docker-compose.yml` or `.env` before delivering to the university.

---

## Reset Everything (Start Fresh)
```bash
docker-compose down -v    # Stops containers AND deletes all data
docker-compose up --build # Rebuilds and starts fresh
```
After this you will need to go through the setup page again.

---

## Project Structure
```
project-similarity-checker/
├── app.py                  Main Flask app
├── config.py               Configuration
├── requirements.txt        Dependencies
├── .env                    Environment variables
├── database/
│   ├── schema.sql          Database tables
│   └── seed.sql            Sample old projects (25 projects)
├── core/
│   ├── similarity.py       TF-IDF + Cosine Similarity engine
│   ├── suggestions.py      Score-based advice generator
│   └── pdf_generator.py    PDF report builder
├── routes/
│   ├── auth.py             Login / Register / Logout
│   ├── student.py          Check / Result / History / PDF
│   └── admin.py            Dashboard / Projects / Setup
├── templates/              All HTML pages
├── static/                 CSS + JavaScript
└── docker/                 Dockerfile + docker-compose
```

---

## Sprints Completed

| Sprint | Feature |
|---|---|
| 1 | Foundation — structure, DB, Docker |
| 2 | Authentication — register, login, logout |
| 3 | NLP Core — TF-IDF + cosine similarity |
| 4 | Suggestions — score-based advice |
| 5 | Admin Panel — dashboard + project management |
| 6 | Student UI — check form, result, history |
| 7 | CSS Theme — engineering design |
| 8 | Setup Page — first-time admin creation |
| 9 | Edit Project — update existing projects |
| 10 | Security — download result report |
| 13 | Final Polish — README, Docker healthcheck |
 — CSRF, rate limiting, error pages |
| 11 | Performance — TF-IDF cache system |
| 12 | PDF Export
---

Built with Flask & scikit-learn — Faculty of Engineering Graduation Project
