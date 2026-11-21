# Virasat Setu Codebase Index and Architectural Map:

This document provides a comprehensive structural guide to the Virasat Setu codebase. It outlines the directory hierarchy, functional responsibilities of every file, data flow linkages and cross component dependencies.

Virasat Setu Codebase Visual Architecture:

1. Client Interface Layer (app/static): index html (Responsive Single Page UI) and app js (State Machine and Fetch Logic).
2. Application Gateway (api/index py and app/main py): Vercel Serverless Entrypoint and FastAPI Application.
3. API Routers Layer (app/routers): auth py, deceased py, matching py, claimants py, claims py, institutions py, notifications py, documents py, dashboard py, admin py.
4. Business Logic Services (app/services): matching service py (100 Point Matching Engine), notification service py (Notification and Email Dispatch), supabase service py (Supabase PostgREST Client).
5. Data Models and Schemas (app/models and app/schemas): models py (Eleven Relational Entities), schemas py (Pydantic Validation Schemas).
6. Dual Persistence Layer (app/database py and supabase): Local Storage (SQLite Database) and Cloud Storage (Supabase Hosted PostgreSQL with Row Level Security).

## Detailed Directory Tree Structure:

The project follows a human interpretable modular layout separating concerns cleanly across routes, services, schemas, models and static assets:

[Root Directory: DTIProject]
/api
  index py .................. Vercel Serverless Function Entrypoint
/app
  main py ................... FastAPI Application Instance and Middlewares
  config py ................. Environment Settings and Supabase Keys
  database py ............... Engine Configuration and Session Maker
  /models
    models py ............... Eleven SQLAlchemy Relational Entities
  /schemas
    schemas py .............. Pydantic Validation and Response Schemas
  /routers
    auth py ................. Authentication and Token Generation
    deceased py ............. Deceased Citizen Records Management
    matching py ............. Asset Matching Execution and Review
    claimants py ............ Heir Verification and Profile Submissions
    claims py ............... Claim Lifecycle and Progress Steppers
    institutions py ......... Institutional Portal and Claims Review
    notifications py ........ System Alerts and Read Status
    documents py ............ Civil Document Uploads and Storage
    dashboard py ............ Family Metrics and Activity Stream
    admin py ................ Administrator Dashboards and Audits
    ai py ................... Artificial Intelligence and Fraud Endpoints
  /services
    matching service py ..... Weighted One Hundred Point Algorithm and ML Transliteration
    ai copilot service py ... Virasat AI Legal Copilot and Knowledge Engine
    fraud prediction service py Claim Health Predictor and Fraud Anomaly Intelligence
    notification service py . Alert Generation and Dispatch Logs
    supabase service py ..... Supabase Cloud REST Helper
  /seed
    sample_data py ............ Database Baseline Sample Records
    populate_realistic_assets py Expanded Realistic Asset Seeder Across Ten Sectors
  /static
    index html .............. National Portal User Interface
    app js .................. Client Single Page Controller
  /utils
    auth py ................. Password Hashing and JWT Tokens
/Visuals
  logo jpg .................. Official Brand Identity Emblem Master Asset
  portal_home png ........... Citizen Portal Landing Interface Screenshot
  citizen_dashboard png ..... Authenticated Citizen Family Dashboard Screenshot
  register_deceased png ..... Deceased Person Registration Form Screenshot
  discovered_matches png .... Discovered Assets and Matching Results Screenshot
  claim_health png .......... AI Claim Health Predictor and Readiness Meter Screenshot
  claim_tracking png ........ Claim Lifecycle and Progress Steppers Screenshot
  browse_database png ....... Financial Institution Database Browser Screenshot
  admin_console png ......... Central Administrative Oversight Console Screenshot
  fraud_anomaly png ......... Administrative AI Fraud and Anomaly Center Screenshot
  institution_desk png ...... Institutional Claim Processing Desk Screenshot
  viru_copilot png .......... Viru AI Legal Copilot Knowledge Dialog Screenshot
  google_oauth png .......... Google Identity OAuth Two Point Zero Authentication Screenshot
  notifications_modal png ... System Notifications and Alerts Modal Screenshot
  notification_email_center png Real Time Email Dispatcher and Notification Modal Screenshot
  GroupNumber_14 jpeg ....... Coursework Project Reference Visual
  VirasatSetu_Figma_Master_UIUX svg ... Master Vector UI and UX Storyboard Board for Figma Import
