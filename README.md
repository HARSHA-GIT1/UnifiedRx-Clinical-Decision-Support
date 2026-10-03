# UnifiedRx

**UnifiedRx** is an evidence-driven clinical decision support platform for cross-system medication safety (Allopathic â†” AYUSH) and longitudinal health intelligence.

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
- `POST /register/patient` â€” Register patient, generates unique `URX-P-XXXXXXXX` Health Code, auto-logs in (returns JWT).
- `POST /register/doctor` â€” Register healthcare professional, generates `URX-D-XXXXXXXX` Professional Code (Pending verification), auto-logs in.
- `POST /login` â€” Standard login with email + password (returns JWT).
- `POST /admin/login` â€” Administrator-only login.
- `GET /me` â€” Returns the authenticated user's profile and role-specific details.

### Patient Profile (`/api/v1/patients`)
- `GET /me` â€” Patient views their own profile.
- `GET /{patient_id}/profile` â€” View profile with consent validation (Patient, Approved Doctor, or Admin).

### Access Grants & Consent (`/api/v1/access`)
- `POST /request` â€” Verified doctor requests access using a patient's exact `health_code`.
- `GET /pending` â€” Patient views incoming access requests.
- `POST /{grant_id}/respond` â€” Patient approves (`approve: true`) or denies (`approve: false`).
- `POST /{grant_id}/revoke` â€” Patient revokes an active grant.
- `GET /my-patients` â€” Doctor lists all active patients with approved access.

### Administration (`/api/v1/admin`)
- `PATCH /professionals/{professional_id}/verify` â€” Admin updates doctor verification status (`verified` / `rejected`).
---

## Known Limitations & Environment Notes

### OCR Engine (EasyOCR / PyTorch)

EasyOCR (>=1.7.2) and PyTorch (2.14.0) are installed as dependencies and listed in 
equirements.txt. However, on machines where **Windows Application Control policy** (or equivalent OS security policy) blocks native DLLs — for example, 	orch/lib/shm.dll (WinError 4551) — EasyOCR will fail to initialize at startup. The service detects this failure at Reader() construction time, logs it at ERROR level, and **automatically falls back** to digital PDF text extraction via pypdf only. No crash occurs; processing degrades gracefully.

**Consequence for academic evaluation (Chapters 8–9 / OCR accuracy metrics):**
- Image-based OCR (scanned prescriptions, PNG/JPG uploads) will only produce results on machines where the Application Control policy permits PyTorch DLLs to load. All OCR accuracy measurements in the capstone should clearly state whether they were collected on a policy-unrestricted machine.
- Digital PDF text extraction (text-layer PDFs) is unaffected and works on all machines.

The ENABLE_REAL_OCR_MODELS flag in pp/core/config.py controls mock mode for testing — when unset or False, tests use a monkeypatched extract_text_from_file and do not require a loaded OCR engine.

### No Git History Prior to Phase 2 Completion

The repository was initialized with git init after Phases 1 and 2 were fully verified (10/10 tests passing). The initial commit (eat: Phase 1 and Phase 2 complete) represents the stable, tested baseline. There is no pre-Phase-1 commit history.
