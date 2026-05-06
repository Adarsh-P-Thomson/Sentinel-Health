# Database Schema Summary

## Updated Architecture (v1.0)

### Key Changes
✅ Added **raw_pages** collection in MongoDB to store complete page data (HTML, links, metadata)  
✅ Added **search_executions** table in PostgreSQL to track each search operation  
✅ Established clear cross-database references using UUIDs and ObjectIds  
✅ Separated page fetching from post extraction for better data organization  

---

## Agent Pipeline Flow

```
Raw Post
    ↓
[1] Relevance Filter → Filter out noise/irrelevant posts
    ↓ (if relevant)
[2] Anonymizer Agent → Remove PII/PHI
    ↓
[3] Medical Entity Extractor → Extract drugs, symptoms, conditions
    ↓
[4] Sentiment Analyst → Analyze emotional tone
    ↓
[5] Trend & Virality Agent → Assess engagement and trends
    ↓
[6] Safety Auditor → Verify against medical databases
    ↓
[7] AI Interpreter → Generate summary and recommendations
    ↓
Analyzed Post (MongoDB) → High-value signals archived to PostgreSQL
```

### New AI Analysis Features

✅ **Relevance Filtering** - Filter noise before expensive AI processing  
✅ **AI Interpretation** - Human-readable summaries and recommendations  
✅ **Recommended Actions** - AI suggests: monitor, investigate, escalate, archive  
✅ **Risk Categorization** - 5-level risk assessment  
✅ **Clinical Significance** - Explanation of medical importance  
✅ **Patient Impact Score** - Quality of life impact assessment  
✅ **Filtering Tracking** - PostgreSQL table tracks all filtered posts  
✅ **Tags & Categories** - AI-suggested tags for organization  
✅ **Confidence Scores** - Per-agent and overall confidence  

---

## PostgreSQL Tables (9 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| **users** | Authentication & authorization | email, role, password_hash |
| **projects** | Monitoring projects | name, status, created_by |
| **keywords** | Keywords to monitor | keyword, category, priority |
| **data_sources** | Social media sources | source_type, source_name, config (JSONB) |
| **search_executions** | Track each search operation | search_query, mongodb_page_ids[], mongodb_post_ids[] |
| **safety_signals** | High-value archived signals | drug_name, symptom, severity, ai_summary, recommended_action |
| **filtered_posts** | Filtered/rejected posts tracking | filter_reason, relevance_score, ai_explanation |
| **reports** | Generated reports | report_type, full_report (JSONB) |
| **audit_logs** | Compliance audit trail | action, resource_type, details (JSONB) |

---

## MongoDB Collections (4 collections)

| Collection | Purpose | TTL | Key Fields |
|------------|---------|-----|------------|
| **raw_pages** | Raw HTML/page data | 30 days (low_value) | url, html_content, links[], search_execution_id |
| **raw_posts** | Extracted posts from pages | 30 days (low_value) | content, raw_page_id, search_execution_id |
| **analyzed_posts** | AI-processed posts with comprehensive analysis | Permanent (high_value) | relevance, entities, sentiment, virality, safety_audit, ai_interpretation |
| **agent_traces** | Execution traces | 90 days | agent_name, llm_provider, duration_ms, cache_hit |

---

## Cross-Database References

### PostgreSQL → MongoDB
```sql
-- search_executions stores MongoDB ObjectIds as strings
search_executions.mongodb_page_ids[] → raw_pages._id
search_executions.mongodb_post_ids[] → raw_posts._id

-- safety_signals stores MongoDB ObjectIds as strings
safety_signals.source_ids[] → analyzed_posts._id
```

### MongoDB → PostgreSQL
```javascript
// MongoDB stores PostgreSQL UUIDs as strings
raw_pages.search_execution_id → search_executions.id
raw_posts.search_execution_id → search_executions.id
raw_posts.project_id → projects.id
raw_posts.source_id → data_sources.id
```

### MongoDB → MongoDB
```javascript
raw_posts.raw_page_id → raw_pages._id (ObjectId)
analyzed_posts.raw_post_id → raw_posts._id (ObjectId)
agent_traces.analyzed_post_id → analyzed_posts._id (ObjectId)
```

---

## Example: Complete Search Flow

### 1. Create Search Execution (PostgreSQL)
```sql
INSERT INTO search_executions (id, project_id, source_id, search_query, search_type, status)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'project-uuid',
    'source-uuid',
    'Drug-Y side effects',
    'keyword_search',
    'running'
);
```