/documentation
  AIMLIntegrations md ......... Artificial Intelligence and Machine Learning Architecture
  Architecture md ............. Deep Technical Architecture
  Backend md .................. Backend Architecture and API Services Specification
  CodeBaseIndex md ............ Detailed Codebase Index
  DTI md ...................... Digital Transformation and Innovation Specification
  DTIProjectPlan md ........... Project Planning Specifications
  Frontend md ................. Frontend Architecture and User Interface Specification
  InstallationAndSetup md ..... Local Setup and Deployment Guide
  LogoDesign md ............... Official Brand Identity Design Specification
  Tech md ..................... Full Technical Specifications
  Usage md .................... Comprehensive Operational Manual
  Visuals md .................. Visual Architecture and Screen Inventory Specification
  WebCyberSecurity md ......... Web Cybersecurity and Threat Mitigation Architecture
/supabase
  schema sql ................ PostgreSQL DDL and Security Policies
  seed sql .................. Ninety Four Central Financial Records
requirements txt ............ Python Dependencies Specification
vercel json ................. Serverless Routing Rules
run server py ............... Local Server Runner
run server bat .............. Windows One Click Execution File
test system py .............. Ten Step Verification Test Suite
test ai features py ......... AI and Google OAuth Verification Test Suite
test security py ............ Cybersecurity and Threat Mitigation Verification Suite
agentic ui tester py ........ Playwright Agentic Browser End to End UI Automation Suite
test vercel live ui py ...... Live Vercel Production Playwright End to End UI Verification Suite
ReadMe md ................... Primary Project Overview

## Detailed File Inventory and Responsibilities:

### Gateway and Application Bootstrap:

1. api index py: Serverless entrypoint exposing the FastAPI ASGI application for zero configuration hosting on Vercel infrastructure.
2. app main py: Primary application factory configuring CORS permissions, mounting static directories, registering all ten API routers and executing startup database table creation.
3. app config py: Centralized configuration class utilizing pydantic settings to load environment variables, database URLs, Supabase credentials and storage paths.
4. app database py: Manages SQLAlchemy database engine connections with automatic fallback to local SQLite for zero setup demonstrations and PostgreSQL for cloud deployment.

### Relational Models and Validation Schemas:

1. app models models py: Defines eleven database tables using SQLAlchemy Declarative Base including User, DeceasedPerson, Claimant, ClaimantRelationship, Document, Institution, FinancialAsset, AssetMatch, Claim, Notification and AuditLog.
2. app schemas schemas py: Pydantic schemas validating input payloads and formatting outgoing JSON responses across all domain entities.

### Modular API Routers:

1. app routers auth py: Handles user account registration, login verification, password checking and role claims issuance.
2. app routers deceased py: Accepts citizen submissions of deceased family members and manages administrative verification workflows.
3. app routers matching py: Triggers the asset discovery engine for verified records and delivers categorized matching results.
4. app routers claimants py: Manages claimant submissions, legal heir documentation and relationship proofs.
5. app routers claims py: Implements the full lifecycle of simulated asset claims with five stage status updates and nodal remarks.
6. app routers institutions py: Provides dedicated desks for banking, insurance and fund officers to process claims assigned to their institutions.
7. app routers notifications py: Supplies endpoints to retrieve citizen alerts, mark items as read and inspect dispatch logs.
8. app routers documents py: Handles asynchronous civil document uploads with file validation, unique naming and secure downloads.
9. app routers dashboard py: Aggregates family statistics including total deceased records, discovered assets, active claims and recent events.
10. app routers admin py: Delivers platform statistics, pending verification queues, audit logs and central financial asset management.
11. app routers ai py: Exposes the Virasat AI Legal Copilot, citizen claim health predictor, and administrative fraud anomaly intelligence endpoints.

