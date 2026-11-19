# Virasat Setu System Architecture Specification:

This document details the architectural design, layer boundaries, data flow sequences and algorithm specifications powering the Virasat Setu digital inheritance platform.

[==================================================================]
[                MULTI TIER FULL STACK ARCHITECTURE                ]
[==================================================================]
                                 v
   [ 1. Presentation Tier ]
   HTML5 Semantic Web Interface
   Tailwind Styling System
   Native JavaScript Single Page Application Controller
                                 v
                                 v (HTTP REST API with JSON)
                                 v
   [ 2. API Gateway and Routing Tier ]
   Vercel Serverless Function Handler (api/index py)
   FastAPI ASGI Core Engine (app/main py)
   Ten Modular Route Controllers (app/routers)
                                 v
                                 v (Business Domain Logic)
                                 v
   [ 3. Application Services Tier ]
   Automated One Hundred Point Asset Matching Engine
   Real Time Notification and Email Dispatch Pipeline
   JWT Role Based Access Control and Security Guards
                                 v
                                 v (Data Persistence and ORM)
                                 v
   [ 4. Data and Security Tier ]
   SQLAlchemy Declarative Relational Models (11 Tables)
   Dual Persistence Engine:
     Primary: Hosted Supabase PostgreSQL with Row Level Security
     Fallback: Local Embedded SQLite for Zero Setup Presentations
[==================================================================]


## Architectural Principles:

The platform adheres to four core software engineering principles:

1. Unified Full Stack Deployment: Frontend presentation and backend APIs run under a shared domain origin, eliminating Cross Origin Resource Sharing latency and complex proxy configurations.
2. Zero Cold Start Interruption: Serverless routing through Vercel delivers instantaneous execution without the long sleep wakeup penalties typical of container services.
3. Dual Persistence Modality: The backend connects seamlessly to PostgreSQL on Supabase while supporting local zero configuration SQLite databases for demonstrations.
4. Strict Role Segregation: Access to sensitive banking and claim records is strictly partitioned between family citizens, government administrators and institutional officers.


## Component Layers:

### Presentation Layer:

The frontend is implemented as an accessible Single Page Application hosted directly through FastAPI static file mounts. It requires no complex client side compile step, ensuring rapid loading across desktop browsers and mobile devices.

1. Layout and Navigation: National portal header with official tricolor accent bar, role switcher and notification bell.
2. Dashboard Engine: Dynamic metric cards tracking registered records, discovered wealth and claim progress.
3. Interactive Consoles: Dedicated tabs for deceased registration, asset discovery, claim tracking, database browsing, administration and institutional processing.


### Gateway and Routing Layer:

FastAPI provides an asynchronous foundation capable of handling concurrent requests with minimal resource consumption. The route hierarchy is organized into domain controllers:

1. Authentication Router: Issues signed JSON Web Tokens encoding user identifiers and authorization roles.
2. Deceased Records Router: Enforces verification prerequisites prior to initiating asset discovery.
3. Matching Router: Exposes the automated matching engine for verified deceased profiles.
4. Claims Router: Manages claim creation, validation and status updates across five lifecycle stages.
5. Administration Router: Provides system stats, pending verification queues and audit logs.


### Services and Algorithm Layer:

The core intellectual property of the platform resides in the matching and notification services:

[==================================================================]
[             ONE HUNDRED POINT MATCHING ALGORITHM MATRIX          ]
[==================================================================]
  Criterion                              Points      Verification
[==================================================================]
  Exact Sample Identity Reference         50         Strict String
  Holder Full Name Similarity             25         Token Distance
  Exact Date of Birth Alignment           15         ISO Date Compare
  Nominee or Branch Location Connection   10         Relation Check
[==================================================================]
  Total Maximum Possible Score           100         Candidate Score
[==================================================================]


The score evaluation determines one of three outcomes:

1. Strong Potential Match: Scores from eighty to one hundred points indicate high confidence matches ready for claimant verification.
2. Requires Manual Review: Scores from sixty to seventy nine points require additional scrutiny by administrative officers.
3. No Match Generated: Scores below sixty points fail the minimum qualification threshold and are excluded from candidate generation.


### Mathematical Formulation of Name Similarity:

Name comparison uses a combined token sort and Jaro Winkler similarity metric. Let string S1 represent the deceased full name and string S2 represent the asset holder name.

1. Text Normalization: Names are converted to lowercase, stripped of honorifics such as Shri, Late or Smt, and sorted alphabetically by token.
2. Jaro Distance Calculation: Computes the number of matching characters within half the maximum string length and measures character transpositions.
3. Winkler Prefix Scaling: Boosts similarity scores when names share identical initial characters up to four characters.
4. Score Attribution: High similarity exceeding zero point nine yields the full twenty five points, while similarity between zero point seven and zero point nine awards fifteen points.


## End to End Data Flow Lifecycle:

[==================================================================]
[                    LIFECYCLE DATA FLOW SEQUENCE                  ]
[==================================================================]
  Citizen          Admin          Matching Service      Institution
     v               v                   v                   v
     v Submit Death  v                   v                   v
     v==============>v                   v                   v
     v               v Civil Review      v                   v
     v               v Approve Record    v                   v
     v               v==================>v                   v
     v               v                   v Run 100 Pt Engine v
     v               v                   v Cross Match DB    v
     v Real Time Notification Arrives    v Store Matches     v
     v<==================================v                   v
     v View Discovered Assets            v                   v
     v Submit Claim Application          v                   v
     v======================================================>v
     v                                   v                   v Review Proofs
     v                                   v                   v Issue Approval
     v Status Stepper Updates to Approved<===================v
[==================================================================]


1. Submission Step: Citizen provides civil death certificate details and attaches supporting documents.
2. Validation Step: Government administrator inspects municipal validity and approves the death certificate.
3. Discovery Step: The system automatically invokes the one hundred point engine across all banking, insurance and fund records.
4. Notification Step: In portal alerts and simulated transactional emails notify the citizen of discovered wealth.
5. Verification Step: The claimant submits succession details establishing their authority as legal heir or nominee.
6. Determination Step: The financial institution evaluates the application and marks the claim Approved for settlement.
