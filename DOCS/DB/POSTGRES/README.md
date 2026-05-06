# PostgreSQL Setup - Sentinel Health

## Overview

PostgreSQL stores structured, relational data requiring ACID compliance including user management, project configuration, and high-value safety signals.

## Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `users` | Authentication & authorization | Role-based access control |
| `projects` | Monitoring project configuration | Soft delete support |
| `keywords` | Keywords to monitor | Categorized by type |
| `data_sources` | Social media source configuration | JSONB config storage |
| `safety_signals` | High-value archived signals | Time-series optimized |
| `reports` | Generated patient impact reports | Distribution tracking |
| `audit_logs` | Compliance audit trail | IP tracking |

## Prerequisites

- PostgreSQL 14+
- psql command-line tool

## Installation

### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Windows
Download and install from: https://www.postgresql.org/download/windows/

## Quick Setup

### 1. Create Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE sentinel_health;

# Create application user
CREATE USER sentinel_app WITH PASSWORD 'CHANGE_THIS_PASSWORD';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sentinel_health TO sentinel_app;

# Exit
\q
```

### 2. Apply Schema
```bash
# Navigate to schema directory
cd DOCS/DB/POSTGRES

# Apply schema
psql -U postgres -d sentinel_health -f schema.sql
```

You should see:
```
CREATE EXTENSION
CREATE TABLE
CREATE INDEX
...
INSERT 0 1
```

### 3. Verify Setup
```bash
psql -U postgres -d sentinel_health -c "\dt"
```

Expected output:
```
              List of relations
 Schema |      Name       | Type  |  Owner   
--------+-----------------+-------+----------
 public | audit_logs      | table | postgres
 public | data_sources    | table | postgres
 public | keywords        | table | postgres
 public | projects        | table | postgres
 public | reports         | table | postgres
 public | safety_signals  | table | postgres
 public | schema_version  | table | postgres
 public | users           | table | postgres
```

## Configuration

### Connection String

**Development**:
```
postgresql://postgres:password@localhost:5432/sentinel_health
```

**Production**:
```
postgresql://sentinel_app:password@host:5432/sentinel_health?sslmode=require
```

### Environment Variables

Add to your `.env` file:
```env
POSTGRES_URL=postgresql://postgres:password@localhost:5432/sentinel_health
POSTGRES_DB=sentinel_health
POSTGRES_USER=sentinel_app
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Schema Features

### UUID Primary Keys
All tables use UUID primary keys for security and distributed systems compatibility.

### Automatic Timestamps
`updated_at` columns are automatically updated via triggers.

### Foreign Key Constraints
Referential integrity enforced with cascading deletes where appropriate.

### JSONB Columns
- `data_sources.config`: Source-specific configuration
- `reports.full_report`: Structured report data
- `audit_logs.details`: Flexible audit metadata

### Indexes
Optimized indexes for:
- Time-series queries (`created_at DESC`)
- Foreign key lookups
- Status filtering
- Full-text search ready

## Views

### Project Dashboard
```sql
SELECT * FROM v_project_dashboard;
```

Shows active projects with aggregated metrics:
- Keyword count
- Source count
- Total signals
- High-priority signals

### Recent Critical Signals
```sql
SELECT * FROM v_recent_critical_signals;
```

Shows unresolved critical/high-severity signals.

## Common Operations

### Create a Project
```sql
INSERT INTO projects (name, description, created_by)
VALUES (
  'Drug-Y Monitoring',
  'Monitor adverse events for Drug-Y',
  (SELECT id FROM users WHERE email = 'admin@sentinelhealth.com')
);
```

### Add Keywords
```sql
INSERT INTO keywords (project_id, keyword, category, priority)
VALUES 
  ('project-uuid', 'Drug-Y', 'drug', 'high'),
  ('project-uuid', 'headache', 'symptom', 'medium'),
  ('project-uuid', 'nausea', 'symptom', 'medium');
```

### Configure Data Source
```sql
INSERT INTO data_sources (project_id, source_type, source_name, monitoring_interval, config)
VALUES (
  'project-uuid',
  'reddit',
  'r/pharmacy',
  'daily',
  '{"subreddit": "pharmacy", "sort": "new", "limit": 100}'::jsonb
);
```

### Query High-Priority Signals
```sql
SELECT 
  drug_name,
  symptom,
  severity,
  virality_score,
  first_detected_at
FROM safety_signals
WHERE severity IN ('critical', 'high')
  AND status = 'new'
ORDER BY virality_score DESC, first_detected_at DESC
LIMIT 20;
```

### Generate Report
```sql
INSERT INTO reports (signal_id, project_id, generated_by, report_type, title, summary)
VALUES (
  'signal-uuid',
  'project-uuid',
  'user-uuid',
  'patient_impact',
  'Drug-Y Adverse Event Report',
  'Emerging pattern of severe headaches reported by Drug-Y users'
);
```

## Backup & Restore

### Backup
```bash
# Full database backup
pg_dump -U postgres sentinel_health > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U postgres sentinel_health | gzip > backup_$(date +%Y%m%d).sql.gz

# Schema only
pg_dump -U postgres --schema-only sentinel_health > schema_backup.sql
```

### Restore
```bash
# Restore from backup
psql -U postgres -d sentinel_health < backup_20260506.sql

# Restore compressed backup
gunzip -c backup_20260506.sql.gz | psql -U postgres -d sentinel_health
```

## Performance Optimization

### Analyze Tables
```sql
ANALYZE users;
ANALYZE projects;
ANALYZE safety_signals;
```

### Vacuum
```sql
VACUUM ANALYZE;
```

### Check Index Usage
```sql
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Slow Query Log
Edit `postgresql.conf`:
```
log_min_duration_statement = 1000  # Log queries slower than 1s
```

## Monitoring

### Database Size
```sql
SELECT pg_size_pretty(pg_database_size('sentinel_health'));
```

### Table Sizes
```sql
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Active Connections
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'sentinel_health';
```

### Lock Monitoring
```sql
SELECT * FROM pg_locks WHERE NOT granted;
```

## Security

### Change Default Password
```sql
ALTER USER sentinel_app WITH PASSWORD 'new_secure_password';
```

### Row-Level Security (Optional)
```sql
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY project_access ON projects
  FOR ALL
  TO sentinel_app
  USING (created_by = current_user_id());
```

### SSL Connection
Edit `postgresql.conf`:
```
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

## Migrations

### Check Current Version
```sql
SELECT * FROM schema_version ORDER BY applied_at DESC;
```

### Apply Migration
```sql
-- Example migration: Add new column
ALTER TABLE safety_signals ADD COLUMN impact_score DECIMAL(3,2);

-- Record migration
INSERT INTO schema_version (version, description)
VALUES ('1.1.0', 'Added impact_score to safety_signals');
```

## Troubleshooting

### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### Permission Denied
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sentinel_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sentinel_app;
```

### Reset Admin Password
```bash
psql -U postgres -d sentinel_health -c "UPDATE users SET password_hash = crypt('newpassword', gen_salt('bf')) WHERE email = 'admin@sentinelhealth.com';"
```

## Default Credentials

**⚠️ CHANGE IN PRODUCTION!**

- **Email**: `admin@sentinelhealth.com`
- **Password**: `admin123`

## Next Steps

1. ✅ PostgreSQL schema applied
2. 🔧 Configure connection in FastAPI backend
3. 🔧 Set up SQLAlchemy ORM
4. 🔧 Implement authentication middleware

---

**Last Updated**: May 6, 2026
