-- VIRASAT SETU: POSTGRESQL SCHEMA FOR SUPABASE
-- Digital Inheritance and Unclaimed Financial Asset Discovery Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Profiles Table (User Accounts and Roles)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    mobile VARCHAR(20),
    role VARCHAR(50) NOT NULL DEFAULT 'family_user', -- 'family_user', 'admin', 'institution_rep'
    institution_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Institutions Table (Banks, Insurance Companies, Mutual Funds)
CREATE TABLE IF NOT EXISTS public.institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'bank', 'insurance', 'mutual_fund'
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Add foreign key from profiles to institutions
ALTER TABLE public.profiles
    DROP CONSTRAINT IF EXISTS fk_profiles_institution;
ALTER TABLE public.profiles
    ADD CONSTRAINT fk_profiles_institution
    FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE SET NULL;

-- 3. Deceased Persons Table
CREATE TABLE IF NOT EXISTS public.deceased_persons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth VARCHAR(20) NOT NULL,
    date_of_death VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    last_known_city VARCHAR(100),
    last_known_state VARCHAR(100),
    death_cert_ref VARCHAR(100) NOT NULL,
    death_reg_date VARCHAR(20),
    issuing_authority VARCHAR(255),
    sample_identity_ref VARCHAR(100) NOT NULL, -- PAN, Sample Aadhaar
    status VARCHAR(50) NOT NULL DEFAULT 'Pending Verification', -- 'Pending Verification', 'Verified', 'Rejected'
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Claimants Table (Nominee and Legal Heir Details)
CREATE TABLE IF NOT EXISTS public.claimants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    deceased_person_id UUID NOT NULL REFERENCES public.deceased_persons(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    relationship VARCHAR(100) NOT NULL, -- 'Son', 'Spouse', 'Daughter', etc.
    email VARCHAR(255) NOT NULL,
    mobile VARCHAR(50) NOT NULL,
    claimant_type VARCHAR(50) NOT NULL DEFAULT 'Nominee', -- 'Nominee', 'Legal Heir'
    status VARCHAR(50) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected', 'Additional Documents Required'
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Financial Assets Table (Sample Datasets across Banks, Insurance and Mutual Funds)
CREATE TABLE IF NOT EXISTS public.financial_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES public.institutions(id) ON DELETE CASCADE,
    asset_type VARCHAR(50) NOT NULL, -- 'bank', 'insurance', 'mutual_fund'
    institution_name VARCHAR(255) NOT NULL,
    holder_name VARCHAR(255) NOT NULL,
    date_of_birth VARCHAR(20),
    sample_identity_ref VARCHAR(100) NOT NULL,
    account_ref VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    nominee_ref VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'Unclaimed',
    unclaimed_status VARCHAR(100) DEFAULT 'Dormant > 10 Yrs',
    approximate_value DOUBLE PRECISION DEFAULT 0.0,
    details_json TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Asset Matches Table (100-Point Weighted Algorithm Results)
CREATE TABLE IF NOT EXISTS public.asset_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deceased_person_id UUID NOT NULL REFERENCES public.deceased_persons(id) ON DELETE CASCADE,
    financial_asset_id UUID NOT NULL REFERENCES public.financial_assets(id) ON DELETE CASCADE,
    matching_score INTEGER NOT NULL,
    matching_reason TEXT NOT NULL,
    match_category VARCHAR(50) NOT NULL, -- 'Strong potential match', 'Requires manual review'
    review_status VARCHAR(50) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Claims Table (Claim Applications and Tracking)
CREATE TABLE IF NOT EXISTS public.claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_reference VARCHAR(50) UNIQUE NOT NULL,
    claimant_id UUID NOT NULL REFERENCES public.claimants(id) ON DELETE CASCADE,
    asset_match_id UUID NOT NULL REFERENCES public.asset_matches(id) ON DELETE CASCADE,
    deceased_person_id UUID NOT NULL REFERENCES public.deceased_persons(id) ON DELETE CASCADE,
    financial_asset_id UUID NOT NULL REFERENCES public.financial_assets(id) ON DELETE CASCADE,
    institution_id UUID NOT NULL REFERENCES public.institutions(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted', -- 'Submitted', 'Under Review', 'Documents Required', 'Approved', 'Rejected', 'Completed'
    remarks TEXT,
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. Documents Table (Uploaded Reference Metadata)
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    deceased_person_id UUID REFERENCES public.deceased_persons(id) ON DELETE SET NULL,
    claimant_id UUID REFERENCES public.claimants(id) ON DELETE SET NULL,
    claim_id UUID REFERENCES public.claims(id) ON DELETE SET NULL,
    document_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER DEFAULT 0,
    content_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 9. Notifications Table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL DEFAULT 'system',
    link VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT false,
    email_sent BOOLEAN NOT NULL DEFAULT false,
    email_logs TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 10. Audit Logs Table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_deceased_persons_identity ON public.deceased_persons(sample_identity_ref);
CREATE INDEX IF NOT EXISTS idx_deceased_persons_fullname ON public.deceased_persons(full_name);
CREATE INDEX IF NOT EXISTS idx_financial_assets_identity ON public.financial_assets(sample_identity_ref);
CREATE INDEX IF NOT EXISTS idx_financial_assets_holder ON public.financial_assets(holder_name);
CREATE INDEX IF NOT EXISTS idx_asset_matches_deceased ON public.asset_matches(deceased_person_id);
CREATE INDEX IF NOT EXISTS idx_claims_reference ON public.claims(claim_reference);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON public.notifications(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deceased_persons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claimants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Base RLS Policies for Service Role and Public Access
CREATE POLICY "Service role full access on profiles" ON public.profiles FOR ALL USING (true);
CREATE POLICY "Service role full access on deceased" ON public.deceased_persons FOR ALL USING (true);
CREATE POLICY "Service role full access on claimants" ON public.claimants FOR ALL USING (true);
CREATE POLICY "Service role full access on financial_assets" ON public.financial_assets FOR ALL USING (true);
CREATE POLICY "Service role full access on asset_matches" ON public.asset_matches FOR ALL USING (true);
CREATE POLICY "Service role full access on claims" ON public.claims FOR ALL USING (true);
CREATE POLICY "Service role full access on notifications" ON public.notifications FOR ALL USING (true);
CREATE POLICY "Service role full access on audit_logs" ON public.audit_logs FOR ALL USING (true);
