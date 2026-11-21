# Virasat Setu Backend Architecture and API Services Specification:

This document details the architectural structure, service layers, database abstractions, routing controllers and security models governing the backend application engine of Virasat Setu.

Virasat Setu Backend Technology Stack:
1. Web Application Framework: FastAPI (Asynchronous Python 3.10+).
2. ASGI Server Implementation: Uvicorn for High Concurrency Local and Container Execution.
3. Serverless Integration Gateway: Vercel ASGI Serverless Handler (api/index py).
4. Object Relational Mapping: SQLAlchemy 2.0 Declarative Relational Models.
5. Data Parsing and Validation: Pydantic v2 with Strict Type Constraints.
6. Authentication and Cryptography: PyJWT and Passlib with Bcrypt Password Hashing.
7. Cloud Relational Database: Supabase Hosted PostgreSQL with Row Level Security.
8. Local Embedded Database: SQLite for Zero Configuration Presentations and Offline Testing.


## Backend Architectural Layering:

The backend codebase is organized into five decoupled architectural layers:

1. Serverless Gateway Layer (api/index py): Serves as the serverless bridge exposing the FastAPI ASGI application to the Vercel edge execution runtime.
2. Application Factory and Middlewares (app/main py and app/middleware): Configures CORS origins, mounts static UI directories, attaches security pipelines and registers all eleven domain routers.
3. Domain API Routers (app/routers): Eleven modular routing controllers exposing RESTful endpoints with dependency injection and role based access control.
4. Business Logic Services (app/services): Domain services implementing the one hundred point discovery engine, ML Indian name transliteration, Viru AI legal intelligence, claim health prediction, fraud anomaly detection and notification dispatch.
5. Persistence and Model Layer (app/database py, app/models, and app/schemas): Manages database engine lifecycles, connection pooling, declarative table definitions, and Pydantic validation schemas.


## Comprehensive API Router Inventory (11 Domain Controllers):

### 1. Authentication Router (app/routers/auth py):

1. POST /api/auth/register: Registers new citizen accounts, hashes passwords with bcrypt, provisions user records and returns signed JSON Web Tokens.
2. POST /api/auth/login: Validates user credentials and issues HMAC SHA256 session tokens.
3. GET /api/auth/me: Returns profile information and assigned roles for currently authenticated sessions.
4. POST /api/auth/demo login: Convenience endpoint allowing rapid role switching across demonstration personas.
5. GET /api/auth/google/config: Returns public client configuration for Google Identity Services.
6. POST /api/auth/google/login: Validates Google OAuth credentials, auto provisions citizen profiles, and issues internal session tokens.

### 2. Deceased Records Router (app/routers/deceased py):

1. POST /api/deceased: Accepts citizen submissions of deceased relatives, validates civil registration references, and queues records for administrative review.
2. GET /api/deceased: Retrieves authorized deceased records filtered by citizen ownership or global administrative scope.
3. GET /api/deceased/{id}: Fetches full civil profile for a single deceased individual.
4. PATCH /api/deceased/{id}/verify: Administrative endpoint approving civil death certificates and automatically triggering the discovery engine.

### 3. Asset Matching Router (app/routers/matching py):

1. POST /api/matching/{deceased id}: Triggers the automated one hundred point matching engine across central banking, insurance and fund repositories.
2. GET /api/matches/{deceased id}: Retrieves generated candidate matches with granular point breakdowns and classification ratings.

### 4. Claimants Router (app/routers/claimants py):

1. POST /api/claimants: Registers legal heir or nominee profiles and links applicants to deceased family records.
2. GET /api/claimants: Retrieves registered claimant profiles for authenticated users.

### 5. Claims Lifecycle Router (app/routers/claims py):

1. POST /api/claims: Initiates simulated inheritance claims against verified asset matches, minting unique tracking codes like CLM 2026 88AB.
2. GET /api/claims: Retrieves claims filtered contextually by user role and institutional assignment.
3. GET /api/claims/{id}: Returns comprehensive claim dossiers including claimant declarations, asset metadata and audit timelines.
4. PATCH /api/claims/{id}/status: Institutional desk endpoint updating claim status across five lifecycle stages and appending binding nodal remarks.

### 6. Institutions Router (app/routers/institutions py):

1. GET /api/institutions: Delivers directory of participating banks, life insurance companies and mutual fund asset management companies.
2. GET /api/institutions/{id}: Fetches detailed profile, helpline contacts and regulatory metadata for a specific institution.

### 7. Notifications Router (app/routers/notifications py):

1. GET /api/notifications: Delivers personalized alerts regarding asset discoveries, administrative verifications and claim updates.
2. PATCH /api/notifications/{id}/read: Marks a single notification as read.
3. POST /api/notifications/read all: Clears unread indicators across all alerts for the current user.
4. POST /api/notifications/send email: Dispatches customized transactional and discovery notifications directly to any citizen email address.
5. POST /api/notifications/test email: Triggers automated asset discovery notification dispatch with live verification testing (tested with xerontitan99@gmail.com).

### 8. Documents Storage Router (app/routers/documents py):

1. POST /api/documents/upload: Accepts multipart file uploads, enforces extension whitelisting, validates size ceilings, and stores files with random UUID filenames.
2. GET /api/documents/{id}/download: Serves authenticated document downloads with Insecure Direct Object Reference (IDOR) ownership verification.

