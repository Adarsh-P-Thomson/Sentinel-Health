# 🔒 Database Schema - LOCKED FOR PRODUCTION

**Status**: ✅ **LOCKED**  
**Version**: 1.1.0  
**Date**: May 6, 2026  
**Approved By**: Development Team

---

## Schema Lock Notice

⚠️ **This schema is now locked for production use.**

All future changes MUST be done through migrations:
- **PostgreSQL**: Use Alembic migrations (`Backend/alembic/`)
- **MongoDB**: Use migration scripts (`Backend/migrations/mongodb/`)

See: `/DOCS/DB/MIGRATION_GUIDE.md` for instructions.

---

## Schema Summary

### PostgreSQL (9 Tables)

| # | Table | Purpose | Rows (Est.) |
|---|-------|---------|-------------|
| 1 | `users` | Authentication & authorization | 10-100 |
| 2 | `projects` | Monitoring projects | 10-50 |
| 3 | `keywords` | Keywords to monitor | 100-1000 |
| 4 | `data_sources` | Social media sources | 50-200 |
| 5 | `search_executions` | Search tracking | 1000-10000 |
| 6 | `safety_signals` | High-value archived signals | 1000-100000 |
| 7 | `filtered_posts` | Filtered/rejected posts | 10000-1000000 |
| 8 | `reports` | Generated reports | 100-10000 |
| 9 | `audit_logs` | Compliance audit trail | 10000-1000000 |

**Total Estimated Size**: 10-100 GB (depending on usage)

### MongoDB (4 Collections)

| # | Collection | Purpose | Documents (Est.) | TTL |
|---|------------|---------|------------------|-----|
| 1 | `raw_pages` | Raw HTML/page data | 100K-1M | 30 days (low_value) |
| 2 | `raw_posts` | Extracted posts | 1M-10M | 30 days (low_value) |
| 3 | `analyzed_posts` | AI-processed posts | 1M-10M | Permanent (high_value) |
| 4 | `agent_traces` | Execution traces | 10M-100M | 90 days |

**Total Estimated Size**: 100-500 GB (with TTL cleanup)

---

## Key Features

### ✅ Comprehensive AI Analysis
- 7 specialized agents (Anonymizer, Extractor, Sentiment, Trend, Auditor, Interpreter, Filter)
- Per-agent confidence scores
- Full execution metadata

### ✅ Cross-Database References
- PostgreSQL ↔ MongoDB bidirectional tracking
- UUID and ObjectId cross-references
- Full data lineage from page → post → analysis → signal

### ✅ Data Retention & Cost Optimization
- TTL indexes for automatic cleanup
- Tiered storage (low_value → high_value)
- 30-day purge for noise
- 90-day trace retention
- Permanent archival for high-value signals

### ✅ Explainability & Traceability
- LangSmith integration
- Agent execution traces
- Confidence scores at every level
- Full audit trail

### ✅ Filtering & Noise Reduction
- Relevance filtering before expensive AI processing
- `filtered_posts` table for analytics
- Noise and spam detection

### ✅ Actionable Insights
- AI-generated summaries and recommendations
- Recommended actions (monitor, investigate, escalate, archive)
- Clinical significance explanations
- Patient impact scoring

### ✅ Performance Optimized
- Proper indexes on all query patterns
- GIN indexes for array fields
- Connection pooling
- Compound indexes for common queries

---

## Schema Files

### Source Files (DO NOT MODIFY DIRECTLY)
- `DOCS/DB/POSTGRES/schema.sql` - PostgreSQL schema
- `DOCS/DB/MONGODB/schema.js` - MongoDB schema

### Documentation
- `DOCS/DB/DATABASE_ARCHITECTURE.md` - Complete architecture
- `DOCS/DB/CROSS_REFERENCE_GUIDE.md` - Cross-database queries
- `DOCS/DB/AI_ANALYSIS_FIELDS.md` - AI field documentation
- `DOCS/DB/SCHEMA_SUMMARY.md` - Quick reference
- `DOCS/DB/SCHEMA_CHANGELOG.md` - Version history
- `DOCS/DB/FINAL_SCHEMA_REVIEW.md` - Pre-lock review

### Migration Setup
- `Backend/alembic/` - PostgreSQL migrations
- `Backend/alembic.ini` - Alembic configuration
- `DOCS/DB/MIGRATION_GUIDE.md` - Migration instructions

---

## Applying Initial Schema

### PostgreSQL

