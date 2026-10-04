# Technical Documentation Report: Client Management Module

**Project:** Gym Trainer Management System (IB CS IA)  
**Module:** Client APIs & Streamlit Frontend UI Integration  
**Date:** October 2, 2026  

---

## 1. Executive Summary

This report documents the design, architecture, validation logic, and end-to-end data flow for the **Client Management Module**. This module connects a **Streamlit** multi-tab frontend interface with a **FastAPI** RESTful backend operating over an **SQLite** database (`gym_trainer.db`).

The module supports three core client business workflows:
1. **Fetching Client Roster (`GET /clients`)**: Displays all registered clients with optional active status filtering and real-time name searching.
2. **Registering a Client (`POST /clients`)**: Validates input data (strict 10-digit phone validation, email format checking, non-empty name validation) and persists new client records in SQLite.
3. **Inspecting Client Details (`GET /clients/{client_id}`)**: Fetches details for an individual client record by ID, raising HTTP 404 if the record is missing.

---

## 2. End-to-End System Architecture & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor Trainer as User (Trainer)
    participant UI as Streamlit UI (frontend/app.py)
    participant APIClient as HTTP Client (frontend/api_client.py)
    participant API as FastAPI App (backend/main.py)
    participant Router as Client Router (backend/api/clients.py)
    participant Schema as Pydantic Validator (backend/schemas/client.py)
    participant ORM as SQLAlchemy Model (backend/models/client.py)
    participant DB as SQLite DB (gym_trainer.db)

    Note over Trainer, DB: Flow 1: Registering a New Client (POST /clients)
    Trainer->>UI: Fills Add Client form & clicks "Add Client"
    UI->>UI: Client-side validation (phone regex & length, email format)
    UI->>APIClient: create_client(name, phone, email, active)
    APIClient->>API: HTTP POST /clients {json_payload}
    API->>Router: Route request to create_client endpoint
    Router->>Schema: Instantiate ClientCreate(payload)
    alt Validation Failed (Invalid phone / email / empty name)
        Schema-->>Router: Raise ValueError
        Router-->>APIClient: HTTP 422 Unprocessable Entity
        APIClient-->>UI: Raise clean ValueError
        UI-->>Trainer: Render Error Banner (below form)
    else Validation Passed
        Schema-->>Router: Validated Pydantic object
        Router->>ORM: Instantiate Client(name, phone, email, active)
        Router->>DB: db.add() & db.commit()
        DB-->>Router: Return inserted record with generated ID
        Router-->>APIClient: HTTP 201 Created {ClientResponse JSON}
        APIClient-->>UI: Return client dict
        UI-->>Trainer: Render Success Banner (below form) & update metrics
    end

    Note over Trainer, DB: Flow 2: Viewing Client Directory (GET /clients)
    Trainer->>UI: Opens Client Directory tab
    UI->>APIClient: get_clients(active_only=False)
    APIClient->>API: HTTP GET /clients?active_only=false
    API->>Router: Route request to list_clients endpoint
    Router->>DB: db.query(Client).order_by(Client.id.asc()).all()
    DB-->>Router: Return list of Client ORM instances
    Router->>Schema: Serialize using ClientResponse
    Router-->>APIClient: HTTP 200 OK [ClientResponse list]
    APIClient-->>UI: List of client dicts
    UI-->>Trainer: Render DataFrame Table & Update Metric Cards

    Note over Trainer, DB: Flow 3: Client Details Lookup (GET /clients/{client_id})
    Trainer->>UI: Selects Client or Enters ID & clicks "Fetch Client Details"
    UI->>APIClient: get_client(client_id)
    APIClient->>API: HTTP GET /clients/{client_id}
    API->>Router: Route request to get_client endpoint
    Router->>DB: db.query(Client).filter(Client.id == client_id).first()
    alt Client Not Found
        DB-->>Router: Return None
        Router-->>APIClient: HTTP 404 Not Found {"detail": "Client with ID #X not found."}
        APIClient-->>UI: Raise ValueError("Client with ID #X not found.")
        UI-->>Trainer: Render Error Banner
    else Client Found
        DB-->>Router: Return Client ORM Instance
        Router->>Schema: Serialize using ClientResponse
        Router-->>APIClient: HTTP 200 OK {ClientResponse JSON}
        APIClient-->>UI: Return client detail dict
        UI-->>Trainer: Render Profile Summary Card
    end
