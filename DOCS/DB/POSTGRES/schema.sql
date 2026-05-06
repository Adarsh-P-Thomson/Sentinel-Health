-- Sentinel Health - PostgreSQL Schema
-- Version: 1.0
-- Description: Structured data for configuration, users, and high-value safety signals

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer', -- admin, analyst, viewer
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

COMMENT ON TABLE users IS 'User authentication and role management';
COMMENT ON COLUMN users.role IS 'User role: admin (full access), analyst (view + analyze), viewer (read-only)';

-- ============================================================================
-- PROJECTS & CONFIGURATION
-- ============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'active', -- active, paused, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

COMMENT ON TABLE projects IS 'Monitoring projects configured by admins';
COMMENT ON COLUMN projects.status IS 'Project status: active (running), paused (temporarily stopped), archived (historical)';

-- ============================================================================
-- KEYWORDS
-- ============================================================================

CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    category VARCHAR(100), -- drug, symptom, condition, brand
    priority VARCHAR(50) DEFAULT 'medium', -- high, medium, low
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_keywords_project ON keywords(project_id);
CREATE INDEX idx_keywords_category ON keywords(category);
CREATE INDEX idx_keywords_keyword ON keywords(keyword);
CREATE UNIQUE INDEX idx_keywords_unique ON keywords(project_id, keyword);

COMMENT ON TABLE keywords IS 'Keywords to monitor per project (drugs, symptoms, conditions)';
COMMENT ON COLUMN keywords.category IS 'Keyword type: drug, symptom, condition, brand';

-- ============================================================================
-- DATA SOURCES
-- ============================================================================

CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    source_type VARCHAR(100) NOT NULL, -- twitter, reddit, quora, forum
    source_name VARCHAR(255) NOT NULL, -- e.g., "r/pharmacy", "@healthnews"
    monitoring_interval VARCHAR(50) NOT NULL, -- realtime, daily, weekly
    is_active BOOLEAN DEFAULT true,
    config JSONB, -- Source-specific configuration (API keys, filters, etc.)
    last_crawled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_project ON data_sources(project_id);
CREATE INDEX idx_sources_type ON data_sources(source_type);
CREATE INDEX idx_sources_active ON data_sources(is_active);
CREATE INDEX idx_sources_interval ON data_sources(monitoring_interval);

COMMENT ON TABLE data_sources IS 'Configured data sources (X, Reddit, forums) for each project';
COMMENT ON COLUMN data_sources.config IS 'JSON configuration: API credentials, filters, rate limits';

-- ============================================================================
-- SEARCH EXECUTIONS
-- ============================================================================

CREATE TABLE search_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    source_id UUID REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Search parameters
    search_query TEXT NOT NULL, -- The actual search query executed
    keywords_used TEXT[], -- Array of keywords from the project used in this search
    
    -- Execution metadata
    search_type VARCHAR(50) NOT NULL, -- keyword_search, url_crawl, api_fetch
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed, partial
    
    -- Results tracking
    pages_found INTEGER DEFAULT 0,
    pages_stored INTEGER DEFAULT 0, -- Count of MongoDB raw_pages documents created
    posts_extracted INTEGER DEFAULT 0, -- Count of posts extracted from pages
    
    -- MongoDB references
    mongodb_page_ids TEXT[], -- Array of MongoDB raw_pages._id (ObjectId as strings)
    mongodb_post_ids TEXT[], -- Array of MongoDB raw_posts._id (ObjectId as strings)
    
    -- Timing
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    
    -- Error tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Next execution (for scheduled searches)
    next_scheduled_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_project ON search_executions(project_id);
CREATE INDEX idx_search_source ON search_executions(source_id);
CREATE INDEX idx_search_status ON search_executions(status);
CREATE INDEX idx_search_started_at ON search_executions(started_at DESC);
CREATE INDEX idx_search_next_scheduled ON search_executions(next_scheduled_at);

COMMENT ON TABLE search_executions IS 'Track each search/crawl execution with references to MongoDB raw data';
COMMENT ON COLUMN search_executions.mongodb_page_ids IS 'Array of MongoDB raw_pages._id references';
COMMENT ON COLUMN search_executions.mongodb_post_ids IS 'Array of MongoDB raw_posts._id references';

-- ============================================================================
-- SAFETY SIGNALS (High-Value Archive)
-- ============================================================================

