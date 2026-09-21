# UnifiedRx — Master Project Prompt for Antigravity

Use this document as the complete project brief. Read it fully before writing any code. Do not attempt to build the entire system in one pass — follow the phased build plan at the end of this document.

---

## 1. Project Overview

**Title:** UnifiedRx — An Evidence-Driven Clinical Decision Support Platform for Cross-System Medication Safety and Longitudinal Health Intelligence

**What it does:** UnifiedRx is a web platform that ingests a patient's medical documents (prescriptions, lab reports, discharge summaries, diagnostic reports) in PDF/image form, extracts structured clinical information from them using OCR and medical NLP, and then runs that structured data through a set of deterministic, evidence-based analytical engines to produce:

1. A unified, chronological patient health timeline (medications, labs, diagnoses, events).
2. Cross-system medication safety alerts — specifically checking for interaction risks **between allopathic and AYUSH (Ayurvedic/Unani/Siddha/Homeopathic) medicines**, which is the platform's core differentiator, since existing tools only check within the allopathic system.
3. Longitudinal laboratory trend detection (flagging values trending dangerously even while still "in range").
4. Temporal association analysis — correlating when a lab trend started against which medication was introduced beforehand, to suggest (not assert) a candidate cause.
5. An AI-generated, evidence-backed longitudinal clinical summary for the patient/clinician dashboard.

**Who uses it:** Patients (upload documents, view their own timeline/summary), Healthcare Professionals (review alerts, timelines, and summaries with evidence), and a System Administrator (manages the medicine normalization database and interaction knowledge base).

**Important scoping/tone constraint for all generated content:** This system supports clinical review — it never asserts a diagnosis or an autonomous treatment decision. All AI-generated outputs (safety alerts, temporal associations, summaries) must be presented as evidence-backed *suggestions for human review*, not conclusions. Every alert must carry its supporting evidence (source interaction record, or the specific data points that triggered it). Keep this framing in every UI string, API response field, and generated summary — never phrase output as a diagnosis or a directive.

---

## 2. System Architecture (6 Layers)

Build strictly along these layers — do not blur responsibilities between them.

1. **Presentation Layer** — React.js + Vite frontend. Talks to the backend only via REST APIs. Performs zero clinical processing itself.
2. **Application Layer** — FastAPI services: Authentication, Document Management, Workflow Orchestration. Coordinates the pipeline and exposes REST endpoints to the frontend.
3. **AI Processing Layer** — OCR Engine, Medical NLP Engine, AI Summarization Module. Converts raw documents into structured data and produces natural-language summaries from structured data.
4. **Clinical Intelligence Layer** — Deterministic, evidence-based engines (not LLM-based, must be reproducible): Medicine Normalization Engine, Longitudinal Timeline Engine, Cross-System Medication Safety Engine, Laboratory Trend Analysis Engine, Temporal Association Engine.
5. **Data Layer** — PostgreSQL (all structured records) + object storage for raw uploaded files (local disk for development; pluggable for cloud storage later).
6. **Knowledge Layer** — Curated, versioned reference data: Brand→Generic medicine mappings, the Allopathic–AYUSH Interaction Evidence Base, and Clinical Terminology & Lab Reference Ranges. This layer is read by the Clinical Intelligence Layer and is maintained by the Administrator.

**Data flow (high level):**
```
Patient → Login → Upload Document
   → OCR Processing → Medical NLP Extraction → Medicine Normalization
   → Timeline Generation
        ├─→ Cross-System Medication Safety Engine (reads Knowledge Layer)
        └─→ Laboratory Trend Analysis Engine
               → Temporal Association Engine (correlates the two branches above)
   → AI Summary Generation (consumes all structured outputs + evidence)
   → Clinical Dashboard (Presentation Layer)
```
All engines in the Clinical Intelligence Layer must be deterministic and reproducible — same input always produces the same output. Only the AI Summarization Module is allowed to use an LLM, and even there, it must be grounded strictly in the structured data and evidence already computed upstream (no free-form clinical claims).

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React.js + Vite |
| UI Framework | Material UI |
| Charts | Recharts (lab trends, timelines) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| OCR | PaddleOCR |
| Medical NLP | spaCy + MedSpaCy |
| AI Summary Generation | Ollama (local LLM — Gemma / Llama / Mistral) |
| Authentication | JWT + bcrypt |
| File Storage | Local disk for dev; abstracted behind a storage interface for future cloud object storage |
| Deployment | Docker / Docker Compose |