```

---

## 3. Implemented File Matrix

| File Path | Component | Responsibility & Changes Implemented |
|-----------|-----------|---------------------------------------|
| `backend/database.py` | Database Engine | Configured SQLAlchemy SQLite engine, session factory (`SessionLocal`), and FastAPI `get_db()` yield dependency. |
| `backend/models/client.py` | ORM Model | Defined `Client` SQLAlchemy model mapped to `clients` table columns (`id`, `name`, `phone`, `email`, `active`, `created_at`, `updated_at`). |
| `backend/schemas/client.py` | Pydantic Schemas | Implemented `ClientBase`, `ClientCreate`, and `ClientResponse` Pydantic v2 schemas with strict field validators. |
| `backend/api/clients.py` | API Router | Implemented `GET /clients` (with `?active_only` filtering), `GET /clients/{client_id}` (single client lookup / 404 handling), and `POST /clients` with `try...except db.rollback()` error safety. |
| `backend/main.py` | FastAPI Application | Configured FastAPI app, CORS middleware, and `/health` health-check endpoint. |
| `frontend/api_client.py` | HTTP Helper | Implemented `check_health()`, `get_clients()`, `get_client()`, and `create_client()` functions using `requests` with clean error detail parsing. |
| `frontend/app.py` | Streamlit UI | Primary multi-tab UI page containing health status badge, client roster table, search filter, metric cards, registration form, and Client Details profile lookup card (Tab 3). |
| `database/schema.sql` | SQL DDL Script | SQLite table definitions for `clients`, `sessions`, and `payments` tables with `created_at` and `updated_at` timestamps. |
| `database/seed.sql` | SQL Seed Script | Seed data containing 20 clients, 77 workout sessions (scheduled, completed, cancelled, compensation), and 40 payment records. |

---

## 4. Key Design Decisions & Validation Logic

### A. Single Client Lookup & 404 Error Handling
- **API Endpoint**: `GET /clients/{client_id}` queries SQLite by primary key. If no matching record is found, it returns `HTTP 404 Not Found` with detail `"Client with ID #{client_id} not found."`.
- **Frontend Integration**: Tab 3 ("Client Details (GET /clients/{client_id})") allows trainers to select from a dropdown of existing roster clients or enter an ID manually. It displays a formatted Profile Summary Card upon success or an inline error banner if 404 occurs.

### B. Pydantic Schema Separation (`ClientCreate` vs. `ClientResponse`)
- **`ClientCreate`**: Inherits from `ClientBase` and enforces `@field_validator` checks exclusively during **new record creation**:
  - **Name Validator**: Rejects empty strings or whitespace-only names.
  - **Phone Validator**: Uses regex `^\+?[0-9\s\-()]{7,15}$` to reject letters/alphabets. Strips country code prefixes (`+91`, `+1`, `+44`) and verifies that the core number is **exactly 10 digits**.
  - **Email Validator**: Uses regex `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$` to verify standard email format.
- **`ClientResponse`**: Inherits from `ClientBase` without input creation validation rules, allowing existing database rows to serialize cleanly to JSON.

---

## 5. Summary of API Endpoints

```http
### 1. Health Check
GET /health
Response 200 OK:
{
  "status": "healthy",
  "service": "Gym Trainer API"
}

### 2. List Clients
GET /clients?active_only=false
Response 200 OK:
[
  {
    "id": 1,
    "name": "Alex Johnson",
    "phone": "5550101",
    "email": "alex.j@example.com",
    "active": true,
    "created_at": "2026-08-01T09:00:00",
    "updated_at": "2026-08-01T09:00:00"
  }
]

### 3. Get Single Client Details
GET /clients/1
Response 200 OK:
{
  "id": 1,
  "name": "Alex Johnson",
  "phone": "5550101",
  "email": "alex.j@example.com",
  "active": true,
  "created_at": "2026-08-01T09:00:00",
  "updated_at": "2026-08-01T09:00:00"
}

GET /clients/9999
Response 404 Not Found:
{
  "detail": "Client with ID #9999 not found."
}

### 4. Create Client
POST /clients
Content-Type: application/json
{
  "name": "Nandani Mishra",
  "phone": "8928376353",
  "email": "nandani@gmail.com",
  "active": true
}

Response 201 Created:
{
  "id": 21,
  "name": "Nandani Mishra",
  "phone": "8928376353",
  "email": "nandani@gmail.com",
  "active": true,
  "created_at": "2026-09-19T18:40:00",
  "updated_at": "2026-09-19T18:40:00"
}
```