```bash
# Create database
psql -U postgres -c "CREATE DATABASE sentinel_health;"

# Apply schema
psql -U postgres -d sentinel_health -f DOCS/DB/POSTGRES/schema.sql

# Verify
psql -U postgres -d sentinel_health -c "\dt"
```

### MongoDB

```bash
# Apply schema
mongosh < DOCS/DB/MONGODB/schema.js

# Verify
mongosh sentinel_health --eval "db.getCollectionNames()"
```

---

## Making Changes (Post-Lock)

### ❌ DO NOT:
- Directly modify `schema.sql` or `schema.js`
- Manually alter tables/collections in production
- Skip migrations

### ✅ DO:
- Create Alembic migration for PostgreSQL changes
- Create migration script for MongoDB changes
- Test migrations on development first
- Document changes in migration files
- Update schema documentation after migration

### Example: Adding a Field

**PostgreSQL**:
```bash
cd Backend
alembic revision -m "add_phone_to_users"
# Edit migration file
alembic upgrade head
```

**MongoDB**:
```javascript
// Backend/migrations/mongodb/002_add_field.js
db.analyzed_posts.updateMany(
  { new_field: { $exists: false } },
  { $set: { new_field: default_value } }
);
```

---

## Version History

### v1.1.0 (May 6, 2026) - Current
- Enhanced AI analysis fields
- Added AI interpretation agent
- Added relevance filtering
- Added `filtered_posts` table
- Enhanced all agent outputs
- Added tags and categories
- Added review and validation workflow

### v1.0.0 (May 6, 2026) - Initial
- Initial schema design
- Basic tables and collections
- Cross-database references
- TTL indexes

---

## Schema Statistics

### PostgreSQL Indexes: 50+
- Primary key indexes: 9
- Foreign key indexes: 15
- Query optimization indexes: 20+
- GIN indexes for arrays: 6

### MongoDB Indexes: 30+
- Unique indexes: 3
- Compound indexes: 10
- TTL indexes: 3
- Text indexes: 2
- Single field indexes: 15+

---

## Backup Strategy

### PostgreSQL
```bash
# Daily backup
pg_dump sentinel_health > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump sentinel_health | gzip > backup_$(date +%Y%m%d).sql.gz
```

### MongoDB
```bash
# Daily backup
mongodump --db sentinel_health --out /backup/$(date +%Y%m%d)

# Compressed backup
mongodump --db sentinel_health --archive --gzip > backup_$(date +%Y%m%d).gz
```

---

## Performance Benchmarks (Expected)

### PostgreSQL
- Simple SELECT: <10ms
- Complex JOIN: <50ms
- Aggregation query: <100ms
- Insert: <5ms

### MongoDB
- Find by ID: <5ms
- Find with filter: <20ms
- Aggregation: <100ms
- Insert: <2ms

---

## Monitoring

### Key Metrics to Track
- Database size growth
- Query performance
- Index usage
- TTL cleanup effectiveness
- Connection pool utilization
- Cache hit rates

### Alerts
- Database size > 80% capacity
- Slow queries > 1s
- Failed migrations
- TTL cleanup failures
- Connection pool exhaustion

---

## Support

### Issues with Schema
1. Check documentation in `/DOCS/DB/`
2. Review migration guide
3. Check troubleshooting guide
4. Contact development team

### Requesting Schema Changes
1. Document the requirement
2. Explain why existing schema doesn't work
3. Propose migration strategy
4. Get approval from team lead
5. Create migration
6. Test thoroughly
7. Apply to production

---

## Compliance

### HIPAA Compliance
- ✅ PII/PHI anonymization in `analyzed_posts`
- ✅ Audit logging in `audit_logs`
- ✅ Access control via `users.role`
- ✅ Data retention policies

### Data Retention
- ✅ 30-day TTL for low-value data
- ✅ 90-day TTL for traces
- ✅ Permanent storage for high-value signals
- ✅ Configurable retention policies

---

## Next Steps

1. ✅ Schema locked
2. 🔧 Create SQLAlchemy models
3. 🔧 Create Pydantic schemas
4. 🔧 Implement CRUD operations
5. 🔧 Build API endpoints
6. 🔧 Implement agent pipeline
7. 🔧 Add authentication
8. 🔧 Deploy to production

---

**🔒 Schema Lock Date**: May 6, 2026  
**📝 Last Updated**: May 6, 2026  
**✅ Status**: Production Ready  
**🚀 Next**: Implement application layer
