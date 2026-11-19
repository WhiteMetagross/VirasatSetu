# **Virasat Setu: Complete Website Prototype Plan**

## **1. Project overview**

Virasat Setu will be a complete, functional web application that helps families discover potential unclaimed financial assets belonging to deceased family members.

The website will provide a single interface to search sample bank records, insurance policies and mutual fund investments. It will also provide claimant verification, notifications and claim tracking.

The project will be developed as a working college prototype using fictional data. It will not require access to actual government or financial institution databases.

The website must demonstrate the complete process, from user registration and death record submission to asset discovery and claim status updates.

### **Main project objectives**

1. Allow users to register and log in securely.
2. Allow families to submit details of deceased individuals.
3. Maintain a database of deceased individuals and their nominees or legal heirs.
4. Search sample bank, insurance and mutual fund databases.
5. Identify possible financial assets through an automated matching algorithm.
6. Allow administrators to verify submitted records and potential matches.
7. Generate automatic email and in website notifications.
8. Allow claimants to submit verification documents.
9. Provide claim tracking.
10. Provide separate dashboards for administrators and financial institutions.

## **2. Recommended technology stack**

The technology stack is based on Supabase and Vercel (unified full-stack architecture).

Technology Stack Summary:
1. Framework: Next.js (App Router, React 19) for full stack web application and UI.
2. Styling: Tailwind CSS and shadcn/ui for modern, responsive website design.
3. Backend APIs: Next.js Route Handlers for business logic, APIs and matching engine.
4. Database: Supabase PostgreSQL to store all project data.
5. Authentication: Supabase Auth (@supabase/ssr) for registration, login and role middleware.
6. File storage: Supabase Storage to store uploaded verification documents.
7. Database security: Supabase RLS to control access to records.
8. Notifications: Resend API and Supabase for email and in website notifications.
9. Hosting: Vercel for unified deployment (Frontend and Backend).
10. Version control: GitHub to store and manage project code.

**Why Supabase?**

Supabase provides PostgreSQL database hosting, authentication, file storage and automatically generated APIs. This reduces the amount of backend infrastructure that needs to be developed separately. 

Supabase will replace MySQL completely. You will use PostgreSQL through Supabase.

### **Recommended architecture**

The application uses a modern, unified full-stack architecture hosted entirely on Vercel and Supabase.

**1. Application and Presentation Layer (Next.js on Vercel)**

Next.js handles all frontend pages, forms, role-based dashboards, tables and user interactions. Built-in Next.js Route Handlers (`app/api/*`) and Server Actions handle all backend business logic, including executing the asset matching algorithm, claimant verification workflows and dispatching notification requests.

**2. Data and Security Layer (Supabase)**

Supabase provides the hosted PostgreSQL database, authentication system, document storage and Row Level Security (RLS). It stores all user profiles, deceased person records, sample financial records, claimant details, documents, matching results, claims, notifications and audit logs.

The application flow will be:

User Browser ↔ Next.js Full-Stack App (Vercel) ↔ Supabase (PostgreSQL, Auth and Storage).

Supabase Auth with `@supabase/ssr` manages session cookies and role-based route protection, while Row Level Security policies ensure secure data isolation between family users, institutions and administrators.

## **3. Website modules and required functionality**

The website should contain the following modules.

### **Module 1. Home page**

The home page introduces Virasat Setu and explains why the platform is needed.

It should contain:

1. Website name and navigation bar.
2. Introduction to the platform.
3. Explanation of unclaimed financial assets.
4. Information about bank deposits, insurance and mutual funds.
5. A section explaining how the platform works.
6. Login and registration options.
7. Frequently asked questions.
8. Contact and help information.

The main button should be called Discover Unclaimed Assets. It will redirect visitors to the login or registration page.

### **Module 2. User registration and authentication**

This module allows families and other authorised users to create accounts.

Registration fields should include:

1. Full name.
2. Email address.
3. Mobile number.
4. Password.
5. Confirm password.

Use Supabase Auth for registration, login, logout, password recovery and email verification.

After successful login, the user should be redirected to the correct dashboard according to their assigned role.

The project should support three roles: Family User, Administrator and Institution Representative.

Create a separate `profiles` table in Supabase to store additional user information and role details. The user's profile ID should reference their Supabase Auth user ID.

### **Module 3. Family dashboard**

The dashboard will provide an overview of the user's activities.

It should contain:

