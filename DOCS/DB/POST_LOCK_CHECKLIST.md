# Post-Schema Lock Checklist

## ✅ Schema Lock Complete

**Date**: May 6, 2026  
**Version**: 1.1.0  
**Status**: LOCKED

---

## Immediate Next Steps

### 1. Apply Initial Schema

#### PostgreSQL
```bash
cd DOCS/DB/POSTGRES
psql -U postgres -c "CREATE DATABASE sentinel_health;"
psql -U postgres -d sentinel_health -f schema.sql
```

**Verify**:
```bash
psql -U postgres -d sentinel_health -c "\dt"
# Should show 9 tables
```

#### MongoDB
```bash
cd DOCS/DB/MONGODB
mongosh < schema.js
```

**Verify**:
```bash
mongosh sentinel_health --eval "db.getCollectionNames()"
# Should show 5 collections (including schema_version)
```

---

### 2. Test Database Connections

```bash
cd Backend
uvicorn app.main:app --reload
```

**Test endpoints**:
```bash
curl http://localhost:8000/api/v1/health/postgres
curl http://localhost:8000/api/v1/health/mongodb
curl http://localhost:8000/api/v1/health/databases
```

All should return `"status": "healthy"`.

---

### 3. Create SQLAlchemy Models

Create `Backend/app/models/` directory with models matching schema:

- [ ] `user.py` - User model
- [ ] `project.py` - Project model
- [ ] `keyword.py` - Keyword model
- [ ] `data_source.py` - DataSource model
- [ ] `search_execution.py` - SearchExecution model
- [ ] `safety_signal.py` - SafetySignal model
- [ ] `filtered_post.py` - FilteredPost model
- [ ] `report.py` - Report model
- [ ] `audit_log.py` - AuditLog model

---

### 4. Create Pydantic Schemas

Create `Backend/app/schemas/` directory with request/response schemas:

- [ ] `user.py` - UserCreate, UserResponse, UserUpdate
- [ ] `project.py` - ProjectCreate, ProjectResponse, ProjectUpdate
- [ ] `keyword.py` - KeywordCreate, KeywordResponse
- [ ] `data_source.py` - DataSourceCreate, DataSourceResponse
- [ ] `safety_signal.py` - SafetySignalResponse
- [ ] `report.py` - ReportCreate, ReportResponse

---

### 5. Setup Alembic Initial Migration

```bash
cd Backend

# Initialize alembic (already done)
# alembic init alembic

# Create initial migration
alembic revision -m "initial_schema"

# Edit the migration file to match schema.sql
# Or use autogenerate after creating models:
alembic revision --autogenerate -m "initial_schema"

# Apply migration
alembic upgrade head
```

---

### 6. Create CRUD Operations

Create `Backend/app/crud/` directory:

- [ ] `user.py` - User CRUD operations
- [ ] `project.py` - Project CRUD operations
- [ ] `keyword.py` - Keyword CRUD operations
- [ ] `data_source.py` - DataSource CRUD operations
- [ ] `safety_signal.py` - SafetySignal CRUD operations

---

### 7. Create API Endpoints

Create `Backend/app/api/` routes:

- [ ] `users.py` - User management endpoints
- [ ] `projects.py` - Project management endpoints
- [ ] `keywords.py` - Keyword management endpoints
- [ ] `data_sources.py` - Data source management endpoints
- [ ] `search.py` - Search execution endpoints
- [ ] `signals.py` - Safety signal endpoints
- [ ] `reports.py` - Report generation endpoints

---

### 8. Implement Authentication

- [ ] JWT token generation
- [ ] Login endpoint
- [ ] Register endpoint
- [ ] Password hashing (bcrypt)
- [ ] Role-based access control
- [ ] Protected route decorator

---

### 9. MongoDB Integration

Create `Backend/app/services/mongodb/`:

- [ ] `raw_pages.py` - Raw page operations
- [ ] `raw_posts.py` - Raw post operations
- [ ] `analyzed_posts.py` - Analyzed post operations
- [ ] `agent_traces.py` - Agent trace operations

---

### 10. Implement Agent Pipeline

Create `Backend/app/agents/`:

- [ ] `relevance_filter.py` - Relevance filtering agent
- [ ] `anonymizer.py` - PII/PHI anonymization agent
- [ ] `entity_extractor.py` - Medical entity extraction agent
- [ ] `sentiment_analyzer.py` - Sentiment analysis agent
- [ ] `trend_analyzer.py` - Trend & virality agent
- [ ] `safety_auditor.py` - Safety audit agent
- [ ] `interpreter.py` - AI interpretation agent
- [ ] `pipeline.py` - LangGraph pipeline orchestration

---

### 11. Setup LangSmith Integration