Use Python for the entire backend (no Java anywhere in this stack). Keep OCR, NLP, and the deterministic engines as clearly separated internal services/modules within the FastAPI app (or as separable microservices later) — not one monolithic file.

---

## 4. User Roles

- **Patient:** registers/logs in, uploads documents, views own timeline, lab trends, alerts, and AI summary. Cannot directly edit extracted clinical data — can only re-upload corrected documents.
- **Healthcare Professional (Doctor / Hospital Care Team):** registers separately from patients, receives their own professional ID, and can look up a patient's record (subject to that patient's authorization) to review alerts, timelines, trends, and summaries with evidence. Does not receive autonomous diagnosis/treatment output from the system.
- **System Administrator:** manages user accounts, the Medicine Normalization Database, the Drug/Herb Interaction Knowledge Base, Laboratory Reference Values, and system configuration. Admin accounts are not self-registerable (see Section 4A).

## 4A. Registration, Identity, and Access Control

This is a dual-registration system with a separate, non-public admin entry point. Design it as follows:

**1. Registration choice screen** — the very first screen a new visitor sees (before any form) presents exactly two clear options: **"Register as a Patient"** and **"Register as a Doctor / Healthcare Team."** Each leads to its own tailored registration form — don't merge them into one form with a role dropdown; the two audiences need different fields and different tone.

**2. Patient registration → auto-generated Health ID**
- Fields: full name, date of birth, gender, phone, email, password, blood group (optional).
- On successful registration, the system automatically generates and assigns a unique, human-readable **Patient Health ID** (e.g., format `URX-P-XXXXXXXX`, generated server-side, never user-chosen). Show this ID prominently on the post-registration welcome screen and on the patient's profile page — patients will need to share this ID with a doctor to grant access.
- This mirrors the real ABHA-ID pattern already referenced in the project's background research, which reinforces the platform's credibility rather than reinventing a new pattern.

**3. Doctor / Healthcare Team registration → auto-generated Professional ID**
- Fields: full name, professional registration/license number, specialization, hospital/clinic affiliation, email, password, phone.
- On successful registration, the system automatically generates a unique **Professional ID** (e.g., format `URX-D-XXXXXXXX`).
- New professional accounts are created in a `Pending Verification` state (do not grant patient-search access immediately) — the admin verifies the license/registration number before the account moves to `Verified`. Reflect this status clearly in the doctor's own dashboard ("Your account is under verification").

**4. Doctor's patient search & access flow (consent-based, not open lookup)**
- A verified doctor can search for a patient **only by that patient's exact Health ID** — there is no name/phone-based search, to prevent casual browsing of patient records.
- Searching by Health ID sends an **access request** to that patient; the patient must approve it (in-app notification/approval screen) before the doctor can view any record. This is the authorization step already required in Section 5's functional requirements ("Healthcare Professional: ... appropriate authorization").
- Once approved, the doctor's dashboard lists that patient under "My Patients," with an option for the patient to revoke access at any time from their own side.

**5. Admin login — separate, dedicated section**
- Admin is **not** part of the public registration flow at all. Provide a distinct, non-advertised route (e.g., `/admin/login`, not linked from the public landing page navigation) with its own login form.
- Admin accounts are provisioned directly in the database/seed script for the first release (no self-registration UI for admins in this phase).

**Additional database tables needed to support this (add to Section 6):**

