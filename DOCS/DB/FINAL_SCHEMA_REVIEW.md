# Final Schema Review - Pre-Migration Lock

## ✅ Requirements Coverage Checklist

### Module A: The Configurator (Input)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Projects management | `projects` table | - | ✅ |
| Target keywords configuration | `keywords` table | - | ✅ |
| Time interval selection | `data_sources.monitoring_interval` | - | ✅ |
| Data source selection | `data_sources` table | - | ✅ |
| Source-specific config | `data_sources.config` (JSONB) | - | ✅ |
| User/Admin management | `users` table | - | ✅ |

### Module B: MCP Servers (Scout)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Track search executions | `search_executions` table | - | ✅ |
| Store raw page data | - | `raw_pages` | ✅ |
| Store HTML content | - | `raw_pages.html_content` | ✅ |
| Store links found | - | `raw_pages.links[]` | ✅ |
| Store media found | - | `raw_pages.media[]` | ✅ |
| URL deduplication | - | `raw_pages.url_hash` (unique) | ✅ |
| HTTP metadata | - | `raw_pages.http_status`, `headers` | ✅ |
| Cross-reference tracking | `search_executions.mongodb_page_ids[]` | `raw_pages.search_execution_id` | ✅ |

### Module C: LangGraph Multi-Agent Brain

#### Anonymizer Agent

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Anonymized content | - | `analyzed_posts.anonymized_content` | ✅ |
| PII detection flag | - | `analyzed_posts.pii_detected` | ✅ |
| PII types identified | - | `analyzed_posts.pii_types[]` | ✅ |
| Redaction mapping | - | `analyzed_posts.pii_redaction_map` | ✅ |
| Confidence score | - | `analyzed_posts.anonymizer_confidence` | ✅ |
| Agent execution metadata | - | `analyzed_posts.agent_pipeline.anonymizer` | ✅ |

#### Medical Entity Extractor

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Drug extraction | - | `analyzed_posts.entities.drugs[]` | ✅ |
| Drug name, dosage, frequency | - | `drugs[].name`, `dosage`, `frequency` | ✅ |
| Generic/brand names | - | `drugs[].generic_name`, `brand_name` | ✅ |
| Symptom extraction | - | `analyzed_posts.entities.symptoms[]` | ✅ |
| Symptom severity | - | `symptoms[].severity` | ✅ |
| Symptom onset/duration | - | `symptoms[].onset`, `duration` | ✅ |
| Condition extraction | - | `analyzed_posts.entities.conditions[]` | ✅ |
| ICD codes | - | `conditions[].icd_code` | ✅ |
| Procedure extraction | - | `analyzed_posts.entities.procedures[]` | ✅ |
| Context for each entity | - | All entities have `.context` | ✅ |
| Confidence scores | - | All entities have `.confidence` | ✅ |
| Agent execution metadata | - | `agent_pipeline.extractor` | ✅ |

#### Sentiment Analyst

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Overall sentiment | - | `analyzed_posts.sentiment.overall` | ✅ |
| Sentiment score (-1 to 1) | - | `sentiment.score` | ✅ |
| Emotion detection | - | `sentiment.emotions[]` | ✅ |
| Individual emotion scores | - | `sentiment.emotion_scores{}` | ✅ |
| Sentiment context | - | `sentiment.context` | ✅ |
| Patient vs. general | - | `sentiment.is_patient_experience` | ✅ |
| Confidence score | - | `sentiment.confidence` | ✅ |
| Agent execution metadata | - | `agent_pipeline.sentiment` | ✅ |

#### Trend & Virality Agent

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Virality score | - | `analyzed_posts.virality.score` | ✅ |
| Trend classification | - | `virality.trend` | ✅ |
| Engagement metrics | - | `virality.engagement_rate` | ✅ |
| Viral potential | - | `virality.viral_potential` | ✅ |
| Engagement velocity | - | `virality.velocity` | ✅ |
| Similar posts count | - | `virality.similar_posts_count` | ✅ |
| Trending flag | - | `virality.is_trending` | ✅ |
| Agent execution metadata | - | `agent_pipeline.trend` | ✅ |

#### Safety Auditor

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Adverse event detection | - | `analyzed_posts.safety_audit.is_adverse_event` | ✅ |
| Severity assessment | - | `safety_audit.severity` | ✅ |
| Known side effect check | - | `safety_audit.known_side_effect` | ✅ |
| Investigation flag | - | `safety_audit.requires_investigation` | ✅ |
| Risk categorization | - | `safety_audit.risk_category` | ✅ |
| Medical DB verification | - | `safety_audit.medical_database_match` | ✅ |
| FDA label check | - | `safety_audit.fda_label_check` | ✅ |
| Similar reports count | - | `safety_audit.similar_reports_count` | ✅ |
| Confidence score | - | `safety_audit.confidence` | ✅ |
| Agent execution metadata | - | `agent_pipeline.auditor` | ✅ |