- [ ] Configure LangSmith API key
- [ ] Implement tracing decorator
- [ ] Store trace IDs in database
- [ ] Create trace retrieval endpoint

---

### 12. Implement Data Retention

- [ ] MongoDB TTL index verification
- [ ] Archival job (MongoDB → PostgreSQL)
- [ ] Cleanup job for expired data
- [ ] Retention policy configuration

---

### 13. Setup Redis Caching

- [ ] Redis connection setup
- [ ] Cache decorator
- [ ] LLM response caching
- [ ] Cache invalidation strategy

---

### 14. Implement Report Generation

- [ ] Patient impact report template
- [ ] Report generation service
- [ ] PDF generation (optional)
- [ ] Email/WhatsApp integration

---

### 15. Create Admin Dashboard Endpoints

- [ ] Project statistics
- [ ] Signal dashboard data
- [ ] Filtering analytics
- [ ] Agent performance metrics
- [ ] Cost tracking

---

### 16. Testing

- [ ] Unit tests for CRUD operations
- [ ] Integration tests for API endpoints
- [ ] Agent pipeline tests
- [ ] Database migration tests
- [ ] Load testing

---

### 17. Documentation

- [ ] API documentation (Swagger/ReDoc)
- [ ] Agent pipeline documentation
- [ ] Deployment guide
- [ ] User guide
- [ ] Developer guide

---

### 18. Deployment Preparation

- [ ] Docker configuration
- [ ] Docker Compose setup
- [ ] Environment variable documentation
- [ ] CI/CD pipeline
- [ ] Monitoring setup
- [ ] Backup automation

---

## Migration Workflow (For Future Changes)

### PostgreSQL Changes

1. Create migration:
   ```bash
   alembic revision -m "description"
   ```

2. Edit migration file

3. Test locally:
   ```bash
   alembic upgrade head
   ```

4. Commit to git

5. Apply to staging/production:
   ```bash
   alembic upgrade head
   ```

### MongoDB Changes

1. Create migration script:
   ```javascript
   // Backend/migrations/mongodb/XXX_description.js
   ```

2. Test locally:
   ```bash
   mongosh sentinel_health < migration.js
   ```

3. Commit to git

4. Apply to staging/production:
   ```bash
   mongosh sentinel_health < migration.js
   ```

---

## Monitoring Setup

### Database Monitoring

- [ ] PostgreSQL slow query log
- [ ] MongoDB profiling
- [ ] Connection pool monitoring
- [ ] Disk space alerts
- [ ] Query performance tracking

### Application Monitoring

- [ ] API response times
- [ ] Error rates
- [ ] Agent execution times
- [ ] LLM token usage
- [ ] Cache hit rates

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable PostgreSQL SSL
- [ ] Enable MongoDB authentication
- [ ] Implement rate limiting
- [ ] Add CORS configuration
- [ ] Implement API key authentication
- [ ] Add input validation
- [ ] Implement SQL injection prevention
- [ ] Add XSS protection
- [ ] Implement CSRF protection

---

## Performance Optimization

- [ ] Database connection pooling
- [ ] Query optimization
- [ ] Index optimization
- [ ] Caching strategy
- [ ] Async operations
- [ ] Batch processing
- [ ] Load balancing

---

## Compliance

- [ ] HIPAA compliance review
- [ ] Data retention policy implementation
- [ ] Audit logging verification
- [ ] Access control testing
- [ ] PII/PHI anonymization testing
- [ ] Backup and recovery testing

---

## Production Readiness

- [ ] All tests passing
- [ ] Documentation complete
- [ ] Security audit complete
- [ ] Performance testing complete
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Team trained

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Database Setup | Apply schemas, test connections | 1 day |
| Models & Schemas | SQLAlchemy + Pydantic | 2-3 days |
| CRUD & API | Basic endpoints | 3-5 days |
| Authentication | JWT, RBAC | 2 days |
| Agent Pipeline | 7 agents + LangGraph | 5-7 days |
| Integration | LangSmith, Redis, etc. | 3-4 days |
| Testing | Unit + Integration | 3-5 days |
| Documentation | API + User docs | 2-3 days |
| Deployment | Docker + CI/CD | 2-3 days |

**Total**: 23-35 days (3-5 weeks)

---

## Resources

### Documentation
- `/DOCS/DB/` - All database documentation
- `/Backend/README.md` - Backend setup guide
- `/Backend/TROUBLESHOOTING.md` - Common issues

### Tools
- Alembic - PostgreSQL migrations
- SQLAlchemy - ORM
- Pydantic - Data validation
- FastAPI - Web framework
- LangGraph - Agent orchestration
- LangSmith - Tracing

---

**Status**: Ready to proceed with implementation  
**Next**: Create SQLAlchemy models  
**Priority**: High  
**Deadline**: TBD