- **Healthcare_Professionals** — Professional_ID (UUID, PK), User_ID (FK→Users), Full_Name, Professional_Code (the human-readable `URX-D-XXXXXXXX` ID, unique), License_Number, Specialization, Hospital_Affiliation, Verification_Status (Pending/Verified/Rejected), Created_Date.
- **Patient_Access_Grants** — Grant_ID (UUID, PK), Patient_ID (FK→Patients), Professional_ID (FK→Healthcare_Professionals), Status (Requested/Approved/Revoked), Requested_Date, Approved_Date.

Update the **Patients** table (Section 6, Table 2) to add: **Health_Code** (the human-readable `URX-P-XXXXXXXX` ID, unique, indexed — this is what doctors search by, never the internal UUID).

All patient-scoped API endpoints (Section 8) must check `Patient_Access_Grants` for `Status = Approved` before returning data to a Healthcare Professional — a doctor's own login alone is never sufficient authorization to view a specific patient's record.

---

## 5. Functional Requirements (build checklist)

- Secure registration/login (JWT + bcrypt), role-based access (Patient / Healthcare Professional / Admin).
- Upload medical documents (PDF, JPG, PNG) with document-type tagging (prescription / lab report / discharge summary / diagnostic report).
- OCR extraction of text from uploaded documents.
- Medical NLP extraction of: medicines, dosages, frequency, diagnoses, lab test names/values/units, dates, providers.
- Medicine normalization: map extracted brand names to generic names via the Medicine Normalization Database, tagging each medicine with its system of medicine (Allopathic or AYUSH) and drug class.
- Longitudinal timeline generation: merge medicines, diagnoses, and lab events into one chronological per-patient timeline.
- Cross-system medication safety analysis: for every pair of concurrently active medicines (regardless of system), look up the Drug/Herb Interaction Knowledge Base and generate a severity-tagged alert (Major/Moderate/Minor) with evidence text and clinical reference if a match is found.
- Laboratory trend analysis: for each lab parameter with 3+ historical values for a patient, run a z-score-based (or equivalent statistical) trend detector to flag a dangerous trajectory even if the latest value is still within the normal reference range.
- Temporal association analysis: when a lab trend is flagged, check whether any medicine was started/changed within a configurable prior window (default 14–90 days) and surface it as a candidate association with an explicit "correlation, not causation" disclaimer and the computed time gap.
- AI-assisted clinical summary generation: produce a natural-language longitudinal summary strictly grounded in the structured timeline, alerts, and associations already computed — must cite/reference the specific underlying data points it summarizes.
- Dashboard: patient profile, uploaded documents list, medication timeline view, lab trend charts, medication safety alerts list, temporal associations list, AI summary panel.
- Admin interface: CRUD for the Medicine Normalization Database, the Interaction Knowledge Base, and Laboratory Reference Values.

## Non-Functional Requirements

- **Performance:** document processing should complete within an acceptable response time; support concurrent users without major degradation (design APIs to be async where I/O-bound, e.g., OCR/NLP calls).
- **Reliability:** the four Clinical Intelligence engines must be deterministic — identical input must always produce identical output. Do not introduce randomness or non-reproducible logic there.
- **Security:** encrypted transport, hashed passwords, role-based authorization, restricted access to patient records by role.
- **Scalability:** modular services so new knowledge bases, AI models, or analytical engines can be added later without rearchitecting.
- **Usability:** dashboards must present complex clinical data (timelines, trends, alerts) in a way a non-specialist patient and a busy clinician can both parse quickly.
- **Maintainability:** each module independently testable behind a well-defined interface/API — avoid tight coupling between engines.

---

## 6. Database Schema (PostgreSQL — 13 tables)

Implement exactly this schema (types are guidance — adjust only for valid PostgreSQL syntax, e.g., UUID via `uuid-ossp` or `gen_random_uuid()`):

