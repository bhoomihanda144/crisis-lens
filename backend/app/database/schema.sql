-- ==============================================================================
-- CrisisLens: Trust-Aware Emergency Intelligence System
-- Database Schema: Supabase PostgreSQL (API Contract v1.0 Compliant)
-- Member 2: Backend, Database and Integration Lead
-- ==============================================================================

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- 2. Timestamp Trigger Function
-- ==============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- 3. Table Definitions (Strict Dependency Order)
-- Human-readable IDs matching API contract ('inc_001', 'rpt_001', 'sim_001', etc.)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Table 1: incidents
-- Aggregated emergency events consolidating multiple reports.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('inc_' || substr(md5(random()::text), 1, 8)),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    incident_type VARCHAR(50) NOT NULL CHECK (incident_type IN (
        'flood', 'fire', 'earthquake', 'landslide', 'structural', 'medical', 'other'
    )),
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN (
        'active', 'monitoring', 'resolved'
    )),
    severity VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (severity IN (
        'low', 'medium', 'high', 'critical'
    )),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    location_name TEXT,
    report_count INTEGER NOT NULL DEFAULT 0,
    independent_source_count INTEGER NOT NULL DEFAULT 0,
    first_reported_at TIMESTAMPTZ DEFAULT now(),
    timeline JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trigger_incidents_updated_at ON incidents;
CREATE TRIGGER trigger_incidents_updated_at
    BEFORE UPDATE ON incidents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------------------------
-- Table 2: reports
-- Raw crisis reports submitted by citizens, sensors, news, or responders.
-- References: incidents(id)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('rpt_' || substr(md5(random()::text), 1, 8)),
    incident_id VARCHAR(50) REFERENCES incidents(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    title VARCHAR(255),
    source_type VARCHAR(50) NOT NULL DEFAULT 'citizen' CHECK (source_type IN (
        'citizen', 'social_media', 'news', 'official', 'sensor', 'responder'
    )),
    source_name VARCHAR(255) DEFAULT 'Citizen reporter',
    author_id VARCHAR(100),
    location_name TEXT,
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    reported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    forwarded_from VARCHAR(50) REFERENCES reports(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending_analysis' CHECK (status IN (
        'pending_analysis', 'analyzed', 'verified', 'rejected', 'needs_more_info'
    )),
    media_urls JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trigger_reports_updated_at ON reports;
CREATE TRIGGER trigger_reports_updated_at
    BEFORE UPDATE ON reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------------------------
-- Table 3: report_relationships
-- Cross-report linkages for evidence graphs (corroboration, duplicate, conflict).
-- References: reports(id) [source and target]
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS report_relationships (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('edge_' || substr(md5(random()::text), 1, 8)),
    source_report_id VARCHAR(50) NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    target_report_id VARCHAR(50) NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
        'original', 'duplicate', 'forwarded', 'corroborating', 'conflicting'
    )),
    label VARCHAR(100),
    confidence_score NUMERIC(4, 3) NOT NULL DEFAULT 1.000 CHECK (confidence_score >= 0.000 AND confidence_score <= 1.000),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_different_reports CHECK (source_report_id <> target_report_id),
    CONSTRAINT uq_report_pair UNIQUE (source_report_id, target_report_id, relationship_type)
);

