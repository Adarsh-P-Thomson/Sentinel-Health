-- Seed test data for development

-- Insert test project
INSERT INTO projects (id, name, description, status) VALUES
('00000000-0000-0000-0000-000000000001', 'Test Hospital Monitoring', 'Test project for monitoring hospital-related safety signals', 'active')
ON CONFLICT (id) DO NOTHING;

-- Insert test keywords
INSERT INTO keywords (project_id, keyword, category, priority) VALUES
('00000000-0000-0000-0000-000000000001', 'Drug-Y', 'drug', 'high'),
('00000000-0000-0000-0000-000000000001', 'headache', 'symptom', 'medium'),
('00000000-0000-0000-0000-000000000001', 'nausea', 'symptom', 'medium')
ON CONFLICT DO NOTHING;

SELECT 'Test data seeded successfully' as status;