CREATE TABLE safety_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    signal_type VARCHAR(100) NOT NULL, -- adverse_event, quality_issue, sentiment_spike, treatment_efficacy, drug_interaction
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    drug_name VARCHAR(255),
    symptom VARCHAR(255),
    condition VARCHAR(255),
    
    -- Aggregated metrics
    mention_count INTEGER DEFAULT 1,
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    virality_score DECIMAL(5,2), -- 0 to 100
    confidence_score DECIMAL(3,2), -- 0.0 to 1.0
    
    -- AI Analysis Summary
    ai_summary TEXT, -- Concise AI-generated summary
    key_findings TEXT[], -- Array of key findings
    clinical_significance TEXT, -- Clinical significance explanation
    recommended_action VARCHAR(50), -- monitor, investigate, escalate, archive
    action_rationale TEXT, -- Why this action is recommended
    
    -- Risk Assessment
    risk_category VARCHAR(50), -- no_risk, low_risk, moderate_risk, high_risk, critical_risk
    known_side_effect BOOLEAN DEFAULT false,
    fda_label_match BOOLEAN DEFAULT false,
    similar_reports_count INTEGER DEFAULT 0,
    
    -- Patient Impact
    patient_impact_score DECIMAL(3,2), -- 0.0 to 1.0
    quality_of_life_impact VARCHAR(50), -- none, mild, moderate, severe
    
    -- Source tracking
    source_type VARCHAR(100),
    source_ids TEXT[], -- Array of MongoDB analyzed_posts._id
    
    -- Temporal data
    first_detected_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trending_period VARCHAR(50), -- 1h, 6h, 24h, 7d
    
    -- Status & Assignment
    status VARCHAR(50) DEFAULT 'new', -- new, investigating, validated, false_positive, resolved, escalated
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    escalated_at TIMESTAMP,
    escalation_reason TEXT,
    
    -- Tags & Classification
    tags TEXT[], -- User or AI-generated tags
    categories TEXT[], -- Categorization (e.g., cardiovascular, neurological)
    
    -- AI metadata
    ai_analysis_summary TEXT,
    langsmith_trace_id VARCHAR(255),
    overall_confidence DECIMAL(3,2), -- Overall AI confidence
    
    -- Review & Validation
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    is_validated BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_project ON safety_signals(project_id);
CREATE INDEX idx_signals_severity ON safety_signals(severity);
CREATE INDEX idx_signals_status ON safety_signals(status);
CREATE INDEX idx_signals_drug ON safety_signals(drug_name);
CREATE INDEX idx_signals_symptom ON safety_signals(symptom);
CREATE INDEX idx_signals_detected_at ON safety_signals(first_detected_at DESC);
CREATE INDEX idx_signals_trending ON safety_signals(trending_period, virality_score DESC);
CREATE INDEX idx_signals_assigned ON safety_signals(assigned_to);
CREATE INDEX idx_signals_risk_category ON safety_signals(risk_category);
CREATE INDEX idx_signals_recommended_action ON safety_signals(recommended_action);
CREATE INDEX idx_signals_validated ON safety_signals(is_validated);
CREATE INDEX idx_signals_tags ON safety_signals USING GIN(tags);
CREATE INDEX idx_signals_categories ON safety_signals USING GIN(categories);

COMMENT ON TABLE safety_signals IS 'Validated, high-priority safety signals for permanent storage';
COMMENT ON COLUMN safety_signals.source_ids IS 'Array of MongoDB analyzed_posts._id references';
COMMENT ON COLUMN safety_signals.langsmith_trace_id IS 'LangSmith trace ID for explainability';
COMMENT ON COLUMN safety_signals.ai_summary IS 'AI-generated concise summary of the signal';
COMMENT ON COLUMN safety_signals.recommended_action IS 'AI-recommended action: monitor, investigate, escalate, archive';
COMMENT ON COLUMN safety_signals.patient_impact_score IS 'Calculated impact on patient quality of life (0.0-1.0)';
COMMENT ON COLUMN safety_signals.tags IS 'Array of tags for categorization and filtering';