-- ------------------------------------------------------------------------------
-- Table 4: analysis_results
-- AI Engine inference outputs preserving full analysis JSON and separate scores.
-- References: reports(id)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analysis_results (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('anl_' || substr(md5(random()::text), 1, 8)),
    report_id VARCHAR(50) NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    engine_version VARCHAR(50) NOT NULL DEFAULT '0.1.0',
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    duplicate JSONB NOT NULL DEFAULT '{"is_duplicate": false, "matches": []}'::jsonb,
    source_verification JSONB NOT NULL DEFAULT '{}'::jsonb,
    freshness JSONB NOT NULL DEFAULT '{}'::jsonb,
    conflicts JSONB NOT NULL DEFAULT '[]'::jsonb,
    scores JSONB NOT NULL DEFAULT '{}'::jsonb,
    recommendation JSONB NOT NULL DEFAULT '{}'::jsonb,
    raw_ai_output JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trigger_analysis_results_updated_at ON analysis_results;
CREATE TRIGGER trigger_analysis_results_updated_at
    BEFORE UPDATE ON analysis_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------------------------
-- Table 5: priority_scores
-- Separate Urgency, Confidence, and Verification scores (0-100 integers).
-- Supports incident-level priority rankings as well as report-level scoring.
-- References: reports(id), incidents(id)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS priority_scores (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('psc_' || substr(md5(random()::text), 1, 8)),
    incident_id VARCHAR(50) REFERENCES incidents(id) ON DELETE CASCADE,
    report_id VARCHAR(50) REFERENCES reports(id) ON DELETE CASCADE,
    rank INTEGER,
    urgency_score INTEGER NOT NULL CHECK (urgency_score >= 0 AND urgency_score <= 100),
    urgency_level VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (urgency_level IN (
        'low', 'medium', 'high', 'critical'
    )),
    urgency_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_confidence INTEGER NOT NULL CHECK (evidence_confidence >= 0 AND evidence_confidence <= 100),
    confidence_level VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (confidence_level IN (
        'low', 'medium', 'high'
    )),
    confidence_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification_priority INTEGER NOT NULL CHECK (verification_priority >= 0 AND verification_priority <= 100),
    verification_level VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (verification_level IN (
        'low', 'medium', 'high'
    )),
    verification_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    explanation JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_next_steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    requires_human_decision BOOLEAN NOT NULL DEFAULT true,
    human_decision JSONB NOT NULL DEFAULT '{"status": "not_decided", "decided_by": null, "decided_at": null}'::jsonb,
    calculated_by VARCHAR(100) NOT NULL DEFAULT 'rule_engine',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_target_exists CHECK (incident_id IS NOT NULL OR report_id IS NOT NULL)
);

DROP TRIGGER IF EXISTS trigger_priority_scores_updated_at ON priority_scores;
CREATE TRIGGER trigger_priority_scores_updated_at
    BEFORE UPDATE ON priority_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------------------------
-- Table 6: verifications
-- Human-in-the-loop responder and dispatcher verification audit log.
-- References: reports(id)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS verifications (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('vrf_' || substr(md5(random()::text), 1, 8)),
    report_id VARCHAR(50) NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL CHECK (action IN (
        'confirm', 'reject', 'request_more_info'
    )),
    note TEXT,
    verified_by VARCHAR(100) NOT NULL,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------------------------
-- Table 7: simulations
-- Independent what-if scenario modeling (resource demand, road blockages).
-- Operates independently of real incidents (incident_id is nullable).
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulations (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('sim_' || substr(md5(random()::text), 1, 8)),
    incident_id VARCHAR(50) REFERENCES incidents(id) ON DELETE SET NULL,
    scenario_name VARCHAR(255) NOT NULL,
    is_simulation BOOLEAN NOT NULL DEFAULT true,
    affected_population INTEGER NOT NULL DEFAULT 0,
    disaster_severity INTEGER NOT NULL DEFAULT 3 CHECK (disaster_severity >= 1 AND disaster_severity <= 5),
    rescue_teams INTEGER NOT NULL DEFAULT 0,
    blocked_roads INTEGER NOT NULL DEFAULT 0,
    available_ambulances INTEGER NOT NULL DEFAULT 0,
    inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    results JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'completed' CHECK (status IN (
        'queued', 'running', 'completed', 'failed'
    )),
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trigger_simulations_updated_at ON simulations;
CREATE TRIGGER trigger_simulations_updated_at
    BEFORE UPDATE ON simulations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- 4. Performance Indexes
-- (Created after all seven tables exist)
-- ==============================================================================

-- Indexes on incidents
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_incidents_location ON incidents(latitude, longitude);

-- Indexes on reports
CREATE INDEX IF NOT EXISTS idx_reports_incident_id ON reports(incident_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_source_type ON reports(source_type);
CREATE INDEX IF NOT EXISTS idx_reports_reported_at ON reports(reported_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_forwarded_from ON reports(forwarded_from);
CREATE INDEX IF NOT EXISTS idx_reports_location ON reports(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_reports_metadata ON reports USING gin(metadata);

-- Indexes on report_relationships (Evidence Graph)
CREATE INDEX IF NOT EXISTS idx_report_rel_source ON report_relationships(source_report_id);
CREATE INDEX IF NOT EXISTS idx_report_rel_target ON report_relationships(target_report_id);
CREATE INDEX IF NOT EXISTS idx_report_rel_type ON report_relationships(relationship_type);

-- Indexes on analysis_results
CREATE INDEX IF NOT EXISTS idx_analysis_results_report_id ON analysis_results(report_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_conflicts ON analysis_results USING gin(conflicts);
CREATE INDEX IF NOT EXISTS idx_analysis_results_scores ON analysis_results USING gin(scores);

-- Indexes on priority_scores
CREATE INDEX IF NOT EXISTS idx_priority_scores_incident_id ON priority_scores(incident_id);
CREATE INDEX IF NOT EXISTS idx_priority_scores_report_id ON priority_scores(report_id);
CREATE INDEX IF NOT EXISTS idx_priority_scores_rank ON priority_scores(rank);
CREATE INDEX IF NOT EXISTS idx_priority_scores_urgency ON priority_scores(urgency_score DESC);
CREATE INDEX IF NOT EXISTS idx_priority_scores_priority ON priority_scores(verification_priority DESC);

-- Indexes on verifications
CREATE INDEX IF NOT EXISTS idx_verifications_report_id ON verifications(report_id);
CREATE INDEX IF NOT EXISTS idx_verifications_action ON verifications(action);

-- Indexes on simulations
CREATE INDEX IF NOT EXISTS idx_simulations_incident_id ON simulations(incident_id);
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations(created_at DESC);

-- ==============================================================================
-- 5. Row Level Security (RLS) Enablement
-- ==============================================================================
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE priority_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;

-- ==============================================================================
-- 6. Backend-Only Access Policies
-- The frontend never connects directly to Supabase and holds no Supabase keys.
-- All data access flows strictly through the FastAPI backend via service_role.
-- Direct anon/public access from web browsers is rejected by default.
-- ==============================================================================

DROP POLICY IF EXISTS "service_role_full_access_incidents" ON incidents;
CREATE POLICY "service_role_full_access_incidents" ON incidents
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_full_access_reports" ON reports;
CREATE POLICY "service_role_full_access_reports" ON reports
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_full_access_report_relationships" ON report_relationships;
CREATE POLICY "service_role_full_access_report_relationships" ON report_relationships
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_full_access_analysis_results" ON analysis_results;
CREATE POLICY "service_role_full_access_analysis_results" ON analysis_results
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_full_access_priority_scores" ON priority_scores;
CREATE POLICY "service_role_full_access_priority_scores" ON priority_scores
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_full_access_verifications" ON verifications;
CREATE POLICY "service_role_full_access_verifications" ON verifications
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_full_access_simulations" ON simulations;
CREATE POLICY "service_role_full_access_simulations" ON simulations
    FOR ALL TO service_role USING (true) WITH CHECK (true);