#### AI Interpreter (NEW)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Human-readable summary | - | `analyzed_posts.ai_interpretation.summary` | ✅ |
| Key findings | - | `ai_interpretation.key_findings[]` | ✅ |
| Clinical significance | - | `ai_interpretation.clinical_significance` | ✅ |
| Recommended action | - | `ai_interpretation.recommended_action` | ✅ |
| Action rationale | - | `ai_interpretation.action_rationale` | ✅ |
| Suggested tags | - | `ai_interpretation.suggested_tags[]` | ✅ |
| Related signals | - | `ai_interpretation.related_signals[]` | ✅ |
| Overall confidence | - | `ai_interpretation.confidence_overall` | ✅ |
| Agent execution metadata | - | `agent_pipeline.interpreter` | ✅ |

#### Relevance Filter (NEW)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Relevance detection | - | `analyzed_posts.relevance.is_relevant` | ✅ |
| Relevance score | - | `relevance.relevance_score` | ✅ |
| Matched keywords | - | `relevance.matched_keywords[]` | ✅ |
| Filter reason | - | `relevance.filter_reason` | ✅ |
| Noise detection | - | `relevance.is_noise` | ✅ |
| Language matching | - | `relevance.language_match` | ✅ |
| Filtered posts tracking | `filtered_posts` table | - | ✅ |
| Agent execution metadata | - | `agent_pipeline.relevance_filter` | ✅ |

### Module D: User UI (Outcome)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| High-priority signals | `safety_signals` table | - | ✅ |
| Signal severity | `safety_signals.severity` | - | ✅ |
| Signal status tracking | `safety_signals.status` | - | ✅ |
| Assignment to users | `safety_signals.assigned_to` | - | ✅ |
| Timeline data | `safety_signals.first_detected_at`, `trending_period` | - | ✅ |
| Virality metrics | `safety_signals.virality_score` | - | ✅ |
| Aggregated mentions | `safety_signals.mention_count` | - | ✅ |
| Tags for filtering | `safety_signals.tags[]` | - | ✅ |
| Categories | `safety_signals.categories[]` | - | ✅ |

### Module E: Actionable Insights & Crisis Sharing

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Report generation | `reports` table | - | ✅ |
| Report types | `reports.report_type` | - | ✅ |
| Patient impact reports | `reports.full_report` (JSONB) | - | ✅ |
| Distribution tracking | `reports.shared_via[]`, `recipients[]` | - | ✅ |
| Share timestamp | `reports.shared_at` | - | ✅ |
| Signal escalation | `safety_signals.escalated_at`, `escalation_reason` | - | ✅ |
| Escalation flag | - | `analyzed_posts.should_escalate` | ✅ |

### Module F: LangSmith (Explainability)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Trace ID storage | `safety_signals.langsmith_trace_id` | `analyzed_posts.langsmith_trace_id` | ✅ |
| Run ID storage | - | `analyzed_posts.langsmith_run_id` | ✅ |
| Agent execution traces | - | `agent_traces` collection | ✅ |
| Per-agent metadata | - | `agent_traces.agent_name`, `model`, etc. | ✅ |
| Token usage tracking | - | `agent_traces.prompt_tokens`, `completion_tokens` | ✅ |
| Cost tracking | - | `agent_traces.total_cost` | ✅ |
| Duration tracking | - | `agent_traces.duration_ms` | ✅ |
| Cache tracking | - | `agent_traces.cache_hit`, `cache_key` | ✅ |

### Module G: Data Retention & Cost Optimization

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| High-value archival | `safety_signals` (permanent) | - | ✅ |
| Low-value TTL | - | `raw_pages.expires_at`, `raw_posts.expires_at` | ✅ |
| Retention policy flag | - | All collections have `retention_policy` | ✅ |
| 30-day auto-purge | - | TTL indexes on `expires_at` | ✅ |
| 90-day trace retention | - | TTL index on `agent_traces` | ✅ |
| Archive flag | - | `analyzed_posts.archived_to_postgres` | ✅ |
| Cross-reference | `safety_signals.source_ids[]` | `analyzed_posts.postgres_signal_id` | ✅ |

### Core Requirements: Part 1 (Generic Engine)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Project configuration | `projects` table | - | ✅ |
| Keyword configuration | `keywords` table | - | ✅ |
| Source configuration | `data_sources` table | - | ✅ |
| Monitoring intervals | `data_sources.monitoring_interval` | - | ✅ |
| Extensible source config | `data_sources.config` (JSONB) | - | ✅ |
| Search execution tracking | `search_executions` table | - | ✅ |
| Raw data storage | - | `raw_pages`, `raw_posts` | ✅ |

