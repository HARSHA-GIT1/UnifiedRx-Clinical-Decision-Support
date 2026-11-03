# UnifiedRx – An Evidence-Driven Clinical Decision Support Platform for Cross-System Medication Safety and Longitudinal Health Intelligence

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.2.8-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3.0-646CFF.svg)](https://vite.dev/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0.35%20Async-D71F00.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Academic%20Prototype-gray.svg)]()

---

## Academic Project Information

**UnifiedRx** is an MCA (Master of Computer Applications) final-year academic capstone project. It is conceptualized, designed, and developed to address the critical clinical safety challenge of fragmented medication records and unmonitored cross-system polypharmacy (Allopathic and AYUSH regimens).

> [!IMPORTANT]
> **Clinical Disclaimer**: UnifiedRx is an academic clinical decision support prototype developed for educational and research evaluation purposes only. It does **not** provide medical advice, diagnosis, or treatment plans, and must **never** be used as a replacement for the clinical judgment, diagnosis, or prescribing authority of licensed healthcare professionals.

---

## Project Overview

In multi-system medical landscapes—particularly in India and Southeast Asia—patients frequently consult both modern allopathic physicians and traditional practitioners (Ayurveda, Yoga & Naturopathy, Unani, Siddha, and Homeopathy — AYUSH) simultaneously. This leads to:

1. **Fragmented Health Records**: Paper prescriptions, scanned documents, and disparate laboratory reports stored across separate clinics with no centralized interoperability.
2. **Unmonitored Herb-Drug Interactions**: High risk of adverse drug reactions caused by concurrent administration of modern pharmaceuticals and potent herbal formulations (e.g., Warfarin potentiated by *Withania somnifera* / Ashwagandha or *Curcumin*, leading to haemorrhage).
3. **Delayed Detection of Adverse Events**: Biochemical lab fluctuations (e.g., elevated serum creatinine, transaminitis, or prolonged INR) often go unassociated with recent medication adjustments.

**UnifiedRx** bridges this critical gap by ingesting clinical documents, normalizing brand and generic entities, building a dual-track longitudinal timeline, performing automated interaction and laboratory trend analysis, and synthesizing temporal safety intelligence for both patients and clinicians.

---

## Key Features

- **Prescription & Laboratory Document Processing**: Secure multi-format document ingestion supporting digital PDFs and scanned image files with role-based access control.
- **OCR-Based Text Extraction**: Automated text extraction powered by EasyOCR, equipped with defensive runtime fallbacks to digital extraction (`pypdf`) if native OS DLL policies restrict PyTorch execution.
- **PDF Text Extraction**: Native stream extraction for digital-layer PDF documents for zero-latency, high-accuracy textual ingestion.
- **Medication Information Extraction**: Heuristic and rule-based clinical NLP routines that detect drug names, dosage strengths, administration routes, frequencies, and durations.
- **Medication Name Normalization**: Automated mapping of commercial brand names to canonical generic names, classifying each drug by System of Medicine (Allopathy vs. AYUSH) and therapeutic class.
- **Medication Reconciliation**: Cross-encounter aggregation that reconciles active medications against historical regimens to identify overlaps, discontinuations, and duplicate therapies.
- **Curated Allopathic–Allopathic Interaction Checks**: Evidence-driven detection of high-risk drug-drug interactions (e.g., Metformin + Contrast Agents, ACE inhibitors + Potassium-sparing diuretics).
- **Configured Allopathic–AYUSH Interaction Checks**: Cross-system interaction engine querying clinically documented herb-drug interaction pairs with cited pharmacological mechanisms.
- **Longitudinal Medication Timeline**: Visual chronological swimlanes separating Allopathic treatments from AYUSH therapies, giving clinicians immediate multi-system visibility.
- **Laboratory Reference-Range Analysis**: Automated flagging of biochemical lab parameters against age- and sex-stratified normal ranges (Normal, Low, High, Critical).
- **Patient-Level Laboratory Trend Analysis**: Statistical trend evaluation employing Z-score anomaly detection ($Z$-threshold $\ge 2.0$) and direction indicators across historical readings.
- **Temporal Association Analysis**: Automated correlation engine evaluating medication initiation events within a configurable temporal window (14–90 days, default: 14 days) preceding an abnormal lab event.
- **AI-Assisted Clinical Summarization**: Integration with local Ollama (`llama3.2:3b`) to synthesize holistic, natural-language clinical narrative summaries for attending doctors.
- **Deterministic Summary Fallback**: Robust rule-based clinical summarizer that generates structured bulleted summaries when the local LLM daemon is offline.
- **Role-Based Web Interface**: Responsive, accessible web portal built with React 19, Material UI, and Recharts featuring dedicated workflows for Patients, Healthcare Professionals, and Administrators.

---

## System Architecture

```mermaid
flowchart TD
    subgraph UI["Frontend (React 19 + Vite + Material UI)"]
        Landing["Landing & Auth Portals"]
        PatDash["Patient Dashboard\n(Timeline, Alerts, Labs)"]
        DocDash["Doctor Clinical View\n(Access Grants, Clinical Summary)"]
        AdminDash["Admin Control Panel\n(Doctor Verification, KB Mgmt)"]
    end

    subgraph API["FastAPI Backend Service (Python 3.11)"]
        AuthRouter["Auth & JWT Guard\n(/api/v1/auth)"]
        DocRouter["Document Ingestion & Download\n(/api/v1/documents)"]
        AccessRouter["Consent & Access Grants\n(/api/v1/access)"]
        IntelRouter["Intelligence & Dashboards\n(/api/v1/intelligence)"]
        AdminRouter["Administration & Curation\n(/api/v1/admin)"]
    end

    subgraph Engines["Core Clinical Intelligence Engines"]
        OCR["OCR & Ingestion\n(EasyOCR / pypdf)"]
        NLP["Clinical NLP & Regex Parser"]
        Norm["Normalization Engine\n(Brand -> Generic -> System)"]
        Safety["Safety & Interaction Engine\n(Allopathy <-> AYUSH)"]
        LabTrend["Lab Trend & Z-Score Anomaly Engine"]
        TempAssoc["Temporal Association Engine\n(14-day Window)"]
        Summary["Clinical Summarizer\n(Ollama llama3.2:3b / Rule Fallback)"]
    end

    subgraph Data["Persistence & Local Services"]
        PG[(PostgreSQL 16\nSQLAlchemy 2.0 Async)]
        Disk[("Secure Local Storage\n(Prescriptions & Lab Files)")]
        OllamaEngine["Ollama LLM Daemon\n(llama3.2:3b)"]
    end

    UI <-->|REST API + Bearer JWT| API
    API --> Engines
    Engines <--> PG
    DocRouter <--> Disk
    Summary <-->|HTTP /api/generate| OllamaEngine
```

---

## Technology Stack

| Layer | Component / Tool | Verified Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Runtime** | Python | `3.11` | Primary backend execution environment |
| **Web Framework** | FastAPI | `0.115.0` | Asynchronous REST API routing, OpenAPI documentation |
| **ASGI Server** | Uvicorn | `0.30.6` | High-performance asynchronous HTTP server |
| **Database** | PostgreSQL | `16` | Relational clinical data store |
| **ORM** | SQLAlchemy | `2.0.35` (Async) | Asynchronous object-relational mapping (`asyncpg`) |
| **Database Driver** | asyncpg | `0.29.0` | High-throughput asynchronous PostgreSQL client |
| **Migrations** | Alembic | `1.13.3` | Database schema migrations and revision control |
| **Data Validation** | Pydantic v2 | `2.9.2` | Strong request/response schema validation & settings |
| **Authentication** | python-jose & bcrypt | `3.3.0` / `4.2.0` | JWT bearer token generation, bcrypt password hashing |
| **OCR Ingestion** | EasyOCR & pypdf | `1.7.2` / `4.0.0` | Multi-engine text extraction from scanned images and PDFs |
| **AI Summarization** | Ollama | `llama3.2:3b` | Offline local clinical narrative generation |
| **Frontend Runtime** | Node.js & npm | `>= 18` | Frontend JavaScript execution & dependency management |
| **UI Framework** | React | `19.2.8` | Component-driven user interface |
| **Build Tool** | Vite | `8.3.0` | Rapid frontend build and development server |
| **Component Library** | Material UI (MUI) | `9.4.0` | Accessible clinical UI design system |
| **Data Visualization**| Recharts | `3.10.1` | Interactive longitudinal lab trend charts |
| **HTTP Client** | Axios | `1.20.0` | Interceptor-managed API communication |
| **Containerization** | Docker & Compose | `v2+` | Multi-container service orchestration |

---

## Project Structure

```
UnifiedRx-Clinical-Decision-Support/
├── .env.example                     # Environment variable template with safe placeholders
├── .gitignore                       # Multi-tier exclusion for secrets, venvs, and build outputs
├── docker-compose.yml               # Container orchestration for PostgreSQL 16 & FastAPI
├── project_brief.md                 # Original capstone specification and architecture blueprint
├── README.md                        # Primary project documentation
├── backend/
│   ├── alembic/                     # Database migration scripts
│   │   ├── env.py                   # Async migration runner linked to SQLAlchemy Base
│   │   └── versions/                # Schema revisions (0001 to 0004)
│   ├── alembic.ini                  # Alembic migration configuration
│   ├── app/
│   │   ├── api/v1/                  # REST API Endpoints
│   │   │   ├── access_grants.py     # Patient-Doctor consent and access grant endpoints
│   │   │   ├── admin.py             # Administrator queue and knowledge-base management
│   │   │   ├── auth.py              # Patient, Doctor, and Admin registration & login
│   │   │   ├── documents.py         # Document upload, status polling, and secure download
│   │   │   ├── intelligence.py      # Timeline, safety alerts, lab trends, and AI summary
│   │   │   ├── patients.py          # Patient profile management
│   │   │   └── router.py            # Aggregator for v1 API routes
│   │   ├── core/                    # Core configuration and security
│   │   │   ├── config.py            # Pydantic BaseSettings environment manager
│   │   │   ├── database.py          # Async engine and session factory
│   │   │   └── security.py          # Password hashing, JWT creation & role verification
│   │   ├── models/                  # 15 SQLAlchemy Relational Models
│   │   │   ├── ai_clinical_summary.py
│   │   │   ├── base.py
│   │   │   ├── diagnosis.py
│   │   │   ├── drug_interaction.py
│   │   │   ├── healthcare_professional.py
│   │   │   ├── laboratory_reference.py
│   │   │   ├── laboratory_result.py
│   │   │   ├── medical_document.py
│   │   │   ├── medication_interaction_alert.py
│   │   │   ├── medication_timeline.py
│   │   │   ├── medicine.py
│   │   │   ├── medicine_normalization.py
│   │   │   ├── patient.py
│   │   │   ├── patient_access_grant.py
│   │   │   ├── temporal_association.py
│   │   │   └── user.py
│   │   ├── schemas/                 # Pydantic DTOs for request/response serialization
│   │   ├── scripts/                 # CLI database seeding and administrative utilities
│   │   │   ├── eval_query.py        # Diagnostic query script for evaluation patient
│   │   │   ├── fix_ayush_som.py     # Utility to backfill missing system-of-medicine tags
│   │   │   ├── init_dev_db.py       # Development database table initialization
│   │   │   ├── seed_admin.py        # Idempotent administrator account seeding
│   │   │   ├── seed_evaluation_dataset.py # Synthetic multi-condition evaluation dataset
│   │   │   ├── seed_interactions.py # 12 curated Allopathy-AYUSH & Allopathy-Allopathy rules
│   │   │   ├── seed_lab_references.py # Standard biochemical reference bounds
│   │   │   └── seed_normalization.py # Brand-to-generic normalization dictionary
│   │   ├── services/                # Business logic engines
│   │   │   ├── access_grant_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── document_service.py
│   │   │   ├── lab_trend_service.py
│   │   │   ├── nlp_service.py
│   │   │   ├── normalization_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── patient_service.py
│   │   │   ├── professional_service.py
│   │   │   ├── safety_service.py
│   │   │   ├── storage_service.py
│   │   │   ├── summary_service.py
│   │   │   ├── temporal_association_service.py
│   │   │   └── timeline_service.py
│   │   └── main.py                  # FastAPI application entrypoint with CORS
│   ├── Dockerfile                   # Python 3.11 backend container image definition
│   ├── requirements.txt             # Python backend dependencies
│   ├── sample_prescription.pdf      # Sample test prescription document
│   ├── sample_unmatched.pdf         # Sample document for unmatched medicine workflows
│   ├── tests/                       # Automated integration and unit test suite
│   │   ├── conftest.py              # Pytest setup and path injection
│   │   ├── test_phase1.py           # Auth, registration, and role guards
│   │   ├── test_phase2.py           # Document processing, normalization, and upload limits
│   │   ├── test_phase3.py           # Safety check, lab trends, and temporal association
│   │   ├── test_phase4.py           # Dashboard aggregation and AI summary fallback
│   │   └── test_phase5_download.py  # Document download authorization and ownership tests
│   └── uploads/                     # Local document storage directory (tracked with .gitkeep)
└── frontend/
    ├── public/                      # Static assets and icons
    ├── src/
    │   ├── api/                     # Axios API service client modules
    │   │   ├── access.js
    │   │   ├── admin.js
    │   │   ├── auth.js
    │   │   ├── client.js
    │   │   ├── documents.js
    │   │   └── patient.js
    │   ├── components/common/       # Reusable UI components (Navbar, Footer, HealthBadge)
    │   ├── context/                 # React Context (AuthContext for session state)
    │   ├── pages/
    │   │   ├── admin/               # Admin dashboard, verification queue, KB editor
    │   │   ├── doctor/              # Doctor dashboard, patient search, clinical view
    │   │   ├── patient/             # Patient dashboard, timeline, alerts, lab trends, upload
    │   │   └── public/              # Landing page, login, and registration screens
    │   ├── theme/                   # Material UI clinical color theme definition
    │   ├── App.jsx                  # React Router root navigation setup
    │   └── main.jsx                 # React root renderer
    ├── package.json                 # Node.js dependencies and scripts
    └── vite.config.js               # Vite build configuration
```

---

## Prerequisites

Before installing and running UnifiedRx, ensure the following tools are available on your system:

- **Python**: Version `3.11.x`
- **Node.js**: Version `18.x` or higher (with `npm`)
- **PostgreSQL**: Version `16.x` (or Docker & Docker Compose)
- **Git**: Version `2.x`
- **Ollama** *(Optional for AI summaries)*: Local installation with `llama3.2:3b` pulled (`ollama pull llama3.2:3b`)

---

## Installation and Setup

### 1. Clone Repository & Enter Directory
```bash
git clone https://github.com/HARSHA-GIT1/UnifiedRx-Clinical-Decision-Support.git
cd UnifiedRx-Clinical-Decision-Support
```

### 2. Configure Environment Variables
Copy the template file to `.env`:
```bash
# Windows PowerShell:
Copy-Item .env.example .env

# Linux / macOS:
cp .env.example .env
```
Open `.env` and verify your local settings (e.g., PostgreSQL credentials, secret keys).

---

### Option A: Running via Docker Compose (Recommended)

1. **Launch PostgreSQL and Backend Containers**:
   ```bash
   docker compose up -d
   ```
2. **Execute Database Migrations**:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
3. **Seed Database Knowledge Bases and Admin**:
   ```bash
   docker compose exec backend python -m app.scripts.seed_admin
   docker compose exec backend python -m app.scripts.seed_normalization
   docker compose exec backend python -m app.scripts.seed_interactions
   docker compose exec backend python -m app.scripts.seed_lab_references
   ```
4. **Start Frontend (in separate terminal)**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

### Option B: Running Locally (Bare Metal)

#### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed initial admin and clinical datasets
python -m app.scripts.seed_admin
python -m app.scripts.seed_normalization
python -m app.scripts.seed_interactions
python -m app.scripts.seed_lab_references

# (Optional) Seed synthetic evaluation dataset
python -m app.scripts.seed_evaluation_dataset

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install Node packages
npm install

# Start Vite development server
npm run dev
```

#### 3. AI Summarization Setup (Optional)
If running local LLM clinical summarization:
```bash
# Start Ollama daemon (if not already running as service)
ollama serve

# Download model (in separate terminal)
ollama pull llama3.2:3b
```
*Note: If Ollama is not running, UnifiedRx automatically falls back to deterministic rule-based clinical summarization without interrupting workflow.*

---

## Environment Configuration

| Variable | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `POSTGRES_USER` | Yes | `unifiedrx_user` | PostgreSQL database user |
| `POSTGRES_PASSWORD` | Yes | `your_secure_password` | PostgreSQL database password |
| `POSTGRES_DB` | Yes | `unifiedrx_db` | PostgreSQL database name |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@localhost:5432/unifiedrx_db` | Asynchronous SQLAlchemy connection string |
| `SECRET_KEY` | Yes | *64-character random string* | Secret key for signing HS256 JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | JWT token validity lifespan |
| `ALGORITHM` | No | `HS256` | JWT cryptographic signing algorithm |
| `ADMIN_EMAIL` | No | `admin@unifiedrx.local` | Email for initial administrator provisioned by seed script |
| `ADMIN_PASSWORD` | No | `SecureAdminPass123!` | Password for seeded administrator |
| `ADMIN_FULL_NAME` | No | `System Administrator` | Display name of system administrator |
| `TEMPORAL_ASSOCIATION_WINDOW_DAYS`| No | `14` | Day window for associating drug initiation with abnormal labs |
| `ENABLE_REAL_OCR_MODELS` | No | `true` | Set `false` to disable native EasyOCR initialization in restricted OS environments |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Endpoint for Ollama local inference daemon |
| `OLLAMA_MODEL` | No | `llama3.2:3b` | Local LLM model identifier for clinical summaries |

---

## Running the Application & Local URLs

Once backend, frontend, and database services are started:

- **Frontend User Interface**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend Health**: [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Database Architecture & Migrations

UnifiedRx utilizes PostgreSQL 16 managed through SQLAlchemy 2.0 (declarative async models) and Alembic migration scripts:

- **Migration `0001_initial_schema`**: Sets up core relational foundation across users, patient profiles, healthcare professionals, access grants, medicines, diagnoses, laboratory results, and knowledge bases.
- **Migration `0002_add_document_status`**: Incorporates asynchronous document processing statuses (`pending`, `processing`, `completed`, `failed`).
- **Migration `0003_phase3_clinical_intelligence`**: Implements tables for longitudinal medication timelines, medication interaction alerts, laboratory reference standards, and temporal association observations.
- **Migration `0004_phase4_add_summary_metadata`**: Adds structured fields for AI summary metadata (token usage, model identifier, fallback triggers).

---

## Testing

The automated test suite verifies all functional modules, role-based security boundaries, clinical normalization, and document processing rules.

### Running Backend Tests
Execute pytest from the `backend/` directory:
```bash
cd backend
python -m pytest -v
```

### Verified Test Suite Results
```
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 31 items

tests/test_phase1.py::test_health_check PASSED                           [  3%]
tests/test_phase1.py::test_patient_registration_with_auto_login PASSED   [  6%]
tests/test_phase1.py::test_doctor_registration_with_auto_login PASSED    [  9%]
tests/test_phase1.py::test_full_access_grant_and_consent_lifecycle PASSED [ 12%]
tests/test_phase1.py::test_seed_admin_idempotency PASSED                 [ 16%]
tests/test_phase1.py::test_role_guards PASSED                            [ 19%]
tests/test_phase2.py::test_file_size_limit PASSED                        [ 22%]
tests/test_phase2.py::test_invalid_file_extension PASSED                 [ 25%]
tests/test_phase2.py::test_end_to_end_document_processing_and_normalization PASSED [ 29%]
tests/test_phase2.py::test_access_authorization_for_patient_documents PASSED [ 32%]
tests/test_phase3.py::test_normalization_brand_to_generic_and_som PASSED [ 35%]
tests/test_phase3.py::test_unmatched_medicine_admin_review PASSED         [ 38%]
tests/test_phase3.py::test_timeline_construction PASSED                  [ 41%]
tests/test_phase3.py::test_allopathy_ayush_interaction_detection PASSED   [ 45%]
tests/test_phase3.py::test_allopathy_allopathy_interaction_detection PASSED [ 48%]
tests/test_phase3.py::test_interaction_severity_and_evidence_generation PASSED [ 51%]
tests/test_phase3.py::test_lab_trend_flagging_out_of_range PASSED        [ 54%]
tests/test_phase3.py::test_lab_trend_zscore_direction PASSED             [ 58%]
tests/test_phase3.py::test_temporal_association_time_gap_calculation PASSED [ 61%]
tests/test_phase3.py::test_temporal_association_rule_exclusion PASSED    [ 64%]
tests/test_phase4.py::test_clinical_summary_generation_success PASSED    [ 67%]
tests/test_phase4.py::test_clinical_summary_service_unavailable_fallback PASSED [ 70%]
tests/test_phase4.py::test_clinical_summary_persistence PASSED          [ 74%]
tests/test_phase4.py::test_patient_dashboard_aggregation_contract PASSED  [ 77%]
tests/test_phase4.py::test_dashboard_consent_enforcement PASSED          [ 80%]
tests/test_phase4.py::test_cross_system_regimen_indicator PASSED        [ 83%]
tests/test_phase4.py::test_summary_refresh_on_new_document PASSED       [ 87%]
tests/test_phase4.py::test_summary_prompt_content PASSED                 [ 90%]
tests/test_phase4.py::test_summary_role_guards PASSED                    [ 93%]
tests/test_phase4.py::test_temporal_association_service_directly PASSED  [ 96%]
tests/test_phase5_download.py::test_patient_cannot_download_another_patients_document PASSED [100%]

======================= 31 passed, 5 warnings in 27.93s =======================
```

---

## Limitations

As an academic prototype, UnifiedRx is subject to several known technical and clinical constraints:

1. **OCR Accuracy & Handwriting Variations**: Scanned, cursive, or low-resolution handwritten prescriptions can introduce character errors during OCR extraction.
2. **Curated Knowledge Base Scope**: The cross-system interaction database currently models selected, clinically documented pairs (e.g., Warfarin + Ashwagandha/Curcumin, Metformin + Karela). It is not an exhaustive national pharmacopeia.
3. **Rule-Based Parsing Constraints**: Clinical NLP extraction relies on structured patterns and heuristics. Highly idiosyncratic document formatting may omit certain non-standard dosage annotations.
4. **Association vs. Causation**: The temporal association engine identifies statistical and chronological correlations between drug initiation and lab abnormalities; it does **not** establish medical causation.
5. **No Live Hospital Trial**: The software has been tested on synthetic datasets and has not undergone formal clinical trial evaluation or medical device regulatory certification.
6. **Synthetic Data for Evaluation**: Evaluation and benchmark metrics were derived using synthetic and mock patient trajectories to preserve patient confidentiality.

---

## Future Enhancements

- **Large-Scale Herb-Drug Knowledge Expansion**: Systematic integration with the AYUSH Research Portal and traditional medicine pharmacopeias.
- **HL7 FHIR Interoperability**: Support for standard FHIR R4 resources (`MedicationRequest`, `Observation`, `Consent`) to interface with modern Hospital Information Systems (HIS).
- **Vision-Language Model (VLM) Ingestion**: Integrating multimodal clinical models (e.g., Med-PaLM M / Gemini) for improved parsing of unconstrained handwritten clinical notes.
- **Federated Healthcare Identification**: Expanding the proprietary Health Code system to integrate with national digital health architectures (such as India's ABDM / ABHA).
- **Clinical Pilot & Usability Evaluation**: Conducting structured clinician feedback studies to evaluate dashboard cognitive load and alert fatigue mitigation.

---

## License

This project is created as an MCA academic project. Distributed for academic and educational evaluation purposes.