1. **Users** — User_ID (UUID, PK), Full_Name, Email (unique), Password_Hash, Role (enum: patient/healthcare_professional/admin), Created_Date.
2. **Patients** — Patient_ID (UUID, PK), User_ID (FK→Users), Name, Date_of_Birth, Gender, Blood_Group, Phone.
3. **Medical_Documents** — Document_ID (UUID, PK), Patient_ID (FK), File_Name, File_Type, Document_Type, Upload_Date, Storage_Path.
4. **Medicines** — Medicine_ID (UUID, PK), Patient_ID (FK), Document_ID (FK), Medicine_Name, Generic_Name, Dosage, Frequency, Start_Date, End_Date. *(Add System_Of_Medicine — Allopathic/AYUSH — and Drug_Class as extra fields needed for the cross-system safety engine, even though the original doc listed a shorter version.)*
5. **Diagnoses** — Diagnosis_ID (UUID, PK), Patient_ID (FK), Disease_Name, Diagnosis_Date.
6. **Laboratory_Results** — Lab_ID (UUID, PK), Patient_ID (FK), Test_Name, Test_Value (DECIMAL), Unit, Test_Date.
7. **Medication_Timeline** — Timeline_ID (UUID, PK), Patient_ID (FK), Medicine_ID (FK), Event_Type, Event_Date.
8. **Medication_Interaction_Alerts** — Alert_ID (UUID, PK), Patient_ID (FK), Medicine_1, Medicine_2, Severity, Evidence (TEXT), Generated_Date.
9. **Temporal_Associations** — Association_ID (UUID, PK), Patient_ID (FK), Medicine_ID (FK), Lab_ID (FK), Observation (TEXT), Time_Gap (INTEGER, days).
10. **AI_Clinical_Summaries** — Summary_ID (UUID, PK), Patient_ID (FK), Summary_Text (TEXT), Generated_Date.
11. **Medicine_Normalization_Database** — Mapping_ID (UUID, PK), Brand_Name, Generic_Name, Drug_Class. *(Add System_Of_Medicine here too.)*
12. **Drug_Interaction_Knowledge_Base** — Interaction_ID (UUID, PK), Medicine_A, Medicine_B, Severity, Evidence (TEXT), Clinical_Reference (TEXT).
13. **Laboratory_Reference_Values** — Reference_ID (UUID, PK), Test_Name, Lower_Limit (DECIMAL), Upper_Limit (DECIMAL), Unit.

Preserve referential integrity via foreign keys everywhere noted above; add indexes on Patient_ID across all patient-scoped tables since nearly every query is patient-scoped.

---

## 7. Core Algorithms (implement as pure, testable functions before wiring into API routes)

1. **Document Processing** — file validation → OCR text extraction → metadata tagging (upload date, document type).
2. **Medical Entity Extraction** — NLP pipeline (spaCy/MedSpaCy) over OCR text → structured entities (medicines, dosages, diagnoses, lab name/value/unit, dates).
3. **Medicine Normalization** — fuzzy-match extracted medicine names against Medicine_Normalization_Database → generic name + drug class + system of medicine; flag unmatched names for admin review rather than silently dropping them.
4. **Longitudinal Timeline Generation** — merge Medicines, Diagnoses, and Laboratory_Results into one chronologically sorted per-patient event list.
5. **Cross-System Medication Safety Analysis** — get all medicines with overlapping active date ranges → generate all pairs → look up each pair (order-independent) in Drug_Interaction_Knowledge_Base → emit alerts with severity + evidence for matches, explicitly including pairs that cross Allopathic/AYUSH systems.
6. **Laboratory Trend Generation** — per test type, per patient, compute a z-score (or equivalent) over the historical series → flag trends whose z-score crosses a defined threshold, even if the latest raw value is still inside Laboratory_Reference_Values bounds.
7. **Temporal Association Analysis** — for each flagged lab trend, look up medicines with Start_Date within the configurable prior window → compute time gap in days → emit an association record with an explicit correlation-only disclaimer.
8. **AI Clinical Summary Generation** — construct a prompt strictly from already-computed structured data (timeline + alerts + associations, not raw documents) → call the local LLM via Ollama → store the generated summary text tied to the source data it was generated from.