1. Welcome message.
2. Add Deceased Family Member button.
3. Total deceased records submitted.
4. Total potential assets identified.
5. Number of claims in progress.
6. Number of unread notifications.
7. Recent activity.
8. Claim status summary.

The information must be retrieved dynamically from Supabase.

For example, when an asset is discovered, the asset count should automatically update. When a claim is processed, its status should also update on the dashboard.

### **Module 4. Deceased person registration**

This module allows a family member to submit details of a deceased individual.

The form should contain three sections.

**Personal information**

1. Full name.
2. Date of birth.
3. Date of death.
4. Gender.
5. Last known city and state.

**Registration information**

1. Death certificate reference number.
2. Death registration date.
3. Issuing authority.
4. Sample identity reference.

**Claimant information**

1. Name of the person submitting the record.
2. Relationship with the deceased.
3. Email address.
4. Mobile number.
5. Claimant type, nominee or legal heir.

The user should also be able to upload a sample death certificate and supporting documents.

After submission, the information will be stored in Supabase and assigned the status Pending Verification.

The administrator can then review the record and approve it, reject it or request additional information.

Only approved death records should be used by the matching system.

For this college prototype, all submitted records and documents should be fictional.

### **Module 5. Financial institution databases**

This is the main data source for the asset discovery feature.

Three separate datasets should be created inside Supabase.

**A. Bank records**

Store the following information:

1. Account holder name.
2. Date of birth.
3. Sample identity reference.
4. Bank name.
5. Account reference.
6. Account category.
7. Nominee reference.
8. Account status.
9. Unclaimed status.

**B. Insurance records**

Store:

1. Policyholder name.
2. Date of birth.
3. Sample identity reference.
4. Insurance company.
5. Policy reference.
6. Policy category.
7. Nominee reference.
8. Policy status.
9. Payout status.

**C. Mutual fund records**

Store:

1. Investor name.
2. Date of birth.
3. Sample identity reference.
4. Fund company.
5. Folio reference.
6. Nominee reference.
7. Investment status.
8. Claim status.

You should populate these databases with fictional information during development.

For example, you can create 30 deceased person records, 40 bank records, 25 insurance records and 25 mutual fund records.

Some records should match each other, while others should not. This will help demonstrate both successful and unsuccessful searches.

### **Module 6. Asset discovery and matching algorithm**

This is the central technical feature of Virasat Setu.

Once an administrator verifies a deceased person's record, the backend should automatically search the three financial datasets.

The matching process will work as follows.

1. Receive the verified deceased person's details.
2. Search the bank records.
3. Search the insurance records.
4. Search the mutual fund records.
5. Compare relevant identity information.
6. Calculate the matching score.
7. Store potential matches in the database.
8. Display the results on the family dashboard.
9. Send a notification when a potential match is identified.

You can implement a simple weighted matching algorithm.

Weighted matching scoring model:
1. Exact sample identity reference: 50 points.
2. Name similarity: 25 points.
3. Exact date of birth: 15 points.
4. Other matching reference details: 10 points.
5. Total maximum score: 100 points.

The score will be used for candidate identification, not legal identity verification.

Define three possible outcomes.

Three possible outcomes:
1. Score 80 to 100: Strong potential match.
2. Score 60 to 79: Requires manual review.
3. Score below 60: No match generated.

Exact sample identity references should receive priority. Name similarity alone should never be enough to confirm an identity.

The matching results should be stored in a dedicated `asset_matches` table.

Each result should contain the deceased person's ID, financial asset ID, matching score, matching reason and review status.

### **Module 7. Asset discovery results**

The results page will display all potential assets identified for a deceased person.

Separate the results into three categories.

1. Bank deposits.
2. Insurance policies.
3. Mutual fund investments.

Each result should display the institution name, masked reference number, asset category, matching status and claim status.

You can also display fictional asset values to make the demonstration more understandable.

The user should be able to select an asset and view its details after claimant verification.

An important distinction is that a matching result only indicates a potential financial connection. It does not establish ownership or guarantee that a claim can be approved.

### **Module 8. Nominee and legal heir verification**

This module verifies the person attempting to claim an identified asset.

The claimant should submit:

1. Name.
2. Relationship with the deceased.
3. Claimant type.
4. Supporting document.
5. Contact information.
6. Selected financial asset.

The administrator or institution representative will review the submitted details.

The verification status can be:

1. Pending.
2. Approved.
3. Rejected.
4. Additional Documents Required.

For the college prototype, verification will be performed manually through the administrator dashboard.

This module demonstrates the difference between identifying an asset and establishing the claimant's authority to claim it.

### **Module 9. Notification system**

The notification system should support both in website notifications and email notifications.

Notifications should be generated when:

1. A deceased person's record is verified.
2. A potential financial asset is discovered.
3. Claimant verification is completed.
4. A claim status changes.
5. Additional documents are requested.

The process will be:

1. An activity occurs in the application.
2. Next.js server logic identifies the event.
3. A notification message is generated.
4. The notification is stored in the Supabase `notifications` table.
5. An email is sent to the registered test email address.
6. The notification is displayed in the user's notification centre.
7. The delivery and read status are updated.

Use an email service such as Resend or an SMTP provider for actual email delivery.

Supabase Auth can manage authentication emails, while your application notification system handles asset discovery and claim updates.

For example, the notification can say:

"Dear User, a potential financial record associated with your deceased family member has been identified. Please log in to Virasat Setu and complete the verification process to view further information."

Do not send account numbers, financial balances or sensitive personal information directly through email or SMS.

SMS can be simulated in the initial prototype.

### **Module 10. Claim management and tracking**

After a claimant is verified, they can initiate a simulated claim for a potential financial asset.

The claim form should contain:

1. Deceased person's name.
2. Selected financial asset.
3. Claimant information.
4. Supporting document references.
5. Date of submission.

The claim will be stored in Supabase.

The financial institution representative can update its status through the institution dashboard.

Use the following statuses:

1. Submitted.
2. Under Review.
3. Documents Required.
4. Approved.
5. Rejected.
6. Completed.

Users should be able to see the current status, previous status updates and any instructions from the institution.

The prototype will simulate claim processing. It will not submit actual claims to banks or transfer money.

### **Module 11. Administrator dashboard**

The administrator dashboard will manage the entire application.

It should provide the following features:

1. View registered users.
2. View submitted deceased person records.
3. Verify or reject records.
4. View financial sample databases.
5. Trigger or review matching operations.
6. Review potential asset matches.
7. Approve or reject claimant verification.
8. View all claims.
9. Manage institution accounts.
10. View notification history.
11. Monitor system activity.

The administrator should also be able to manually add sample bank, insurance and mutual fund records.

This will make it easier to demonstrate the project without editing the database manually.

### **Module 12. Financial institution dashboard**

This dashboard will simulate the working environment of a financial institution.

A representative will log in and see the financial records belonging to their assigned sample institution.

The representative should be able to:

1. View potential matching assets assigned to the institution.
2. View claimant verification requests.
3. Review supporting document references.
4. Update the claim status.
5. Request additional documentation.
6. Add a note about claim progress.

The institution should not be able to view unrelated bank or insurance records.

For the prototype, institution access will be controlled through user roles and institution IDs.

## **4. Supabase database design**

Use Supabase PostgreSQL as the central database.

For easier development, create the following tables.

Database Tables Summary:
1. profiles: User information and roles.
2. deceased_persons: Deceased individual records.
3. claimants: Nominee and legal heir details.
4. claimant_relationships: Relationship between claimants and deceased persons.
5. documents: Uploaded document references.
6. institutions: Bank, insurance and fund company information.
7. financial_assets: Sample financial records.
8. asset_matches: Matching algorithm results.
9. claims: Claim applications and statuses.
10. notifications: Email and in website notification records.
11. audit_logs: Record of important user and administrator actions.

### **Important database relationships**

The `profiles` table will connect to Supabase Auth through the user's ID.

Each deceased person record will be connected to the user who submitted it.

Each claimant relationship will be connected to a deceased person and a claimant.

Each financial asset will be connected to an institution.

Each matching result will connect a deceased person to a potential financial asset.

Each claim will connect the claimant to a particular matching result.

Each notification will belong to its intended recipient.

The `audit_logs` table will maintain a history of important activities, such as verification decisions and claim status changes.

Use UUID values for primary keys and foreign keys. Add timestamps to records that need activity tracking.

### **Supabase Storage**

Create a private storage bucket called `claim-documents`.

Use it to store sample death certificates and supporting documents.

Store the file path and document metadata in the `documents` table rather than storing the actual file inside a database column.

Access to documents should be restricted to authorised users. Supabase Storage supports access control through policies.

