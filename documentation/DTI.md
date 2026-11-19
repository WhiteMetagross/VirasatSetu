# Virasat Setu Digital Transformation and Innovation Specification:

Virasat Setu is an enterprise digital public infrastructure platform designed to bridge citizen families with unclaimed financial assets belonging to deceased relatives. Across India more than one point five lakh crore rupees remain dormant in savings accounts, matured life insurance policies, provident funds and mutual fund folios. Virasat Setu establishes an automated, secure and transparent asset discovery ecosystem connecting civil registration offices, financial institutions and citizens without requiring the platform to hold or transfer funds directly.

Virasat Setu Digital Infrastructure Overview:
1. Civil Registration: Municipal Death Records and State Registration Systems.
2. Financial Regulators: Reserve Bank of India, SEBI and IRDAI.
3. Virasat Setu Core Engine: Civil Certificate Verification Desk, 100 Point Identity and Record Matching, Automated Event Notification Pipeline.
4. Citizen Beneficiaries: Nominees and Legal Heirs, Bereaved Family Members, Civil Society Organizations.
5. Institutional Desks: Public and Private Banks, Life Insurance Companies, Mutual Fund Houses.


## Project Overview and National Problem Statement:

Every year millions of families experience bereavement without complete visibility into the financial holdings of deceased members. Critical documents are frequently lost, misfiled or unknown to lawful heirs. Concurrently, banking and insurance institutions hold statutory obligations to identify rightful claimants before funds transition into government depositor education awareness funds.

Virasat Setu addresses this systemic friction through a centralized, privacy preserving digital gateway. The system receives civil death certificate references, validates authenticity through administrative review, and performs algorithmic cross matching against institutional repositories. By replacing fragmented manual inquiries with automated discovery, the platform protects citizen inheritance rights, accelerates institutional claim resolutions and eliminates administrative deadlocks.


## Business Model Canvas:

The business model canvas establishes the organizational, operational and economic viability of Virasat Setu as a sustainable national utility.

### Key Partners:

1. State Civil Registration Departments: Municipal corporations and state registrar offices providing official civil death certificate validation.
2. Banks and Financial Institutions: Public sector lenders like State Bank of India and private banks supplying indexed dormant account records.
3. Life Insurance Companies: Underwriters like Life Insurance Corporation of India indexing matured unclaimed policies.
4. Mutual Fund Houses and Asset Management Companies: Investment registrars and fund houses indexing dormant investment folios.
5. Financial Regulators: Oversight bodies like the Reserve Bank of India, Securities and Exchange Board of India, and Insurance Regulatory and Development Authority of India.
6. Identity Verification Agencies: Statutory identity platforms facilitating lawful heir authentication.


### Key Activities:

1. Death Record Collection and Verification: Ingesting citizen submissions and verifying municipal death certificate details.
2. Secure Identity Matching: Executing automated weighted algorithms to cross match identity numbers, names, birth dates and nominee connections.
3. Coordination with Financial Institutions: Relaying verified candidate matches to institutional desks for review.
4. Automated Notification Dispatch: Transmitting instant in portal alerts and transactional email communications to legal heirs upon asset discovery.
5. Claim Status Tracking: Providing an auditable five stage progress tracking engine from submission through settlement.
6. Platform Maintenance and Security: Ensuring continuous uptime, encryption standards and role based access boundaries.


### Key Resources:

1. Centralized Digital Platform: Cloud native application infrastructure hosting discovery and tracking engines.
2. Civil Registration System Integration: Technical interfaces validating civil death records.
3. Secure Identity Verification System: High confidence matching protocols comparing identity references and civil metadata.
4. Institutional Database Connectivity: Secure repositories indexing banking, insurance and fund assets.
5. Technical and Cybersecurity Infrastructure: Robust perimeter firewalls, encryption algorithms and access controls.
6. Development and Operations Team: Dedicated software engineers, security analysts and civil liaison specialists.


