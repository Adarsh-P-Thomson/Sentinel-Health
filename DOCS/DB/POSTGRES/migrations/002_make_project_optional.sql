-- Migration 002: Make project_id optional in search_executions
-- Date: 2026-05-07
-- Description: Allow searches without requiring a project (public/ad-hoc searches)

-- Make project_id nullable
ALTER TABLE search_executions 
ALTER COLUMN project_id DROP NOT NULL;

-- Update schema version
INSERT INTO schema_version (version, description) VALUES
('1.0.2', 'Make project_id optional in search_executions for public searches');
