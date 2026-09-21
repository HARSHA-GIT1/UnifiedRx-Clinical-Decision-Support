# UnifiedRx

**UnifiedRx** is an evidence-driven clinical decision support platform for cross-system medication safety (Allopathic ↔ AYUSH) and longitudinal health intelligence.

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI (Async), SQLAlchemy 2.0 (Async / asyncpg), Alembic, Pydantic v2
- **Database**: PostgreSQL 16
- **Auth**: JWT (OAuth2 Bearer) + Passlib (bcrypt)
- **Containerization**: Docker & Docker Compose
- **Future AI / Intelligence Components**: PaddleOCR, spaCy / MedSpaCy, Ollama (Gemma / Llama / Mistral)

---

## Quickstart & Local Setup

### 1. Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed.
- Python 3.11+ (if running locally outside Docker).

### 2. Environment Configuration
Ensure `.env` exists at the root (copied from `.env.example`):
```bash
cp .env.example .env
```
Review the environment variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string (asyncpg driver)
- `SECRET_KEY`: Secret string used for signing JWTs
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens (default: 60)
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`: Default credentials for the seeded administrator account

---

## Running with Docker Compose

### 1. Start the Database and Backend
```bash
docker compose up -d
```

### 2. Apply Database Migrations (All 15 Tables)
```bash
docker compose exec backend alembic upgrade head
```

### 3. Seed Initial Administrator Account
```bash
docker compose exec backend python -m app.scripts.seed_admin
```

### 4. Access Interactive API Documentation
Once running, open your browser:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Running Locally (Without Docker)

### 1. Create and Activate Virtual Environment
```bash
cd backend
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Seed Administrator
```bash
python -m app.scripts.seed_admin
```

### 5. Start the FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API Overview (Phase 1)

### Authentication (`/api/v1/auth`)
- `POST /register/patient` — Register patient, generates unique `URX-P-XXXXXXXX` Health Code, auto-logs in (returns JWT).
- `POST /register/doctor` — Register healthcare professional, generates `URX-D-XXXXXXXX` Professional Code (Pending verification), auto-logs in.
- `POST /login` — Standard login with email + password (returns JWT).
- `POST /admin/login` — Administrator-only login.
- `GET /me` — Returns the authenticated user's profile and role-specific details.

### Patient Profile (`/api/v1/patients`)
- `GET /me` — Patient views their own profile.
- `GET /{patient_id}/profile` — View profile with consent validation (Patient, Approved Doctor, or Admin).

### Access Grants & Consent (`/api/v1/access`)
- `POST /request` — Verified doctor requests access using a patient's exact `health_code`.
- `GET /pending` — Patient views incoming access requests.
- `POST /{grant_id}/respond` — Patient approves (`approve: true`) or denies (`approve: false`).
- `POST /{grant_id}/revoke` — Patient revokes an active grant.
- `GET /my-patients` — Doctor lists all active patients with approved access.

### Administration (`/api/v1/admin`)
- `PATCH /professionals/{professional_id}/verify` — Admin updates doctor verification status (`verified` / `rejected`).
