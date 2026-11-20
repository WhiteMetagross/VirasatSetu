# Virasat Setu Web Cybersecurity and Defensive Architecture Specification:

This document establishes the comprehensive cybersecurity architecture, defensive threat mitigations, cryptographic standards and regulatory compliance posture implemented across the Virasat Setu platform.

Virasat Setu Cybersecurity Defensive Pillars:
1. SQL Injection Multi Tier Defense: Parameterized Object Relational Mapping and Dynamic Regex Signature Filtering.
2. Cross Site Scripting (XSS) Mitigation: Strict Backend Sanitization, Pattern Rejection and Client Side Entity Encoding.
3. Cross Site Request Forgery (CSRF) Elimination: Stateless Bearer Token Isolation and Custom Verification Header Enforcement.
4. HTTP Defensive Security Headers Suite: Modern Browser Policy Enforcement Guarding Against Clickjacking, Sniffing and MIME Exploits.
5. Secure Document Storage Architecture: Path Traversal Elimination, Extension Whitelisting, UUID Isolation and IDOR Defense.
6. Rate Limiting and Brute Force Defense: In Memory Sliding Window Limiter Protecting Authentication Routes and General API Endpoints.
7. Role Based Access Control and Multi Tenant Data Isolation: Tiered Authorization Partitioning Across Citizens, Institutions and Administrators.


## Threat Modeling and OWASP Alignment Matrix:

The platform is fortified against the Open Web Application Security Project Top 10 web application security risks:

1. A01 Broken Access Control: Mitigated through role based middleware guards, institutional tenant isolation, and strict document ownership checks.
2. A02 Cryptographic Failures: Mitigated through bcrypt password hashing with automatic salt generation, HMAC SHA256 signed JSON Web Tokens, and HTTPS transport enforcement.
3. A03 Injection: Mitigated through SQLAlchemy parameterized queries, compile time type binding, and real time pattern detection against SQL and OS command injection vectors.
4. A04 Insecure Design: Mitigated through architectural separation of citizen discovery services from administrative databases, along with role gated fraud analysis.
5. A05 Security Misconfiguration: Mitigated through centralized environment settings, removal of server identification headers, and strict default security headers.
6. A06 Vulnerable and Outdated Components: Mitigated through a lightweight dependency profile and regular dependency audits.
7. A07 Identification and Authentication Failures: Mitigated through sliding window rate limiting on login routes, cryptographically strong session tokens, and Google OAuth 2.0 token verification.
8. A08 Software and Data Integrity Failures: Mitigated through server side file type validation, strict size ceilings, and isolated file system permissions.
9. A09 Security Logging and Monitoring Failures: Mitigated through an immutable database audit log recording security events, authentication transitions, client IP addresses and timestamps.
10. A10 Server Side Request Forgery (SSRF) and Cross Site Request Forgery: Mitigated through custom request header verification, CORS preflight requirements, and token isolation from automatic browser form submissions.


## 1. SQL Injection Defense in Depth:

SQL injection represents a critical threat to financial record registries. Virasat Setu deploys defense in depth across three operational tiers:

### Primary Tier (Parameterized Queries via SQLAlchemy ORM):

1. Abstract Syntax Tree Compilation: All database transactions operate through SQLAlchemy Object Relational Mapping. Rather than concatenating strings into raw SQL statements, queries are compiled into parameterized Abstract Syntax Trees.
2. Bound Value Separation: User supplied values are transmitted to the database driver as separate bound variables. The database engine treats all input strictly as literal data, completely precluding SQL syntax modification.

### Secondary Tier (Input Validation and Pattern Detection):

1. Signature Screening: The input validation layer inspects textual inputs using regex patterns that match SQL injection signatures, including UNION SELECT, OR 1=1, DROP TABLE, DELETE FROM, EXEC XP, and SQL comment sequences.
2. Boundary Enforcement: Text fields enforce strict maximum length boundaries (like sixty characters for municipal identifiers and eighty characters for applicant names), restricting the payload capacity available to malicious actors.

### Tertiary Tier (Administrative Parameterized Search):

1. Central Repository Search: Administrative search queries over ninety four central banking and insurance records employ SQLAlchemy ilike filters with escaped wildcard characters.
2. Structured Filtering: Search operations are restricted to designated indexed fields (holder name, account reference, identity reference), preventing arbitrary query injection.


## 2. Cross Site Scripting (XSS) Mitigation:

Cross Site Scripting vulnerabilities allow attackers to inject client side scripts into pages viewed by other users. Virasat Setu eliminates XSS through multi layer controls:

### Backend Sanitization and Pattern Rejection:

1. HTML Entity Replacement: The backend text sanitizer strips dangerous null bytes and control characters while transforming sensitive markup symbols like ampersands and angle brackets into secure HTML entities.
2. Malicious Payload Rejection: Pydantic field validators inspect incoming payloads and reject strings containing script tags, javascript URI schemes, SVG event handlers, and iframe tags with HTTP 400 Bad Request.

### Frontend Contextual Escaping:

1. Central Escaping Utility: The client Single Page Application incorporates a dedicated escapeHTML helper function.
2. Dynamic Template Protection: Every dynamic data field interpolated into DOM innerHTML templates (including deceased names, asset numbers, institutional remarks and audit details) is routed through the escapeHTML utility before rendering.
3. DOM TextNode Binding: Where applicable, user text is inserted using textContent rather than innerHTML to ensure complete browser interpretation as plain text.