### 2. Store Raw Page (MongoDB)
```javascript
db.raw_pages.insertOne({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000",
  url: "https://reddit.com/r/pharmacy/new",
  url_hash: "sha256_hash",
  html_content: "<html>...</html>",
  text_content: "Extracted text...",
  links: [...],
  fetched_at: new Date(),
  retention_policy: "low_value",
  expires_at: new Date(Date.now() + 30*24*60*60*1000)
});
// Returns: { _id: ObjectId("6645a1b2c3d4e5f6a7b8c9d0") }
```

### 3. Extract Posts from Page (MongoDB)
```javascript
db.raw_posts.insertOne({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000",
  raw_page_id: ObjectId("6645a1b2c3d4e5f6a7b8c9d0"),
  source_type: "reddit",
  content: "I've been taking Drug-Y and experiencing headaches...",
  posted_at: new Date("2026-05-06T08:30:00Z"),
  extracted_at: new Date(),
  processing_status: "pending"
});
// Returns: { _id: ObjectId("6645a1b2c3d4e5f6a7b8c9e0") }
```

### 4. Update Search Execution (PostgreSQL)
```sql
UPDATE search_executions
SET 
    pages_stored = 1,
    posts_extracted = 1,
    mongodb_page_ids = ARRAY['6645a1b2c3d4e5f6a7b8c9d0'],
    mongodb_post_ids = ARRAY['6645a1b2c3d4e5f6a7b8c9e0'],
    status = 'completed',
    completed_at = CURRENT_TIMESTAMP
WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

### 5. AI Processing (MongoDB)
```javascript
db.analyzed_posts.insertOne({
  raw_post_id: ObjectId("6645a1b2c3d4e5f6a7b8c9e0"),
  anonymized_content: "[DRUG] causing [SYMPTOM]...",
  entities: {
    drugs: [{ name: "Drug-Y", confidence: 0.95 }],
    symptoms: [{ name: "severe headaches", confidence: 0.89 }]
  },
  safety_audit: {
    is_adverse_event: true,
    severity: "high",
    requires_investigation: true
  },
  signal_priority: "high",
  processed_at: new Date()
});
```

### 6. Archive to PostgreSQL (High-Value)
```sql
INSERT INTO safety_signals (
    project_id, signal_type, severity, drug_name, symptom,
    source_ids, first_detected_at, status
) VALUES (
    'project-uuid', 'adverse_event', 'high', 'Drug-Y', 'severe headaches',
    ARRAY['6645a1b2c3d4e5f6a7b8c9e0'], -- MongoDB analyzed_posts._id
    '2026-05-06 08:30:00', 'new'
);
```

---

## Data Retention

| Data Type | Storage | Retention | Reason |
|-----------|---------|-----------|--------|
| Raw pages (low-value) | MongoDB | 30 days | Reduce storage costs |
| Raw posts (low-value) | MongoDB | 30 days | Reduce storage costs |
| Analyzed posts (high-value) | MongoDB | Permanent | Evidence for signals |
| Safety signals | PostgreSQL | Permanent | Regulatory compliance |
| Agent traces | MongoDB | 90 days | Debugging & compliance |
| Search executions | PostgreSQL | Permanent | Audit trail |

---

## Unique Features

1. **URL Deduplication**: `raw_pages.url_hash` prevents duplicate page fetches
2. **Hierarchical References**: Page → Posts → Analysis → Signals
3. **Bidirectional Tracking**: PostgreSQL tracks MongoDB IDs, MongoDB tracks PostgreSQL UUIDs
4. **Automatic Cleanup**: TTL indexes auto-delete old low-value data
5. **Full Traceability**: Every signal can be traced back to original page HTML
6. **Flexible Schema**: MongoDB handles varying page/post structures
7. **ACID Compliance**: Critical metadata in PostgreSQL with transactions

---

## Files

- **Architecture**: `DOCS/DB/DATABASE_ARCHITECTURE.md`
- **Cross-Reference Guide**: `DOCS/DB/CROSS_REFERENCE_GUIDE.md`
- **PostgreSQL Schema**: `DOCS/DB/POSTGRES/schema.sql`
- **PostgreSQL Setup**: `DOCS/DB/POSTGRES/README.md`
- **MongoDB Schema**: `DOCS/DB/MONGODB/schema.js`
- **MongoDB Setup**: `DOCS/DB/MONGODB/README.md`

---

**Version**: 1.0  
**Last Updated**: May 6, 2026  
**Status**: ✅ Ready for Implementation