### Value Propositions:

1. Helps Families Discover Unclaimed Financial Assets: Surfaces overlooked bank balances, insurance proceeds and mutual fund investments.
2. Eliminates Fragmented Manual Searches: Removes the necessity for citizens to physically visit dozens of individual branches across multiple institutions.
3. Automated Notifications Following Death Registration: Informs nominees and lawful heirs immediately when valid matches emerge.
4. Faster Identification and Settlement: Accelerates the transition of dormant accounts into active claimant processing.
5. Simplifies Administrative Burden for Heirs: Provides clear digital guidelines on succession proofs and required documentation.
6. Secure and Transparent Asset Discovery: Maintains immutable audit logs recording every access and verification determination.
7. Zero Direct Fund Custody: The platform maintains zero custody over citizen funds and never executes monetary transfers directly, preserving institutional autonomy and regulatory compliance.


### Customer Relationships:

1. Automated Communications: Instant text and email alerts guiding claimants through each operational milestone.
2. Transparent Self Onboarding: Intuitive registration workflows for nominees and legal heirs.
3. Dedicated Grievance Redressal: Integrated support channels to assist citizens with documentation queries.
4. Five Stage Visual Progress Tracking: Real time visual indicators reflecting current institutional claim statuses.
5. Secure and Guided Engagement: Structured prompts ensuring citizens understand required legal heir credentials like succession certificates.


### Channels:

1. Virasat Setu Web Portal: Primary accessible web platform optimized for desktop and mobile browsers.
2. Automated SMS and Email Alerts: Transactional notifications dispatched directly to registered citizen inboxes.
3. Municipal Civil Registration Counters: Informational kiosks and guidance brochures situated at municipal death registration offices.
4. Financial Institution Web Desks: Dedicated processing consoles embedded within institutional portals like bank and insurance intranets.
5. Mobile Friendly Web Application: Fully responsive interface accessible across handheld smartphones and tablets without native application downloads.


### Customer Segments:

1. Nominees and Designated Beneficiaries: Individuals named directly on banking records, insurance policies or fund folios.
2. Legal Heirs and Family Members: Class one and class two legal heirs seeking rightful succession inheritance.
3. Public and Private Sector Banks: Financial institutions seeking to reduce dormant liabilities and fulfill regulatory unclaimed asset mandates.
4. Life Insurance Underwriters: Insurers managing death claims and policy proceeds.
5. Mutual Fund Asset Management Houses: Investment managers seeking to locate rightful holders of dormant investment accounts.
6. Government Registration and Regulatory Authorities: Civil registries and financial regulators monitoring national compliance.


### Cost Structure:

1. Platform Development and Engineering Maintenance: Continuous feature evolution, bug resolution and architecture enhancement.
2. Cloud Infrastructure and Hosting Services: Scalable serverless computing, database hosting and high availability storage.
3. Institutional Interface Integration: Engineering costs associated with connecting institutional datasets and secure data bridges.
4. Cybersecurity and Regulatory Data Protection: Annual penetration testing, vulnerability assessments and cryptographic key management.
5. Civil Identity Verification Operations: Administrative expenses associated with validating municipal death certificates.
6. Technical Support and Helpdesk Operations: Operational staff assisting citizens and resolving technical inquiries.


### Revenue Streams:

1. Government Funding and Technology Grants: National budget appropriations supporting digital public infrastructure.
2. Public Private Partnership Investments: Joint development funding from institutional stakeholders.
3. Institutional Integration and Maintenance Subscriptions: Recurring infrastructure maintenance fees paid by participating financial institutions.
4. Government Technology Service Contracts: Long term maintenance and operational contracts with state administrative bodies.
5. Optional Enterprise Service Tiers: Specialized analytics and batch processing subscriptions for high volume financial institutions.


## Full Stack Architecture and Technology Stack:

The Virasat Setu technology stack is built on modern, unified full stack architecture ensuring high performance, zero cold start delays and strict data protection.

### Application Presentation Layer:

1. Framework and Markup: Accessible semantic HTML5 Single Page Application paired with Tailwind styling utilities.
2. Responsive Viewport Adaptability: Mobile optimized fluid layouts ensuring zero horizontal element clipping on mobile screens down to three hundred and sixty pixels.
3. Asynchronous Client Controller: Native JavaScript state machine managing asynchronous JSON communication, dynamic document rendering and session tokens.


### API Gateway and Modular Routing Layer:

1. Asynchronous Application Server: Python FastAPI framework delivering asynchronous concurrency, automatic OpenAPI documentation and strict data validation.
2. Serverless Cloud Gateway: Vercel serverless routing configured through vercel json and api index py, routing web traffic seamlessly under a unified domain.
3. Ten Domain Routers: Independent modular controllers governing authentication, civil deceased records, asset matching, claimants, claims, institutions, notifications, document storage, dashboard analytics and administrator oversight.


### Database and Security Layer:

1. Primary Cloud Database: Hosted Supabase PostgreSQL database providing managed relational persistence, automated backups and granular Row Level Security.
2. Local Development Database: Embedded SQLite database engine enabling instantaneous zero setup local verification and presentations.
3. Object Relational Mapping: SQLAlchemy declarative models abstracting database operations with strict type safety.
4. Payload Validation: Pydantic schemas validating all incoming JSON requests and serializing outgoing responses.
5. Security and Session Token Protocol: JSON Web Tokens signed with HMAC SHA256 encoding user identifiers and authorization roles.
6. Cryptographic Password Protection: Irreversible bcrypt password hashing utilizing passlib cryptographic libraries.


## Twelve Functional Modules Specification:

Virasat Setu implements twelve cohesive functional modules satisfying every project requirement:

### Module 1 Home Portal:

Introduces the national platform, highlights the challenge of dormant financial assets across India, explains the discovery process and provides immediate navigation to discovery consoles.

### Module 2 Authentication and Role Authorization:

Enables citizen registration, profile creation and role gated access. The platform implements three distinct roles, namely citizen family users, government administrators and financial institution representatives.

### Module 3 Family Metrics Dashboard:

Displays dynamic counters for registered deceased individuals, discovered potential assets, claims in progress and unread alerts alongside an activity feed.

### Module 4 Deceased Person Registration:

Provides a three section civil registration form capturing personal details, municipal death certificate references and submitter heir relationships, accompanied by document attachments.

### Module 5 Central Financial Repository:

Maintains an indexed repository of ninety four realistic records across forty two bank accounts, twenty six insurance policies and twenty six mutual fund folios.

### Module 6 Automated Discovery and Weighted Matching Engine:

Executes a one hundred point weighted algorithm searching across institutional repositories upon administrative verification of a death certificate.

### Module 7 Discovered Assets Console:

Categorizes identified assets into Banking, Insurance and Mutual Funds, displaying approximate financial valuations, score breakdowns and asset specifics.

### Module 8 Claimant and Legal Heir Verification:

Facilitates claimant submissions where legal heirs declare their capacity like nominee or lawful successor and attach supporting documentation.

### Module 9 Multi Channel Notification Pipeline:

Dispatches real time in portal notifications and generates formatted official email logs with national headers to inform claimants of milestone events.

### Module 10 Claim Lifecycle Management:

Provides simulated claim submission and tracking across five operational stages, specifically Submitted, Under Review, Documents Required, Approved and Completed.

### Module 11 Government Administrator Command Center:

Equips authorized officers with global metrics, an audit log stream, pending civil record verification tools and manual asset indexing consoles.

### Module 12 Financial Institution Settlement Desk:

Provides isolated institutional processing desks where nodal officers from specific organizations like State Bank of India or Life Insurance Corporation review claims and issue formal determinations.