Supabase Documentation



## **5. Security and access control**

Since the project involves financial and identity information, security should be included in the design even though all prototype records will be fictional.

Implement the following controls.

1. Use Supabase Auth for authentication.
2. Hash passwords through the authentication service.
3. Enable Row Level Security on all tables exposed through the Supabase API.
4. Allow family users to access only their own records.
5. Allow institution representatives to access only records assigned to their institutions.
6. Restrict administrative functions to administrator accounts.
7. Keep uploaded documents in private storage.
8. Use signed document URLs with limited validity when access is approved.
9. Keep API secrets in server environment variables.
10. Maintain audit logs for administrative actions.

The Supabase publishable key (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) can be safely used in browser client components when appropriate Row Level Security policies are enabled. The Supabase secret service role key (`SUPABASE_SERVICE_ROLE_KEY`) must only be accessed inside server-side Next.js Route Handlers or Server Actions and must never be exposed with the `NEXT_PUBLIC_` prefix because it can bypass Row Level Security. 

For the college prototype, do not use real Aadhaar numbers, PAN numbers, bank account information or real death certificates.

## **6. Backend API design**

Next.js Route Handlers (`app/api/.../route.ts`) will provide the server-side operations and business logic.

The following API routes are recommended:

Recommended API endpoints:
1. POST /api/deceased (Next.js File Path: app/api/deceased/route.ts): Submit a deceased person record.
2. GET /api/deceased (Next.js File Path: app/api/deceased/route.ts): Retrieve authorised records.
3. GET /api/deceased/{id} (Next.js File Path: app/api/deceased/[id]/route.ts): View an individual record.
4. PATCH /api/deceased/{id}/verify (Next.js File Path: app/api/deceased/[id]/verify/route.ts): Verify a death record.
5. POST /api/matching/{id} (Next.js File Path: app/api/matching/[id]/route.ts): Start asset matching.
6. GET /api/matches/{id} (Next.js File Path: app/api/matches/[id]/route.ts): Retrieve matching results.
7. POST /api/claimants (Next.js File Path: app/api/claimants/route.ts): Submit claimant information.
8. PATCH /api/claimants/{id}/verify (Next.js File Path: app/api/claimants/[id]/verify/route.ts): Update claimant verification.
9. POST /api/claims (Next.js File Path: app/api/claims/route.ts): Submit a claim.
10. GET /api/claims/{id} (Next.js File Path: app/api/claims/[id]/route.ts): View claim details.
11. PATCH /api/claims/{id}/status (Next.js File Path: app/api/claims/[id]/status/route.ts): Update claim status.
12. GET /api/notifications (Next.js File Path: app/api/notifications/route.ts): Retrieve user notifications.
13. GET /api/admin/records (Next.js File Path: app/api/admin/records/route.ts): Retrieve administrative records.

These endpoints validate the user's Supabase authentication session and role before executing operations. The matching algorithm is implemented in TypeScript (using `string-similarity` for fuzzy name matching alongside strict equality for identifiers and dates) and executed securely inside the Route Handler.

The backend also validates submitted information, handles errors gracefully and prevents duplicate submissions.

## **7. Complete application workflow**

The entire prototype should work through the following sequence.

**Step 1. User registration**

A family member creates an account using Supabase Auth.

**Step 2. Deceased person submission**

The user submits the deceased person's information and sample documents.

**Step 3. Administrator verification**

The administrator reviews the submitted record and approves it.

**Step 4. Automatic matching**

The Next.js backend API searches the three financial datasets and identifies possible matching assets.

**Step 5. Matching results**

The potential assets are stored in Supabase and displayed on the user's dashboard.

**Step 6. Notification**

The system generates an in website notification and sends an email to the user.

**Step 7. Claimant verification**

The claimant submits supporting documents and relationship information.

**Step 8. Institution review**

The institution representative reviews the request and updates the status.

**Step 9. Claim tracking**

The family member views the latest status through their dashboard.

This complete workflow should be functional in the final prototype.

## **8. Hosting and deployment plan**

The hosting arrangement is a unified full-stack deployment using **Vercel** for the Next.js application and **Supabase** for the database, authentication and document storage. This eliminates the need for separate hosting platforms (such as Render), avoids cold-start spin-down delays, and completely eliminates cross-origin (CORS) configuration issues.

### **A. Supabase setup**

