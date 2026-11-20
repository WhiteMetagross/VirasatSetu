# Virasat Setu Artificial Intelligence and Machine Learning Integration Specification:

This document details the architectural design, algorithmic models, data structures and operational workflows for the artificial intelligence and machine learning capabilities integrated into the Virasat Setu platform.

Virasat Setu Artificial Intelligence Stack:
1. Virasat AI Legal Copilot: Dual Engine Architecture with Google Gemini Generative Intelligence and Embedded Indian Succession Legal Knowledge Engine.
2. Machine Learning Indian Name Transliteration Engine: Pure Python Character Bigram Jaccard and Double Metaphone Phonetic Distance Normalizer.
3. Citizen Claim Health and Approval Probability Predictor: Five Factor Multi Dimension Readiness Evaluator with Prescriptive Action Recommendations.
4. Administrative AI Fraud and Anomaly Intelligence Center: Role Gated Risk Engine Detecting Duplicate Claim Conflicts, High Value Dormancy and Relationship Discrepancies.
5. Google OAuth 2.0 Single Sign On Integration: OpenID Connect Authorization Code Flow with Automatic Citizen Account Provisioning.


## Design Philosophy and Architectural Constraints:

The artificial intelligence systems powering Virasat Setu are engineered under strict architectural constraints tailored for sovereign public infrastructure:

1. Serverless First Execution: All machine learning and inference routines must execute seamlessly within Vercel serverless microVM environments without heavy native C++ binaries, PyTorch dependencies or large model weights.
2. Sub Millisecond Operational Latency: Algorithmic transliteration and claim health evaluations must conclude in under two milliseconds to preserve instantaneous page responsiveness.
3. Resilient Dual Engine Architecture: To protect against external network latency, cloud API quota limitations or intermittent third party outages, external generative models are paired with zero latency deterministic offline inference engines.
4. Strict Role Based Privacy Isolation: Sensitive predictive models like fraud intelligence and anomaly detection are strictly isolated from citizen views and accessible exclusively to authenticated administrators and institutional officers.
5. Absolute Explainability: Every score, recommendation and anomaly flag is accompanied by human interpretable rule breakdowns, ensuring full legal auditability for judicial review.


## 1. Virasat AI Legal Copilot:

The Virasat AI Legal Copilot serves as an interactive legal knowledge assistant for citizens navigating the complexities of Indian succession jurisprudence, banking claim procedures and insurance settlements.

### Dual Engine Architecture:

The Copilot employs a tiered resolution strategy:

1. Primary Generative Layer: Incoming citizen legal questions are routed to Google Gemini 3.8 Flash via secure backend HTTPS endpoints. The generative model provides natural language synthesis, contextual awareness and tailored conversational explanations.
2. Two Second Timeout Guard: The backend dispatches requests to Gemini with a strict two second network timeout to protect the citizen user experience against cloud connectivity delays.
3. Offline Indian Succession Knowledge Engine: If the external Gemini endpoint times out, encounters rate limiting or loses network connectivity, the request is intercepted by the embedded offline knowledge engine.
4. Deterministic Rule Matching: The offline engine tokenizes incoming queries, matches conceptual keywords against curated Indian legal statutes, and returns verified, legally sound guidance with zero external network dependency.

### Embedded Legal Knowledge Corpus:

The knowledge engine incorporates statutory provisions and landmark judicial precedents across Indian succession law:

1. Hindu Succession Act 1956 (Amended 2005):
   * Class 1 Legal Heirs: Governs primary intestate succession. Class 1 heirs include son, daughter, widow, mother, son of a predeceased son, daughter of a predeceased son, widow of a predeceased son, son of a predeceased daughter, daughter of a predeceased daughter, and children of predeceased grandchildren.
   * Equal Inheritance Rights: Class 1 heirs succeed simultaneously to equal shares. Under the 2005 amendment, daughters hold equal coparcenary rights by birth in ancestral property identical to sons.
   * Class 2 Legal Heirs: Category 1 includes father. Category 2 includes son daughter son, son daughter daughter, brother, sister. Heirs in earlier categories exclude those in subsequent categories.

2. Indian Succession Act 1925:
   * Testamentary Succession: Covers execution, attestation and probate of wills across India.
   * Succession Certificate (Section 370 to 389): Issued by a competent civil court having territorial jurisdiction over debts and securities (like bank deposits, government bonds and equity shares). It establishes the legal right of the applicant to receive interest or dividends and negotiate the securities.
   * Letter of Administration: Required when an individual dies intestate leaving immovable property in presidency towns (like Mumbai, Kolkata and Chennai), or where no executor is named in a will.