State the computational complexity of each algorithm in code comments/docstrings as you implement it (this maps to the project's academic documentation, which already has a complexity-analysis section).

---

## 8. Backend ↔ Frontend Contract

- Frontend communicates **exclusively** via versioned REST endpoints (e.g., prefix `/api/v1/...`) — never touches the database or file storage directly.
- Every backend response involving an alert, association, or AI summary must include its supporting evidence fields (never return a bare verdict).
- Use JWT bearer tokens issued at login; every patient-scoped endpoint must verify the requesting user's role and ownership/authorization before returning data.
- Suggested top-level route groups: `/api/v1/auth`, `/api/v1/documents`, `/api/v1/patients/{id}/timeline`, `/api/v1/patients/{id}/medicines`, `/api/v1/patients/{id}/labs`, `/api/v1/patients/{id}/alerts`, `/api/v1/patients/{id}/associations`, `/api/v1/patients/{id}/summary`, `/api/v1/admin/knowledge-base`.
- Long-running work (OCR/NLP/LLM calls) should be handled asynchronously (background task or job queue) with a status endpoint the frontend can poll, rather than blocking the HTTP request — plan for this from the start even in the first backend milestone.

---

## 9. Landing Page (Public, Pre-Login)

Before any login/registration screen, the site needs a proper public landing page — this is most people's first impression of the whole platform, so treat it as a real deliverable, not a placeholder.

**Required sections, in order:**
1. **Hero** — a clear, one-sentence statement of what UnifiedRx does and who it's for (patients juggling multiple doctors and systems of medicine), plus the two primary calls-to-action: "Register as a Patient" and "Register as a Doctor / Healthcare Team." A secondary "Login" action for existing users.
2. **The problem** — 2-3 sentences, plain language, on why fragmented multi-doctor, multi-system (allopathic + AYUSH) care is risky — this is the platform's actual reason to exist, so state it honestly rather than generically.
3. **What UnifiedRx does** — a short feature set, described in terms of what the *user* gets, not the internal architecture: unified health timeline, cross-system medication safety checks, lab trend alerts before a value goes officially abnormal, and an evidence-backed summary for their doctor. Avoid restating the internal engine names (e.g., don't say "Temporal Association Engine" here — say what it means for the person: "we flag if a lab change may be linked to a recent medication").
4. **How it works** — a short, real sequence (upload → extract → analyze → review), only presented as a numbered/step sequence because it genuinely is one (this is a legitimate use of step-numbering, unlike decorative 01/02/03 markers elsewhere).
5. **Trust/credibility section** — mention that alerts are evidence-based and every flag shows its supporting reference, and that a licensed healthcare professional reviews anything before action is taken — this matters a lot for a health product's credibility.
6. **Footer** — standard: about, contact, privacy/security note (this handles patient data, so a one-line data-handling statement belongs here even at MVP stage).

Write real, specific copy for this page as part of the build — do not ship lorem-ipsum or placeholder text, since generic filler copy is one of the biggest tells that a page wasn't actually designed for its subject.

## 10. Frontend Design Directive — Make It Look Human-Built

This is a priority, not a nice-to-have. A generic-looking frontend undermines trust in a healthcare product more than almost anything else about it, so budget real design effort here, not just component wiring.

**Concretely avoid the current AI-generated-frontend "tells":**
- Don't default to a warm cream background with a high-contrast serif headline and a terracotta/clay accent color — this is one of the most common AI-default looks right now.
- Don't default to a stark near-black background with a single neon-green or vermilion accent as the "modern tech" look either.
- Don't decorate sections with numbered badges (01 / 02 / 03) unless the content is a genuine sequence (the "How it works" steps qualify; a feature grid does not).
- Don't scatter animation everywhere (fade-ins on every card, hover-tilt on every tile) — pick one or two deliberate moments (e.g., the timeline visualization animating into place) and keep the rest calm and functional, which also suits a clinical/health product's tone better than a flashy consumer-app feel.

**Before writing any frontend code, work out and state:**
- A small, named color palette (4-6 hex values) that fits a clinical-but-approachable health product — not a generic SaaS-blue-and-white template, but also not garish; something that feels credible to both a patient and a clinician.
- Two type roles at minimum: a display/heading face used with restraint, and a body face for actual content, chosen deliberately rather than defaulting to whatever the UI framework ships with.
- One real "signature" visual element specific to this product — a strong candidate here is the longitudinal timeline itself (medications, labs, and events on one visual line) since that's the actual core idea of the product; make that the thing a person remembers, not a generic dashboard card grid.
- Write all UI copy (buttons, empty states, error messages, alert explanations) in plain, specific, active-voice language from the user's point of view — e.g., a button says "Upload your prescription," not "Submit Document"; an empty timeline says "No documents uploaded yet — add your first prescription or lab report to get started," not a bare "No data."

Apply this design thinking consistently across every screen (landing page, registration, dashboards, admin panels) — a polished landing page sitting in front of a generic default dashboard will feel more, not less, artificial.

---

## 11. Phased Build Plan — Follow This Order, Do Not Skip Ahead

**Do not generate the entire codebase in one shot.** Confirm scope with me before starting each phase, and stop at the end of each phase for review before continuing.

**Phase 1 — Backend Foundation**
- Project scaffolding (FastAPI app structure, config, Docker Compose with PostgreSQL).
- Database schema migration (all 15 tables — the original 13 plus Healthcare_Professionals and Patient_Access_Grants from Section 4A — relationships, indexes).
- Authentication service: dual registration (Patient vs. Healthcare Professional, separate endpoints/payloads), auto-generation of the human-readable Health_Code / Professional_Code, JWT + bcrypt, role-based dependency guards, and a separate admin-only login path (no admin self-registration).
- Access-grant endpoints: doctor requests access by Health_Code, patient approves/revokes.

**Phase 2 — Document Ingestion Backend**
- Document upload endpoint + file storage abstraction.
- OCR service integration (PaddleOCR).
- Medical NLP extraction service (spaCy/MedSpaCy).
- Medicine normalization service against the knowledge base tables.

**Phase 3 — Clinical Intelligence Backend**
- Timeline generation engine.
- Cross-system medication safety engine.
- Laboratory trend analysis engine.
- Temporal association engine.
- Seed/admin endpoints for the three knowledge-base tables.

**Phase 4 — AI Summary + Dashboard APIs**
- Ollama integration for summary generation, strictly grounded in prior structured output.
- Read-optimized dashboard aggregation endpoints (timeline, alerts, trends, associations, summary in the shapes the frontend will need).

**Phase 5 — Frontend**
- Public landing page (Section 9) — build and finalize this first within the phase, since it sets the whole visual identity (palette, type, signature element from Section 10) that every later screen should follow.
- Registration-choice screen → separate Patient and Doctor/Healthcare Team registration flows → login screens, including the separate, unlinked admin login route.
- Patient dashboard shell, document upload UI, post-registration Health ID display.
- Doctor dashboard shell: search-by-Health-ID flow, pending access requests, "My Patients" list.
- Timeline viewer, medication history viewer.
- Lab trend visualization (Recharts).
- Medication safety alerts panel (with evidence shown inline).
- AI clinical summary panel.
- Admin knowledge-base management screens + professional-verification queue.

**Phase 6 — Integration, Testing, and Evaluation Hooks**
- End-to-end wiring of frontend to all backend endpoints.
- Seed a small synthetic dataset (a few patients, prescriptions with planted allopathic-AYUSH conflicts, lab series with a planted dangerous trend) for demoable evaluation, matching the project's own evaluation-benchmark design.
- Basic automated tests for the deterministic engines (these are the easiest to unit test since they must be reproducible).

Start with **Phase 1 only**. Propose the folder structure and initial files, wait for my confirmation, then proceed.