-- ============================================================================
-- REPORTS
-- ============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID REFERENCES safety_signals(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    generated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    report_type VARCHAR(100) NOT NULL, -- patient_impact, trend_analysis, safety_alert
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    full_report JSONB, -- Structured report data
    
    -- Distribution tracking
    shared_via VARCHAR(100)[], -- whatsapp, email, slack, crm
    recipients TEXT[],
    shared_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_signal ON reports(signal_id);
CREATE INDEX idx_reports_project ON reports(project_id);
CREATE INDEX idx_reports_generated_by ON reports(generated_by);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX idx_reports_type ON reports(report_type);

COMMENT ON TABLE reports IS 'Generated patient impact reports and safety alerts';
COMMENT ON COLUMN reports.full_report IS 'Structured JSON report with charts, data, and recommendations';

-- ============================================================================
-- FILTERED POSTS TRACKING
-- ============================================================================

CREATE TABLE filtered_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    search_execution_id UUID REFERENCES search_executions(id) ON DELETE CASCADE,
    
    -- MongoDB reference
    mongodb_post_id TEXT NOT NULL, -- MongoDB raw_posts._id or analyzed_posts._id
    
    -- Filter details
    filter_reason VARCHAR(255) NOT NULL, -- not_relevant, noise, spam, wrong_language, low_confidence
    relevance_score DECIMAL(3,2), -- 0.0 to 1.0
    is_noise BOOLEAN DEFAULT false,
    is_spam BOOLEAN DEFAULT false,
    
    -- What was detected
    matched_keywords TEXT[], -- Keywords that were checked
    language_detected VARCHAR(10),
    
    -- AI decision
    ai_explanation TEXT, -- Why it was filtered
    confidence DECIMAL(3,2), -- Confidence in filtering decision
    
    -- Timestamps
    filtered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filtered_project ON filtered_posts(project_id);
CREATE INDEX idx_filtered_search ON filtered_posts(search_execution_id);
CREATE INDEX idx_filtered_reason ON filtered_posts(filter_reason);
CREATE INDEX idx_filtered_at ON filtered_posts(filtered_at DESC);

COMMENT ON TABLE filtered_posts IS 'Track posts that were filtered out for analytics and model improvement';
COMMENT ON COLUMN filtered_posts.filter_reason IS 'Reason for filtering: not_relevant, noise, spam, wrong_language, low_confidence';

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL, -- login, create_project, share_report, etc.
    resource_type VARCHAR(100), -- project, signal, report
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at DESC);

COMMENT ON TABLE audit_logs IS 'System audit trail for compliance and security';

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON data_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_safety_signals_updated_at BEFORE UPDATE ON safety_signals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active projects with signal counts
CREATE VIEW v_project_dashboard AS
SELECT 
    p.id,
    p.name,
    p.status,
    p.created_at,
    COUNT(DISTINCT k.id) as keyword_count,
    COUNT(DISTINCT ds.id) as source_count,
    COUNT(DISTINCT se.id) as total_searches,
    COUNT(DISTINCT CASE WHEN se.status = 'completed' THEN se.id END) as successful_searches,
    COUNT(DISTINCT ss.id) as signal_count,
    COUNT(DISTINCT CASE WHEN ss.severity IN ('critical', 'high') THEN ss.id END) as high_priority_signals
FROM projects p
LEFT JOIN keywords k ON p.id = k.project_id
LEFT JOIN data_sources ds ON p.id = ds.project_id
LEFT JOIN search_executions se ON p.id = se.project_id
LEFT JOIN safety_signals ss ON p.id = ss.project_id
WHERE p.status = 'active'
GROUP BY p.id, p.name, p.status, p.created_at;

COMMENT ON VIEW v_project_dashboard IS 'Dashboard view of active projects with aggregated metrics';

-- Recent high-priority signals
CREATE VIEW v_recent_critical_signals AS
SELECT 
    ss.id,
    ss.signal_type,
    ss.severity,
    ss.drug_name,
    ss.symptom,
    ss.virality_score,
    ss.confidence_score,
    ss.status,
    ss.first_detected_at,
    p.name as project_name,
    u.full_name as assigned_to_name
FROM safety_signals ss
JOIN projects p ON ss.project_id = p.id
LEFT JOIN users u ON ss.assigned_to = u.id
WHERE ss.severity IN ('critical', 'high')
  AND ss.status NOT IN ('resolved', 'false_positive')
ORDER BY ss.first_detected_at DESC;

COMMENT ON VIEW v_recent_critical_signals IS 'Recent critical and high-severity signals requiring attention';

-- ============================================================================
-- SEED DATA (Optional - for development)
-- ============================================================================

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION!)
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@sentinelhealth.com', crypt('admin123', gen_salt('bf')), 'System Administrator', 'admin');

-- ============================================================================
-- GRANTS (Adjust based on your user setup)
-- ============================================================================

-- Grant permissions to application user (create this user separately)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sentinel_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sentinel_app;

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

CREATE TABLE schema_version (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
('1.0.0', 'Initial schema with users, projects, keywords, sources, search_executions, signals, reports, and audit logs');

COMMENT ON TABLE schema_version IS 'Track database schema versions for migrations';