3. Nominee Rights versus Legal Heir Rights (Supreme Court Jurisprudence):
   * Statutory Trustee Principle: The Supreme Court of India in landmark judgments including Ram Chander Talwar v Devender Kumar Talwar (2010), Sarbati Devi v Usha Devi (1984), and Shakti Yezdani v Jamshed Hormusjee Wadia (2020) ruled that a nominee is merely a statutory custodian and trustee authorized to receive asset custody from financial institutions to ensure a valid discharge.
   * Beneficial Title: A nominee does not become the ultimate owner of the asset. The asset forms part of the estate of the deceased and devolves upon the legal heirs in accordance with applicable succession laws or a valid will.

4. Reserve Bank of India Deceased Banking Claim Directives:
   * Nominated Accounts: If a valid nomination is recorded under Section 45ZA of the Banking Regulation Act, banks are mandated to settle claims in favor of the nominee within fifteen days upon submission of death certificate and identity verification, without requiring a succession certificate or probate.
   * Non Nominated Accounts: For claims without nominee, banks permit settlement up to institutional board approved thresholds (commonly up to five lakh rupees) based on a letter of indemnity and joint affidavit by all legal heirs, bypassing costly court succession petitions.

5. Insurance Act 1938 and AMFI Mutual Fund Transmission Rules:
   * Beneficial Nominees (Section 39 Amendment): Where the nominee is the father, mother, spouse or children, the nominee is classified as a beneficial nominee and holds absolute title to policy proceeds, excluding other legal heirs.
   * Mutual Fund Folio Transmission: Transmission to registered nominee requires Form T3, attested death certificate, KYC verification and bank mandate. Transmission to legal heirs without nominee requires Form T3, indemnity bond, and succession certificate or legal heirship certificate if folio valuation exceeds threshold limits.

### Copilot API and Security Controls:

1. Endpoint Route: POST /api/ai/copilot.
2. Authentication Exemption with Rate Limiting: Accessible to both anonymous visitors and logged in citizens to maximize legal literacy, protected by a dedicated sliding window rate limiter.
3. Prompt Injection Defense: Inputs are stripped of HTML tags, script delimiters, system role directives and control characters before ingestion.


## 2. Machine Learning Indian Name Transliteration Engine:

In Indian civil registries and institutional archives, personal names are frequently transliterated from regional scripts (like Devanagari, Bengali, Tamil, Telugu, Kannada, Gujarati, Malayalam and Gurmukhi) into the Latin alphabet by different municipal clerks and banking officers over decades.

### Transliteration Variance Taxonomy:

1. Aspirate Variants: Lakshmi versus Laxmi, Mukherjee versus Mukhopadhyay, Choudhary versus Chowdhury, Dikshit versus Dixit.
2. Vowel Digraph Alternations: Sangeeta versus Sangita, Meena versus Mina, Sunita versus Suneeta, Rakesh versus Rakeshe.
3. Consonant Reduplication: Agarwal versus Aggarwal, Kapoor versus Kapur, Mittal versus Mital, Sharma versus Shharma.
4. Terminal Vowel Elision: Virender versus Virendra, Surender versus Surendra, Rameshwar versus Rameshwara.

### Algorithmic Pipeline:

The transliteration engine operates a four stage mathematical pipeline:

1. Text Sanitization and Tokenization:
   * Strips honorary titles and honorific prefixes like Shri, Shrimati, Smt, Late, Dr, Pandit, Kumar, Kumari.
   * Converts all characters to standard lowercase Latin characters and normalizes internal whitespace.

2. Pure Python Phonetic Transformation:
   * Maps regional digraphs to canonical phonetic equivalents:
     * 'ksh' and 'x' map to 'x'.
     * 'ee' and 'ea' map to 'i'.
     * 'oo', 'ou', 'ow' map to 'o'.
     * 'ch' maps to 'c'.
     * 'th' maps to 't'.
     * 'dh' maps to 'd'.
     * 'bh' maps to 'b'.
     * 'gh' maps to 'g'.
     * 'jh' maps to 'j'.
     * 'ph' maps to 'f'.
     * 'v' maps to 'w'.
   * Terminal vowel reduction: Normalizes trailing 'a' or 'e' to standard form.
   * Consonant deduplication: Collapses repeated consecutive identical characters into a single consonant token.

3. Character Bigram Jaccard Similarity:
   * Given normalized string S1 and S2, the system extracts sets of sliding two character sub strings (bigrams):
     * B(S) = set of all s[i:i+2] for i in range 0 to len(s) minus 2.
   * Computes Jaccard index:
     * Jaccard(S1, S2) = cardinality of (B(S1) intersection B(S2)) divided by cardinality of (B(S1) union B(S2)).
   * Yields a continuous similarity coefficient bounded strictly between zero and one.

4. Composite Transliteration Scoring Integration:
   * If exact token comparison succeeds: Awards 25 Points.
   * If Jaro Winkler distance exceeds 0.90: Awards 25 Points.
   * If Phonetic Transform exact match or Double Metaphone match occurs: Awards 23 Points with matching reason logged as AI ML Transliteration Match.
   * If Character Bigram Jaccard similarity exceeds 0.85: Awards 21 Points with matching reason logged.
   * If standard token similarity falls between 0.70 and 0.85: Awards 15 Points.