### 9. Dashboard Analytics Router (app/routers/dashboard py):

1. GET /api/dashboard/stats: Aggregates family statistics including registered relatives, discovered wealth, active claims and recent activity events.

### 10. Central Administration Router (app/routers/admin py):

1. GET /api/admin/stats: Delivers platform wide operational metrics across users, records, matches and claims.
2. GET /api/admin/financial assets: Retrieves indexed banking, insurance and mutual fund records with category and text filters.
3. POST /api/admin/financial assets: Enables administrators to index new financial assets into the central database.
4. GET /api/admin/audit logs: Retrieves an immutable chronological log of sensitive operational actions.
5. POST /api/admin/users: Allows administrators to provision new administrator, institutional officer or citizen user accounts.

### 11. Artificial Intelligence and Fraud Router (app/routers/ai py):

1. POST /api/ai/copilot: Exposes the Viru AI Legal Copilot for natural language inheritance inquiries.
2. POST /api/ai/predict claim: Evaluates claim readiness and returns approval probability scores (25% to 98%) with prescriptive documentation checklists.
3. GET /api/ai/admin/fraud anomalies: Delivers anomaly intelligence detecting duplicate claims, high value dormancy scrutiny, and relationship discrepancies (strictly role gated to administrators and institutional desk officers).


## Core Application Business Services:

### 1. Asset Matching Service (matching service py):

1. One Hundred Point Matrix: Calculates composite scores across exact identity match (50 points), name token similarity (25 points), birth date equality (15 points), and nominee family connection (10 points).
2. Machine Learning Indian Name Transliteration: Implements pure Python phonetic transformation rules and character bigram Jaccard similarity metrics to resolve regional spelling variations like Laxmi versus Lakshmi and Agarwal versus Aggarwal without heavy transformer dependencies.
3. Candidate Classification: Categorizes scores between 80 and 100 points as Strong Potential Matches, scores between 60 and 79 points as Requires Manual Review, and excludes scores below 60 points.

### 2. Viru AI Legal Copilot Service (ai copilot service py):

1. Three Tier Resilient Inference Architecture: Coordinates Google Gemini Flash API as primary generative cloud intelligence, ultra fast Groq Cloud API (openai/gpt oss 120b and qwen/qwen3.8 27b) as high speed secondary fallback, and an expanded Offline Indian Succession Knowledge Engine as tertiary failover.
2. Broad Succession and Financial Scope: Answers citizen inquiries on National Pension System (NPS), PRAN exit rules under PFRDA, Employees Provident Fund (EPFO), EPS 95 family pensions, Public Provident Fund (PPF Scheme 2019), National Savings Certificates (NSC), Senior Citizen Savings Scheme (SCSS), Kisan Vikas Patra (KVP), Fixed Deposits (FDs), joint accounts with Either or Survivor mandates, bank safe deposit lockers, and property mutation.
3. Statutory Knowledge Base: Encodes rules from the Hindu Succession Act 1956, Indian Succession Act 1925, Supreme Court nominee rulings, RBI deceased account guidelines, and AMFI mutual fund transmission procedures.

### 3. Fraud and Anomaly Prediction Service (fraud prediction service py):

1. Claim Health Evaluation: Assesses claimant relationship standing, heir succession rights, matching confidence, document completeness, and dormancy tenure to compute approval probability ratings.
2. Duplicate Contention Detection: Flags conflicting claims submitted by distinct claimants targeting the exact same underlying financial holding.
3. High Value Dormancy Verification: Flags assets exceeding five lakh rupees with dormancy tenure over ten years for enhanced civil scrutiny.
4. Nominee Hierarchy Screening: Flags discrepancies where applicant declarations conflict with recorded institutional nominee files.

### 4. Notification and Dispatch Service (notification service py):

1. Persistent Alerts: Generates database notification entries linked to recipient user accounts with unread tracking flags.
2. Multi Channel Email Dispatch: Delivers HTML and plain text notification emails with official government headers, asset discovery summaries, and action deep links.
3. Live SMTP and Simulated Fallback: Supports real time authenticated SMTP delivery when configured, or records complete RFC 5322 delivery logs into notification audit trails.
4. Tested Citizen Delivery: Verified end to end with live verification dispatches to citizen address xerontitan99@gmail.com.

### 5. Supabase Cloud Integration Service (supabase service py):

1. RESTful Cloud Persistence: Provides direct helper methods to interact with hosted Supabase PostgreSQL tables using the PostgREST interface.
2. Dual Modality Support: Seamlessly connects to hosted PostgreSQL when configured or falls back to local embedded SQLite for standalone demonstrations.


## Defensive Cybersecurity and Middleware Pipelines:

All HTTP transactions pass through security middlewares configured in app/middleware/security middleware py:

1. In Memory Sliding Window Rate Limiting: Restricts authentication attempts to thirty requests per minute per IP address and caps general API traffic at three hundred requests per minute.
2. CSRF Custom Header Enforcement: Requires state modifying HTTP requests (POST, PUT, PATCH, DELETE) to present custom client headers like X Requested With or X CSRF Token.
3. HTTP Defensive Security Headers Suite: Attaches Content Security Policy, X Frame Options DENY, X Content Type Options nosniff, Referrer Policy, and Permissions Policy to every response.
4. Real Time Input Sanitization: Inspects incoming textual payloads using regular expression signatures detecting SQL injection and Cross Site Scripting vectors.
