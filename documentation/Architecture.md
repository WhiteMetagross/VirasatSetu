# Virasat Setu System Architecture Specification:

This document details the architectural design, layer boundaries, data flow sequences and algorithm specifications powering the Virasat Setu digital inheritance platform.

Multi Tier Full Stack Architecture:
1. Presentation Tier: HTML5 Semantic Web Interface, Tailwind Styling System, Native JavaScript Single Page Application Controller.
2. API Gateway and Routing Tier: Vercel Serverless Function Handler (api/index py), FastAPI ASGI Core Engine (app/main py), Eleven Modular Route Controllers (app/routers).
3. Application Services Tier: Automated One Hundred Point Asset Matching Engine, ML Transliteration Normalizer, Dual Engine AI Legal Copilot, Claim Health Predictor, AI Fraud Intelligence Center, Real Time Notification and Email Dispatch Pipeline, JWT Role Based Access Control and Security Guards.
4. Data and Security Tier: SQLAlchemy Declarative Relational Models (11 Tables), Dual Persistence Engine with Hosted Supabase PostgreSQL and Local Embedded SQLite.


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
6. Artificial Intelligence Router: Exposes the Virasat AI Legal Copilot, citizen claim health predictor, and administrative fraud anomaly intelligence endpoints.


### Services and Algorithm Layer:

The core intellectual property of the platform resides in the matching and notification services.

One Hundred Point Matching Algorithm Matrix:
1. Exact Sample Identity Reference: 50 Points (Strict String).
2. Holder Full Name Similarity: 25 Points (Token Distance).
3. Exact Date of Birth Alignment: 15 Points (ISO Date Compare).
4. Nominee or Branch Location Connection: 10 Points (Relation Check).
5. Total Maximum Possible Score: 100 Points (Candidate Score).


The score evaluation determines one of three outcomes:

1. Strong Potential Match: Scores from eighty to one hundred points indicate high confidence matches ready for claimant verification.
2. Requires Manual Review: Scores from sixty to seventy nine points require additional scrutiny by administrative officers.
3. No Match Generated: Scores below sixty points fail the minimum qualification threshold and are excluded from candidate generation.


### Mathematical Formulation of Name Similarity:

Name comparison uses a combined token sort and Jaro Winkler similarity metric. Let string S1 represent the deceased full name and string S2 represent the asset holder name.

1. Text Normalization: Names are converted to lowercase, stripped of honorifics like Shri, Late or Smt, and sorted alphabetically by token.
2. Jaro Distance Calculation: Computes the number of matching characters within half the maximum string length and measures character transpositions.
3. Winkler Prefix Scaling: Boosts similarity scores when names share identical initial characters up to four characters.
4. Score Attribution: High similarity exceeding zero point nine yields the full twenty five points, while similarity between zero point seven and zero point nine awards fifteen points.


### Machine Learning Indian Name Transliteration Integration:

To resolve cross regional transliteration discrepancies across Indian civil archives, the matching engine applies machine learning transformations:

1. Indian Phonetic Normalization: Maps regional character variants (like ksh to x, ee to i, oo to o, ch to c, and collapsing repeated consonants) to standard phonetic tokens.
2. Character Bigram Jaccard Similarity: Calculates set intersection over set union of sliding two character sub strings between applicant names and ledger records.
3. Scoring Attribution: Phonetic transform matches and high Jaccard coefficients award twenty one to twenty three points with clear attribution logged in the candidate record.


### Virasat AI Legal Copilot Dual Engine Architecture:

1. Generative Intelligence Tier: Routes natural language inquiries to Google Gemini 3.8 Flash via secure backend APIs for conversational explanation of inheritance statutes.
2. Two Second Timeout Interceptor: Enforces a strict two second ceiling to protect citizen responsiveness.
3. Offline Indian Succession Knowledge Engine: Fallback rule engine encoding statutes including the Hindu Succession Act 1956, Indian Succession Act 1925, banking claim procedures, and Supreme Court nominee rulings.


### Citizen Claim Health and Approval Probability Predictor:

1. Predictive Evaluation: Evaluates claimant relationship standing, heir succession rights, matching confidence, document completeness, and dormancy tenure.
2. Probability Scoring: Outputs a readiness rating between twenty five and ninety eight percent with dynamic prescriptive checklists prior to filing.


### Administrative AI Fraud and Anomaly Intelligence Center:

1. Strictly Gated Access: Isolated from citizen views and accessible exclusively to administrators and institutional desk officers with HTTP 403 Forbidden enforcement.
2. Conflict and Anomaly Detection: Detects duplicate claims filed on the identical financial folio, flags high value dormancy exceeding five lakh rupees for enhanced verification, and detects nominee hierarchy discrepancies.


## Complete Data Flow Lifecycle:

Lifecycle Data Flow Sequence:
1. Citizen Submits Death Record: Citizen enters civil death certificate details and attaches supporting documents.
2. Admin Civil Review: Government administrator inspects municipal validity and approves the death certificate.
3. Automated Discovery: The system automatically invokes the one hundred point engine across all banking, insurance and fund records.
4. Real Time Notification: In portal alerts and simulated transactional emails notify the citizen of discovered wealth.
5. Claimant Verification: The claimant submits succession details establishing their authority as legal heir or nominee.
6. Institutional Determination: The financial institution evaluates the application and marks the claim Approved for settlement.