## 3. Citizen Claim Health and Approval Probability Predictor:

When a citizen discovers a matched financial asset and prepares to file an inheritance claim, uncertainty regarding required documentation often leads to rejected submissions or delayed payouts. The Claim Health Predictor provides prescriptive machine evaluation prior to filing.

### Five Dimension Evaluation Model:

1. Claimant Relationship Standing (25% Weight):
   * Class 1 Legal Heir (Son, Daughter, Spouse, Mother): Highest legal standing, awards maximum weight.
   * Designated Nominee: Strong institutional claim capacity, awards full points under banking regulations.
   * Extended Legal Heir: Requires supplementary genealogy affidavits, adjusts standing score accordingly.

2. Matching Confidence Score (20% Weight):
   * Match scores above 80 points: Verified high probability asset match, provides full confidence.
   * Match scores between 60 and 79 points: Flags requirement for supplementary identity proof linking the deceased to the institution.

3. Civil Record Verification Status (25% Weight):
   * Verified by Government Administrator: Official municipal confirmation established, provides maximum validity.
   * Pending Verification: Advises citizen that administrative verification of death certificate must precede claim processing.

4. Document Completeness Factor (15% Weight):
   * Evaluates presence of official death registration number, sample identity reference (PAN), and uploaded civil proofs.

5. Asset Dormancy Tenure and Valuation Tier (15% Weight):
   * Assets dormant under ten years or valuation below one lakh rupees: Low documentation barrier, high approval velocity.
   * Assets exceeding five lakh rupees or dormant over ten years: Flags statutory requirement for enhanced verification, court succession certificate or indemnity bond.

### Prescriptive Recommendation Engine:

The model generates specific actionable instructions:
1. Low Probability Score (Below 50%): Recommends obtaining an official certified copy of the death certificate, verifying PAN link with the financial institution, and confirming heirship standing.
2. Moderate Probability Score (50% to 75%): Prescribes executing an Affidavit of Heirship signed before a First Class Judicial Magistrate and preparing a No Objection Certificate from other surviving legal heirs.
3. High Probability Score (Above 75%): Confirms strong readiness and advises submitting bank account cancelled cheque and KYC verification documents to facilitate rapid institutional payout.


## 4. AI Fraud and Anomaly Intelligence Center:

To prevent fraudulent claims, identity misappropriation and unauthorized asset liquidation, Virasat Setu features an anomaly detection intelligence engine.

### Role Based Access Control Safeguards:

1. Administrative and Institutional Exclusivity: Fraud detection models, risk scores and anomaly alerts are strictly quarantined from citizen views.
2. Backend Route Authorization: Calls to /api/ai/admin/fraud anomalies enforce role verification. Any attempt by a family user to query this endpoint returns HTTP 403 Forbidden and logs a security audit event.
3. Institutional Scoping: Institutional representatives view anomalies strictly scoped to their assigned bank, insurer or mutual fund.

### Anomaly Detection Vectors:

1. Duplicate Claim Contention Anomaly:
   * Condition: Two or more distinct claimants file claims targeting the exact same financial asset.
   * Risk Category: High Conflict Contention.
   * Operational Action: Both claims are placed on immediate administrative hold. The system generates an alert requiring both parties to present original succession certificates issued by a competent civil court before funds can be released.

2. High Value Dormancy Anomaly:
   * Condition: The unclaimed financial asset has an estimated valuation exceeding five lakh rupees and has remained dormant for over ten years.
   * Risk Category: High Value Enhanced Diligence.
   * Operational Action: The system flags the claim for mandatory dual officer review, municipal registry re verification, and in person identity verification of the claimant.

3. Relationship Capacity Anomaly:
   * Condition: The claimant files as a distant legal heir when the central database contains a recorded active nominee, or files as nominee without matching institutional nominee reference records.
   * Risk Category: Nominee Hierarchy Discrepancy.
   * Operational Action: Alerts the institutional claims desk to cross examine institutional records before dispatching settlement notifications.


## 5. Google OAuth 2.0 Single Sign On Integration:

Virasat Setu implements Google OAuth 2.0 authentication compliant with RFC 6749 and OpenID Connect standards.

### Authentication Flow:

1. Configuration Discovery: The frontend calls /api/auth/google/config to retrieve client authorization parameters.
2. User Consent and Token Generation: The user clicks Continue with Google in the authentication modal, launching the Google Identity Services dialog.
3. Backend Token Validation: The client posts the authorization credential to /api/auth/google/login.
4. Account Auto Provisioning:
   * The backend validates the credential signature against Google public keys.
   * Extracts verified email, full name and user identifier.
   * If the account exists, the session is authenticated.
   * If the user is new, the system auto provisions a citizen family user profile with a cryptographically secure random password hash.
5. Internal Session Minting: The backend generates an internal HMAC SHA256 JSON Web Token with a twenty four hour expiration window, returning complete session credentials to the client application.