### Core Business Logic and Services:

1. app services matching service py: Implements the one hundred point weighted matching engine calculating identity equality, token name similarity, birth date matches, nominee relationships, and machine learning Indian phonetic transliteration variants.
2. app services ai copilot service py: Implements the dual engine Virasat AI Legal Copilot coordinating Google Gemini 3.8 Flash with the offline Indian Succession Legal Knowledge Engine.
3. app services fraud prediction service py: Calculates citizen claim health readiness scores (25% to 98%) and detects duplicate claim conflicts, high value dormancy and relationship anomalies.
4. app services notification service py: Creates persistent notification records, updates unread counters and records formatted government email dispatches.
5. app services supabase service py: Provides direct PostgREST client integrations communicating with hosted Supabase tables.
6. app utils auth py: Provides cryptographic password hashing using passlib bcrypt and JWT token encoding and decoding using pyjwt.

### Presentation Interface Layer:

1. app static index html: Single Page Application markup featuring the tricolor banner, hero discovery section, family dashboard, deceased registration form, discovered assets console, claim progress tracker, browse database explorer, administrative dashboard, institution desks, AI Legal Copilot modal, floating AI launcher, claim health meter and fraud anomaly center.
2. app static app js: Client side state controller managing user sessions, asynchronous API communications, dynamic DOM rendering, role switching, Google OAuth sign in, AI Copilot dialogues, claim health calculations and toast alerts.

### Cloud Migrations and Testing:

1. supabase schema sql: Complete PostgreSQL schema script defining all eleven tables, primary UUID keys, foreign key constraints, indexes and Row Level Security policies.
2. supabase seed sql: SQL seed script pre populating ninety four realistic Indian financial records across public sector banks, private insurers and mutual funds.
3. test system py: Automated complete testing script verifying logins, deceased submissions, matching scores, claim lifecycles, administrative stats and frontend delivery.
4. test ai features py: Comprehensive verification test suite confirming Google OAuth 2.0 configuration, AI Legal Copilot knowledge queries, machine learning transliteration variants, claim health scoring and fraud anomaly role based access controls.
5. test security py: Automated penetration testing suite verifying SQL injection defense, XSS payload rejection, CSRF custom header enforcement, secure document uploads and security headers.
6. agentic ui tester py: Full twenty one step Playwright browser end to end automation suite executing all UI interactions, modals, tabs, form inputs and verifying zero console errors.
7. test vercel live ui py: Automated fifteen step Playwright end to end verification suite validating the live Vercel cloud deployment across authentication, matching, claims, Viru AI dialogue, and administrative interfaces.

### Technical Documentation Specifications:

1. documentation Frontend md: Comprehensive frontend architectural specification detailing the Single Page Application DOM tree, client state controller, dynamic view rendering, modal systems, Viru AI chat dialog and responsive styling.
2. documentation Backend md: Comprehensive backend architectural specification detailing the FastAPI ASGI application, eleven domain API routers, service layer abstractions, database persistence engines, security pipelines and verification suites.
3. documentation AIMLIntegrations md: Architectural specification covering the Google Gemini 3.8 Flash Viru legal copilot, offline Indian succession rule engine, ML transliteration and fraud anomaly detection.
4. documentation WebCyberSecurity md: Web cybersecurity defense architecture specifying SQL injection elimination, XSS sanitization, CSRF token protections, rate limiting, and HTTP security headers.
5. documentation Visuals md: Complete visual design specification detailing color palettes, typography, UI components, brand emblems, and interface gallery screenshots.
6. documentation CodeBaseIndex md: Complete architectural index mapping directory trees, module responsibilities, database schemas, and inter component dependencies.
7. documentation Architecture md: Deep system architecture documenting multi tier application flows, database relationships, and algorithmic scoring engines.
8. documentation Usage md: Comprehensive operational manual guiding citizens, administrators, and financial officers through platform workflows.