## 3. Cross Site Request Forgery (CSRF) Mitigation:

Cross Site Request Forgery forces an authenticated browser to execute unwanted actions on a trusted web application. Virasat Setu eliminates CSRF vectors through architectural design:

### Stateless Bearer Token Isolation:

1. Local Storage Isolation: Authentication JSON Web Tokens are stored in browser local storage rather than in ambient browser cookies.
2. No Automatic Header Transmission: Browsers never attach Authorization headers to cross site requests automatically. A third party website cannot make authenticated calls on behalf of a logged in citizen.

### Custom Verification Header Enforcement:

1. Header Requirement: The CSRF Protection Middleware enforces that all state modifying HTTP verbs (POST, PUT, PATCH, DELETE) must provide custom client headers like X Requested With or X CSRF Token.
2. Browser Security Boundary: Standard HTML forms, image tags and cross site scripts cannot set custom HTTP headers without triggering a Cross Origin Resource Sharing preflight OPTIONS request.
3. Safe Method Exemption: Read only HTTP methods (GET, HEAD, OPTIONS) are exempt from custom header checks to facilitate direct document downloads and static asset loading.


## 4. HTTP Defensive Security Headers Suite:

Every HTTP response dispatched by the Virasat Setu application includes defensive security headers configured via the SecurityHeadersMiddleware:

1. Content Security Policy: Enforces default self origin restrictions while allowing styles and scripts from designated trustworthy content delivery networks (like Tailwind and Google Fonts), disallowing unauthorized external script execution.
2. X Frame Options: Configured as DENY to eliminate Clickjacking attacks by forbidding foreign domains from embedding the platform inside hidden iframes.
3. X Content Type Options: Set to nosniff to instruct modern browsers not to override the declared MIME type, preventing script execution disguised as images or text.
4. X XSS Protection: Set to 1; mode=block to activate hardware script filtering in legacy browsers.
5. Referrer Policy: Configured as strict origin when cross origin to prevent leakage of sensitive URL path tokens and query parameters to external hosts.
6. Permissions Policy: Restricts access to hardware sensors and device APIs including camera, microphone and geolocation.
7. Cross Origin Opener Policy: Set to same origin to isolate the browsing context from foreign tabs and windows.


## 5. Secure Document Storage and Path Traversal Elimination:

The platform manages sensitive civil documents including death certificates, succession proofs and identity documents.

### Storage Security Controls:

1. Extension Whitelisting: Document upload endpoints strictly accept only verified file extensions: .pdf, .png, .jpg, .jpeg, and .webp. Executable extensions (.exe, .sh, .py, .php, .html) are rejected immediately.
2. File Size Enforcement: Uploads are strictly capped at ten megabytes to protect server memory and storage resources.
3. Path Traversal Elimination: Incoming filenames are stripped of dangerous path traversal patterns like double dots and directory separators, preventing attackers from writing outside the storage root.
4. Random UUID Storage: Uploaded files are persisted on disk using randomly generated UUID filenames. The physical storage path is completely decoupled from the original uploaded filename.
5. Insecure Direct Object Reference (IDOR) Defense: Document download endpoints authenticate the requesting user and verify ownership. A citizen cannot download documents uploaded by another family, and access is restricted strictly to the document owner, authorized administrators or assigned institutional officers.


## 6. Rate Limiting and Brute Force Protections:

To thwart credential stuffing, automated scraping and denial of service attempts, the platform incorporates an in memory sliding window rate limiter:

1. Authentication Endpoint Throttling: The login and registration routes enforce a strict limit of thirty requests per minute per IP address.
2. General API Throttling: Standard application routes are governed by a three hundred request per minute ceiling.
3. Automatic Window Expiry: The rate limiter maintains sliding timestamps and automatically clears expired entries, ensuring zero memory accumulation over extended runtimes.
4. Clean HTTP 429 Status: Requests exceeding configured thresholds receive an immediate HTTP 429 Too Many Requests response with descriptive error headers.


## 7. Role Based Access Control and Multi Tenant Partitioning:

The platform enforces three distinct operational authorization tiers:

1. Family Citizen Users (family_user): Can register deceased family members, view discovered matching assets for their registered records, initiate claims, and view personal notifications. Cannot browse the central database, verify death certificates, access fraud analytics, or view other citizens claims.
2. Financial Institution Representatives (institution_rep): Access is restricted to claims matching their assigned institution identifier (like State Bank of India or Life Insurance Corporation). Cannot browse unrelated banking records or modify platform settings.
3. Government Administrators (admin): Full system oversight, civil certificate verification, administrative user creation, central database browsing, and AI fraud anomaly intelligence inspection.


## 8. Security Verification Test Suite:

Virasat Setu includes an automated penetration test suite located in test_security.py:

1. Test Execution Command: python test_security.py.
2. Verification Scope:
   * Validates SQL injection defense against classic tautology and UNION payloads.
   * Tests script tag and event handler rejection on registration and deceased endpoints.
   * Confirms CSRF rejection when custom verification headers are omitted on POST requests.
   * Validates document extension blocking against unauthorized script files.
   * Tests IDOR protection ensuring cross user document downloads return HTTP 403 Forbidden.
   * Verifies that all defensive HTTP security headers are present in server responses.
