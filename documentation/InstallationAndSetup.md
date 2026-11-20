# Virasat Setu Installation and Deployment Guide:

This document provides clear technical instructions for setting up, configuring, testing and deploying the Virasat Setu platform in both local development and cloud production environments.

Deployment Pipeline Overview:
1. Local Development: Python 3.10+ Environment, FastAPI and Automated Verification Suite.
2. Cloud Database Setup: Supabase PostgreSQL Project with Schema and Seed Migrations.
3. Serverless Production: Deploy to Vercel via Git Repository and Configure Cloud Environment Variables.


## System Requirements and Prerequisites:

Ensure your development computer meets the following technical requirements:

1. Operating System: Microsoft Windows, Linux Ubuntu or Apple macOS.
2. Python Runtime: Python version three point ten or higher installed with pip package manager.
3. Git Version Control: Git installed and configured with your personal account.
4. Supabase Account: Access to Supabase cloud console for hosted PostgreSQL database services.
5. Vercel Account: Access to Vercel cloud platform for full stack serverless deployment.


## Local Environment Setup:

Follow these steps to establish a running instance on your local machine:

1. Clone Project Repository: Clone the official Virasat Setu repository to your local computer.
2. Open Project Folder: Navigate inside the root DTIProject directory using your terminal or command prompt.
3. Create Virtual Environment: Execute python with option m venv venv to create an isolated Python virtual environment.
4. Activate Virtual Environment on Windows: In PowerShell execute venv Scripts Activate ps1 or in Command Prompt run venv Scripts activate bat.
5. Activate Virtual Environment on Linux or macOS: In bash or zsh execute source venv bin activate.
6. Install Dependencies: Execute pip install with option r requirements txt to install FastAPI, Uvicorn, SQLAlchemy, Pydantic and auxiliary libraries.
7. Configure Environment Variables: Copy dot env example to create dot env and verify default parameters.


## Running the Application Locally:

Virasat Setu includes convenient runners for quick local execution:

1. Windows Quick Execution: Double click the file run server bat in your file explorer to start the application automatically.
2. Standard Terminal Execution: Run python run server py from your command line within the activated virtual environment.
3. Access Web Interface: Open your web browser and navigate to http 127 0 0 1 8000 to interact with the live portal.
4. Automatic Database Creation: On initial startup the application creates all eleven tables within local SQLite storage if cloud PostgreSQL is not reachable.


## Executing the Verification Test Suite:

Virasat Setu includes comprehensive automated test suites verifying all core services, artificial intelligence features, cybersecurity defenses and browser user interactions:

1. System Workflow Test Suite: Run python test system py to verify citizen login, deceased record retrieval, one hundred point matching calculations, claimant registration, claim initiation, administrative oversight, institutional reviews, notification logging and frontend delivery.
2. AI and Google OAuth Test Suite: Run python test ai features py to verify Google OAuth configuration, AI Legal Copilot queries, machine learning transliteration variants, claim health probability scoring, and administrative fraud anomaly access control.
3. Cybersecurity Penetration Test Suite: Run python test security py to verify SQL injection defense, script injection rejection, CSRF custom header verification, arbitrary file upload defense, and HTTP defensive security headers.
4. Agentic Browser UI Automation Suite: Run python agentic ui tester py to execute a complete twenty one step automated Playwright browser session testing all buttons, inputs, tabs, modals and confirming zero console errors.


## Supabase Cloud Database Configuration:

To connect the application to hosted Supabase cloud PostgreSQL:

1. Access Supabase Project: Log into the Supabase management console for project id elmvmptsxmkzcowwnmlk in region ap southeast two.
2. Retrieve API Keys: Ensure you have the Publishable Anon Key and the Secret Service Role Key ready in your environment configuration.
3. Open SQL Editor: Navigate to the SQL Editor within your Supabase project dashboard.
4. Execute Schema Script: Copy the contents of supabase schema sql into the editor and execute it to create all eleven tables, foreign keys and Row Level Security policies.
5. Execute Seed Script: Copy the contents of supabase seed sql into the editor and run it to populate the ninety four central financial records and institutional demo accounts.
6. Verify Table Health: Navigate to the Table Editor in Supabase to confirm that tables including financial assets, institutions, deceased persons and claims contain populated data.


## Vercel Production Deployment:

To deploy the unified full stack application to Vercel:

1. Connect Repository: Log into your Vercel dashboard and click Add New Project.
2. Import Git Repository: Select the VirasatSetu repository from your GitHub account.
3. Framework Detection: Vercel detects the configuration automatically via vercel json and api index py without requiring custom build scripts.
4. Configure Environment Variables: In the Project Settings Environment Variables section add SUPABASE URL, SUPABASE ANON KEY, SUPABASE SERVICE ROLE KEY, GEMINI API KEY, and GOOGLE CLIENT SECRET.
5. Deploy Application: Click Deploy to trigger serverless compilation and distribution.
6. Production Verification: Open your deployed Vercel domain to verify that frontend pages, AI endpoints and API controllers communicate seamlessly under a single domain origin.



## Operational Troubleshooting:

1. Port In Use Error: If port 8000 is occupied by another process, adjust the port setting in run server py or terminate the conflicting background process.
2. Missing Dependencies: If module import errors appear, execute pip install with option r requirements txt again to ensure all packages are installed.
3. Database Permission Discrepancy: Ensure that the Supabase Service Role Key is configured properly in environment variables when executing privileged administrative actions.