## One Hundred Point Weighted Matching Algorithm:

The matching engine evaluates verified deceased records against central financial repositories using a weighted scoring matrix designed to minimize false positives:

One Hundred Point Matching Algorithm Matrix:
1. Exact Sample Identity Reference: 50 Points (Strict Match).
2. Full Name Token Similarity: 25 Points (Jaro Winkler).
3. Exact Date of Birth Match: 15 Points (ISO Date).
4. Nominee or Branch City Association: 10 Points (Context Link).
5. Maximum Composite Score: 100 Points (Candidate).


The algorithm assigns records into three operational qualification tiers:

1. Strong Potential Match (Eighty to One Hundred Points): Indicates high confidence alignment across identity reference, name and birth date. Automatically approved for claimant view.
2. Requires Manual Review (Sixty to Seventy Nine Points): Indicates partial alignment like matching name and birth date with secondary identity discrepancy. Queued for administrative scrutiny.
3. No Match Generated (Below Sixty Points): Fails the minimum qualification threshold and is excluded from candidate lists to prevent citizen confusion.


## Relational Database Architecture:

The platform data store comprises eleven relational tables linked via UUID primary keys and foreign key constraints:

1. Users Table: Stores citizen and officer profiles, encrypted passwords and authorization roles.
2. Institutions Table: Maintains institutional records like State Bank of India, Punjab National Bank, Bank of Baroda, Life Insurance Corporation and HDFC Mutual Fund.
3. Deceased Persons Table: Stores civil death records submitted by citizens awaiting administrative validation.
4. Financial Assets Table: Indexes central financial assets across banking, insurance and fund sectors.
5. Asset Matches Table: Records candidate pairings generated by the matching algorithm with explicit point breakdowns.
6. Claimants Table: Stores legal heir profiles and relationship declarations.
7. Claimant Relationships Table: Maps claimants to corresponding deceased individual profiles.
8. Claims Table: Tracks individual claim applications, institutional assignments and five stage statuses.
9. Documents Table: Stores metadata, file sizes, MIME types and file paths for uploaded death certificates and civil proofs.
10. Notifications Table: Logs real time in portal alerts, unread counters and deep links.
11. Audit Logs Table: Maintains an immutable chronological trail of user logins, matching executions and claim determinations.


## Security Access Control and Policy Isolation:

1. Zero Fund Custody: The platform never accepts, holds or disburses money, leaving all monetary settlements to authorized banking and insurance systems.
2. Fine Grained Role Segregation: Citizens can access only records they submitted, institutional officers access only claims assigned to their institution, and administrators manage platform health.
3. Cryptographic Token Protection: User sessions utilize signed JSON Web Tokens containing encrypted role claims verified on every API invocation.
4. Row Level Security: Cloud PostgreSQL tables implement Supabase Row Level Security ensuring database level isolation.
5. Protected Document Repository: Civil documents like death certificates are stored in private storage accessible only via authenticated endpoints.


## Complete Operational Workflow:

The complete lifecycle operates through nine distinct operational steps:

1. User Account Registration: Citizen creates an authenticated profile on the portal.
2. Civil Deceased Submission: Citizen submits deceased person metadata and attaches municipal death certificate copies.
3. Administrative Civil Review: Government administrator verifies the certificate reference against municipal standards and approves the record.
4. Automated Discovery Execution: Approval triggers the one hundred point algorithm searching all institutional repositories.
5. Candidate Match Generation: The system stores candidate records with scores of sixty or higher and notifies the citizen.
6. Notification Receipt: Citizen receives an in portal alert and formatted transactional email notification.
7. Heir Capacity Declaration: Citizen inspects discovered assets and submits claimant details establishing nominee or legal heir rights.
8. Institutional Desk Review: Nodal officer from the holding institution reviews the claim and updates status to Approved.
9. Lifecycle Milestone Tracking: Citizen views the updated determination on their dashboard visual progress stepper.
