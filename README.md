# Gym Trainer Management System (IB CS IA)

A full-stack management web application built for personal trainers to manage clients, session schedules, cancellation/compensation workflows, and payment tracking.

## 🏗 Architecture Overview

- **Frontend:** Streamlit (UI with multi-page navigation)
- **Backend:** FastAPI (RESTful API, Pydantic validation, business rules)
- **Database:** SQLite (`gym_trainer.db`)
- **Data Access:** SQLAlchemy ORM / DDL SQL scripts

---

## 📁 Project Structure

```text
Gym-trainer-management-system-cs-ia/
├── frontend/
│   ├── app.py                 # Streamlit Client Directory & Registration page
│   ├── api_client.py          # API wrapper client for FastAPI endpoints
│   └── pages/
│       ├── dashboard.py       # Trainer dashboard & metrics
│       ├── clients.py         # Client management & profiles
│       ├── schedule.py        # Daily schedule & gym grouping
│       └── payments.py        # Payment status tracking
├── backend/
│   ├── main.py                # FastAPI app entry point (/health & CORS)
│   ├── database.py            # Database connection & SQLAlchemy setup
│   ├── api/
│   │   ├── clients.py         # Implemented: GET /clients & POST /clients
│   │   ├── sessions.py        # Sessions router
│   │   ├── payments.py        # Payments router
│   │   └── dashboard.py       # Dashboard router
│   ├── schemas/
│   │   └── client.py          # Client Pydantic schemas (ClientCreate, ClientResponse)
│   ├── models/
│   │   └── client.py          # Client SQLAlchemy model
│   ├── services/              # Business logic layer
│   └── repositories/          # Data access layer
├── database/
│   ├── schema.sql             # SQLite DDL creation script (Clients, Sessions, Payments)
│   ├── seed.sql               # Seed SQL script (20 clients, 77 sessions, 40 payments)
│   └── schema.md              # Database documentation & Mermaid ERD diagram
├── tests/                     # Automated test suites
├── data/
│   └── seed.py                # Python seed script
├── requirements.txt
├── README.md
└── .env.example
```

---

## 🔌 Implemented APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint returning backend status |
| `GET` | `/clients` | List all clients (supports `?active_only=true`) |
| `POST` | `/clients` | Create a new client record |

---

## 🚀 How to Run

### 1. Initialize Database & Seed Records
```bash
sqlite3 gym_trainer.db < database/schema.sql
sqlite3 gym_trainer.db < database/seed.sql
```

### 2. Start Backend API Server
```bash
uvicorn backend.main:app --reload --port 8000
```
- Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Start Streamlit UI Page
```bash
streamlit run frontend/app.py
```
- Web UI: [http://localhost:8501](http://localhost:8501)
