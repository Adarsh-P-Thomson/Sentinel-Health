-- Migration 001: Fix source_id column type in search_executions
-- Date: 2026-05-07
-- Description: Change source_id from UUID to VARCHAR(100) to store source identifiers like 'reddit', 'twitter'

-- Drop the foreign key constraint first
ALTER TABLE search_executions 
DROP CONSTRAINT IF EXISTS search_executions_source_id_fkey;

-- Change the column type
ALTER TABLE search_executions 
ALTER COLUMN source_id TYPE VARCHAR(100);

-- Drop the index on source_id if it exists
DROP INDEX IF EXISTS idx_search_source;

-- Recreate the index
CREATE INDEX idx_search_source ON search_executions(source_id);

-- Update schema version
INSERT INTO schema_version (version, description) VALUES
('1.0.1', 'Fix source_id type in search_executions from UUID to VARCHAR(100)');