### Core Requirements: Part 2 (Analysis)

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| Entity extraction | - | `analyzed_posts.entities` | ✅ |
| Individual sentiment | - | `analyzed_posts.sentiment` | ✅ |
| Overall sentiment | `safety_signals.sentiment_score` | - | ✅ |
| Trending detection | - | `analyzed_posts.virality` | ✅ |
| Safety issue highlighting | `safety_signals` table | `analyzed_posts.safety_audit` | ✅ |
| Timeline view data | `safety_signals.first_detected_at`, `trending_period` | - | ✅ |
| Explainability | `safety_signals.langsmith_trace_id` | `agent_traces` | ✅ |
| Confidence scores | All tables/collections | All agents have confidence | ✅ |
| PII/PHI flagging | - | `analyzed_posts.pii_detected`, `pii_types[]` | ✅ |

### Additional Features

| Requirement | PostgreSQL | MongoDB | Status |
|-------------|-----------|---------|--------|
| User authentication | `users` table | - | ✅ |
| Role-based access | `users.role` | - | ✅ |
| Audit logging | `audit_logs` table | - | ✅ |
| Review & validation | `safety_signals.reviewed_by`, `is_validated` | - | ✅ |
| Patient impact scoring | `safety_signals.patient_impact_score` | - | ✅ |
| Quality of life impact | `safety_signals.quality_of_life_impact` | - | ✅ |

---

## 🔍 Missing or Questionable Items

### ⚠️ Items to Consider

1. **Multimodal Vision (Photos/Videos)**
   - **Current**: `raw_pages.media[]` and `raw_posts.media[]` store URLs
   - **Missing**: No fields for image/video analysis results
   - **Recommendation**: Add later via migration when implementing multimodal analysis

2. **Elasticsearch Integration**
   - **Current**: Not in schema
   - **Recommendation**: Add later if needed for advanced search

3. **CRM Integration Tracking**
   - **Current**: `reports.shared_via[]` includes "crm"
   - **Missing**: No specific CRM sync status tracking
   - **Recommendation**: Add `reports.crm_sync_status` if needed

4. **Rate Limiting / API Quota Tracking**
   - **Current**: Not in schema
   - **Recommendation**: Add `data_sources.api_quota_used`, `api_quota_limit` if needed

5. **Notification Preferences**
   - **Current**: Not in schema
   - **Recommendation**: Add `users.notification_preferences` (JSONB) if needed

---

## ✅ Schema Strengths

1. **Comprehensive AI Analysis**: All 7 agents fully represented
2. **Cross-Database References**: Bidirectional tracking between PostgreSQL and MongoDB
3. **Explainability**: Full LangSmith integration
4. **Data Retention**: TTL indexes and retention policies
5. **Filtering Analytics**: `filtered_posts` table for model improvement
6. **Extensibility**: JSONB fields for flexible configuration
7. **Audit Trail**: Complete audit logging
8. **Performance**: Proper indexes on all query patterns

---

## 📋 Pre-Migration Checklist

- [x] All agent outputs captured
- [x] Cross-database references defined
- [x] TTL indexes for auto-cleanup
- [x] Confidence scores at all levels
- [x] Explainability via LangSmith
- [x] User management and RBAC
- [x] Audit logging
- [x] Report generation and distribution
- [x] Filtering and noise detection
- [x] Tags and categorization
- [x] Review and validation workflow
- [x] Escalation tracking
- [x] Patient impact assessment
- [x] Proper indexes for performance
- [x] JSONB for flexible config
- [x] Array fields with GIN indexes

---

## 🚀 Ready for Production

### PostgreSQL Tables (9)
1. ✅ `users` - Complete
2. ✅ `projects` - Complete
3. ✅ `keywords` - Complete
4. ✅ `data_sources` - Complete
5. ✅ `search_executions` - Complete
6. ✅ `safety_signals` - Complete
7. ✅ `filtered_posts` - Complete
8. ✅ `reports` - Complete
9. ✅ `audit_logs` - Complete

### MongoDB Collections (4)
1. ✅ `raw_pages` - Complete
2. ✅ `raw_posts` - Complete
3. ✅ `analyzed_posts` - Complete
4. ✅ `agent_traces` - Complete

---

## 🔒 Schema Lock Recommendation

**Status**: ✅ **APPROVED FOR MIGRATION LOCK**

The schema comprehensively covers all requirements from the Idea.md document. Any future changes should be handled via migrations.

### Minor Enhancements (Can be added via migration later):
1. Multimodal analysis fields (when implementing image/video analysis)
2. Elasticsearch integration (if needed for advanced search)
3. CRM sync status tracking (if needed)
4. API quota tracking (if needed)
5. User notification preferences (if needed)

---

**Reviewed**: May 6, 2026  
**Status**: Ready for Migration Lock  
**Next Step**: Create Alembic migrations for PostgreSQL