1. Create a Supabase project at [supabase.com](https://supabase.com).
2. Create the database tables using SQL in the Supabase SQL Editor.
3. Configure Supabase Auth and email provider settings.
4. Configure user roles inside the `profiles` table.
5. Enable Row Level Security (RLS) across all tables.
6. Create the private document storage bucket called `claim-documents`.
7. Add fictional sample data for institutions and financial records.
8. Collect the Project URL, Publishable Anon Key (`NEXT_PUBLIC_SUPABASE_ANON_KEY`), and Secret Service Role Key (`SUPABASE_SERVICE_ROLE_KEY`).

### **B. Full-stack deployment on Vercel**

1. Push the Next.js project to GitHub.
2. Sign in to [Vercel](https://vercel.com) and click **Add New -> Project**.
3. Import the GitHub repository.
4. Vercel automatically detects the **Next.js** framework with zero manual configuration.
5. Add the following environment variables in Vercel:

`NEXT_PUBLIC_SUPABASE_URL`

`NEXT_PUBLIC_SUPABASE_ANON_KEY`

`SUPABASE_SERVICE_ROLE_KEY`

`RESEND_API_KEY`

6. Click **Deploy**. Vercel will build the frontend pages and serverless API route handlers, deploying them to a secure production domain like `https://virasat-setu.vercel.app`.

### **C. Key deployment advantages**

1. **Same-domain API Routing:** Frontend pages and backend APIs share the exact same domain. Client requests call relative paths like `/api/matching/...`, completely eliminating CORS preflight overhead and cross-domain configuration errors.
2. **Instant Wake-ups (No Sleep Delays):** Unlike free container platforms that take 50+ seconds to wake up from inactivity, Vercel serverless functions handle requests with cold starts of approximately 100 to 300 milliseconds.
3. **Edge Route Protection:** Next.js `middleware.ts` verifies Supabase Auth cookies at the edge, redirecting unauthorized users before dashboard pages even render.

## **9. Suggested project folder structure**

Organise the project as a modern, unified Next.js (App Router) codebase:

```
virasat-setu/
    app/
        (auth)/
            login/
                page.tsx
            register/
                page.tsx
        (dashboard)/
            family/
                page.tsx
            admin/
                page.tsx
            institution/
                page.tsx
        api/
            deceased/
                route.ts
                [id]/
                    route.ts
                    verify/
                        route.ts
            matching/
                [id]/
                    route.ts
            matches/
                [id]/
                    route.ts
            claimants/
                route.ts
                [id]/
                    verify/
                        route.ts
            claims/
                route.ts
                [id]/
                    route.ts
                    status/
                        route.ts
            notifications/
                route.ts
            admin/
                records/
                    route.ts
        layout.tsx
        page.tsx
        globals.css
    components/
        ui/                     # Buttons, modals, badges like shadcn/ui
        forms/                  # Registration, deceased submission, claim forms
        dashboard/              # Stats cards, asset tables, notification panel
        shared/                 # Navbar, footer, breadcrumbs
    lib/
        supabase/
            client.ts           # Browser Supabase client
            server.ts           # Server-side Supabase client (cookie-based)
            admin.ts            # Service role client for privileged backend ops
        matching.ts             # Weighted asset matching algorithm
        email.ts                # Resend transactional email helper
        utils.ts                # Tailwind utility functions (cn, formatters)
    seed/
        sample_data.sql         # Seed data script for Supabase tables
    types/
        database.types.ts       # Generated Supabase TypeScript types
    middleware.ts               # Role-based route guard and session refresh
    package.json
    tsconfig.json
    tailwind.config.js
    .env.local.example
```

The `app/api/` folder contains all backend Route Handlers executing server-side logic.

The `lib/matching.ts` file contains the pure TypeScript weighted matching algorithm.

The `middleware.ts` file intercepts incoming requests to enforce role-based access for Family, Admin, and Institution dashboards.

Keep sensitive credentials in `.env.local` during development and configure them in Vercel project settings for production.

## **10. Development roadmap**

Develop the project in the following order so that every part can be tested before moving to the next stage.

Development Roadmap Phases:
1. Phase 1: Finalise requirements and UI design (Expected outcome: Page structure and workflow).
2. Phase 2: Create Supabase project and database (Expected outcome: Working database).
3. Phase 3: Implement authentication and roles (Expected outcome: Registration and login).
4. Phase 4: Develop home page and dashboards (Expected outcome: Functional frontend).
5. Phase 5: Build deceased person registration (Expected outcome: Record submission).
6. Phase 6: Create financial databases (Expected outcome: Three financial datasets).
7. Phase 7: Develop matching algorithm (Expected outcome: Automated asset discovery).
8. Phase 8: Build claimant verification (Expected outcome: Verification workflow).
9. Phase 9: Develop notification system (Expected outcome: Email and website alerts).
10. Phase 10: Build claim tracking and institution dashboard (Expected outcome: Complete claim workflow).
11. Phase 11: Develop admin dashboard (Expected outcome: Record and system management).
12. Phase 12: Testing and deployment (Expected outcome: Complete hosted prototype).

A realistic target is approximately four to six weeks for a small student team, depending on development experience.

## **11. Testing requirements**

Before submitting the project, test the following scenarios.

1. New user can register and log in.
2. Different user roles receive different access permissions.
3. User can submit a deceased person record.
4. Administrator can approve or reject records.
5. Matching starts only after record verification.
6. Matching identifies correct sample bank records.
7. Matching identifies correct sample insurance records.
8. Matching identifies correct mutual fund records.
9. Unrelated records do not appear as confirmed matches.
10. Claimant can submit verification documents.
11. Administrator can update verification status.
12. User receives a notification after an asset is identified.
13. Email notification is delivered to the test email address.
14. Institution representative can update claim status.
15. Family user can view claim progress.
16. Unauthorised users cannot view another user's records.
17. Uploaded documents cannot be accessed by unauthorised users.
18. Website works on both desktop and mobile screens.
19. Deployed Next.js application and API routes communicate seamlessly with Supabase without CORS errors.

## **12. Final prototype demonstration**

Your final presentation should demonstrate one complete example rather than showing each page separately.

Use the following fictional scenario.

A deceased person named Rajesh Kumar has a bank deposit, an insurance policy and a mutual fund investment in your sample database.

1. Register a family member as a new user.
2. Log in to the family dashboard.
3. Submit Rajesh Kumar's details.
4. Log in as administrator and verify the submitted record.
5. Let the matching algorithm search all three financial datasets.
6. Display the potential bank, insurance and mutual fund records.
7. Show the automatic email and in website notification.
8. Log back in as the family member.
9. Submit nominee or legal heir verification information.
10. Log in as institution representative.
11. Review the sample claim and update its status.
12. Return to the family dashboard and show the updated claim status.

The evaluator should be able to see the entire process working through the deployed website.

## **13. Final project scope and limitations**

It is important to clearly distinguish prototype functionality from the proposed real world system.

Prototype Scope and Limitations Comparison:
1. User registration: Fully functional in college prototype; fully functional in real implementation.
2. Death record submission: Sample records in college prototype; authorised government integration in real implementation.
3. Financial databases: Fictional datasets in college prototype; authorised institution integration in real implementation.
4. Asset matching: Functional algorithm in college prototype; secure institutional matching in real implementation.
5. Claimant verification: Manual sample verification in college prototype; legally valid verification in real implementation.
6. Notifications: Functional email and in website alerts in college prototype; approved notification integration in real implementation.
7. Claim tracking: Simulated claim processing in college prototype; institution connected claim processing in real implementation.
8. Money transfer: Not included in college prototype; handled directly by financial institutions in real implementation.

The prototype should demonstrate the technology and process without pretending to have access to restricted databases.

## **14. Final recommended implementation scope**

For a college project, I recommend prioritising these features as essential:

1. Complete user registration and login through Supabase Auth.
2. Family dashboard with dynamic information.
3. Deceased person registration and document upload.
4. Administrator verification.
5. Three fictional financial institution datasets.
6. Automated matching algorithm.
7. Asset discovery results page.
8. Claimant verification workflow.
9. Automatic email and in website notifications.
10. Institution dashboard.
11. Claim submission and tracking.
12. Complete deployment on Vercel and Supabase.

Do not spend too much development time trying to connect real government APIs, real banks or real identity verification services. Those are outside the realistic scope of this college prototype.

**Final recommendation:** Build a functional end to end website where every important operation works with Supabase data. The strongest part of your demonstration should be the automatic matching of three financial datasets following administrator approval of a death record, followed by notification and claim tracking.

This will show that Virasat Setu is not just a website design or a conceptual business model. It is a working prototype of the proposed digital asset discovery system.