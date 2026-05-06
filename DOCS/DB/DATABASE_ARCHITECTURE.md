# Database Architecture - Sentinel Health

## Overview

Sentinel Health uses a **hybrid database architecture** combining PostgreSQL and MongoDB to optimize for different data types and access patterns.

### Database Selection Strategy

| Database | Purpose | Data Types |
|----------|---------|------------|
| **PostgreSQL** | Structured, relational data requiring ACID compliance | Projects, Users, Configurations, High-Value Signals, Reports |
| **MongoDB** | Unstructured, high-volume data with flexible schemas | Raw Social Posts, AI Analysis Results, Agent Traces, Temporary Data |

---

## PostgreSQL Schema

**Use Case**: Structured configuration, user management, validated safety signals, and historical reporting.

### Why PostgreSQL?
- ✅ ACID compliance for critical configuration data
- ✅ Complex joins for reporting and analytics
- ✅ Strong data integrity with foreign keys
- ✅ Efficient indexing for time-series queries
- ✅ Perfect for "High Value" archived signals

### Tables

#### 1. **users**
User authentication and role management.

```sql
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
```

#### 2. **projects**
Monitoring projects configured by admins.

```sql
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
```

#### 3. **keywords**
Keywords to monitor per project.

```sql
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
```

#### 4. **data_sources**
Configured data sources (X, Reddit, forums).

```sql
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
```

#### 5. **safety_signals** (High-Value Archive)
Validated, high-priority safety signals for permanent storage.

```sql
CREATE TABLE safety_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    signal_type VARCHAR(100) NOT NULL, -- adverse_event, quality_issue, sentiment_spike
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    drug_name VARCHAR(255),
    symptom VARCHAR(255),
    condition VARCHAR(255),
    
    -- Aggregated metrics
    mention_count INTEGER DEFAULT 1,
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    virality_score DECIMAL(5,2), -- 0 to 100
    confidence_score DECIMAL(3,2), -- 0.0 to 1.0
    
    -- Source tracking
    source_type VARCHAR(100),
    source_ids TEXT[], -- Array of MongoDB document IDs
    
    -- Temporal data
    first_detected_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trending_period VARCHAR(50), -- 1h, 6h, 24h, 7d
    
    -- Status
    status VARCHAR(50) DEFAULT 'new', -- new, investigating, validated, false_positive, resolved
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- AI metadata
    ai_analysis_summary TEXT,
    langsmith_trace_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_project ON safety_signals(project_id);
CREATE INDEX idx_signals_severity ON safety_signals(severity);
CREATE INDEX idx_signals_status ON safety_signals(status);
CREATE INDEX idx_signals_drug ON safety_signals(drug_name);
CREATE INDEX idx_signals_detected_at ON safety_signals(first_detected_at DESC);
CREATE INDEX idx_signals_trending ON safety_signals(trending_period, virality_score DESC);
```

#### 6. **reports**
Generated patient impact reports.

```sql
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
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
```

#### 7. **audit_logs**
System audit trail for compliance.

```sql
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
CREATE INDEX idx_audit_created_at ON audit_logs(created_at DESC);
```

---

## MongoDB Schema

**Use Case**: High-volume, unstructured data including raw pages, extracted posts, AI analysis results, and agent traces.

### Why MongoDB?
- ✅ Flexible schema for varying page/post structures
- ✅ High write throughput for real-time data ingestion
- ✅ Efficient storage of nested JSON (AI analysis results)
- ✅ TTL indexes for automatic data expiration (30-day purge)
- ✅ Full-text search capabilities
- ✅ Store complete raw HTML/page data

### Collections

#### 1. **raw_pages**
Complete raw page data from web scraping.

```javascript
{
  _id: ObjectId("..."),
  search_execution_id: "uuid-string", // References PostgreSQL search_executions.id
  project_id: "uuid-string",
  source_id: "uuid-string",
  
  // Page identification
  url: "https://reddit.com/r/pharmacy/new",
  url_hash: "sha256_hash", // For deduplication
  canonical_url: "https://reddit.com/r/pharmacy/new",
  
  // Raw content
  html_content: "<html>...</html>",
  text_content: "Extracted text without HTML tags",
  
  // Page metadata
  title: "r/pharmacy - New Posts",
  description: "Meta description",
  author: "Page author if available",
  published_date: ISODate("2026-05-06T10:00:00Z"),
  
  // Links found on page
  links: [
    {
      href: "/r/pharmacy/comments/abc123",
      text: "Drug-Y side effects discussion",
      type: "internal" // internal, external, social
    }
  ],
  
  // Media found on page
  media: [
    {
      type: "image",
      url: "https://...",
      alt_text: "Photo of rash"
    }
  ],
  
  // HTTP metadata
  http_status: 200,
  headers: { "content-type": "text/html" },
  
  // Processing status
  processing_status: "completed", // pending, processing, completed, failed
  posts_extracted_count: 5,
  
  // Temporal
  fetched_at: ISODate("2026-05-06T10:00:00Z"),
  processed_at: ISODate("2026-05-06T10:01:00Z"),
  
  // Retention
  retention_policy: "low_value",
  expires_at: ISODate("2026-06-05T10:00:00Z"), // 30 days
  
  created_at: ISODate("2026-05-06T10:00:00Z")
}

// Indexes
db.raw_pages.createIndex({ search_execution_id: 1 });
db.raw_pages.createIndex({ project_id: 1, fetched_at: -1 });
db.raw_pages.createIndex({ url_hash: 1 }, { unique: true });
db.raw_pages.createIndex({ url: 1 });
db.raw_pages.createIndex({ processing_status: 1 });
db.raw_pages.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 }); // TTL
db.raw_pages.createIndex({ text_content: "text" }); // Full-text search
```

#### 2. **raw_posts**
Individual posts/comments extracted from raw pages.

```javascript
{
  _id: ObjectId("..."),
  search_execution_id: "uuid-string", // References PostgreSQL search_executions.id
  raw_page_id: ObjectId("..."), // References raw_pages._id
  project_id: "uuid-string",
  source_id: "uuid-string",
  
  // Source metadata
  source_type: "twitter", // twitter, reddit, quora, forum
  source_post_id: "tweet_123456", // Original platform ID
  source_url: "https://twitter.com/user/status/123456",
  
  // Content
  content: "I've been taking Drug-Y and experiencing severe headaches...",
  author_username: "user123", // May contain PII - to be anonymized
  author_id: "platform_user_id",
  
  // Engagement metrics
  likes: 150,
  shares: 45,
  comments: 23,
  views: 1200,
  
  // Temporal
  posted_at: ISODate("2026-05-06T10:30:00Z"),
  extracted_at: ISODate("2026-05-06T10:35:00Z"),
  
  // Processing status
  processing_status: "pending", // pending, processing, completed, failed
  processed_at: ISODate("2026-05-06T10:36:00Z"),
  
  // Metadata
  language: "en",
  location: "New York, USA", // May contain PII
  hashtags: ["DrugY", "SideEffects"],
  mentions: ["@FDA", "@HealthCare"],
  
  // Media attachments
  media: [
    {
      type: "image",
      url: "https://...",
      description: "Photo of rash"
    }
  ],
  
  // Retention
  retention_policy: "low_value", // low_value, high_value
  expires_at: ISODate("2026-06-05T10:35:00Z"), // 30 days for low_value
  
  created_at: ISODate("2026-05-06T10:35:00Z")
}

// Indexes
db.raw_posts.createIndex({ search_execution_id: 1 });
db.raw_posts.createIndex({ raw_page_id: 1 });
db.raw_posts.createIndex({ project_id: 1, extracted_at: -1 });
db.raw_posts.createIndex({ source_id: 1 });
db.raw_posts.createIndex({ processing_status: 1 });
db.raw_posts.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 }); // TTL index
db.raw_posts.createIndex({ content: "text" }); // Full-text search
```

#### 3. **analyzed_posts**
Posts after AI agent processing.

```javascript
{
  _id: ObjectId("..."),
  raw_post_id: ObjectId("..."), // References raw_posts._id
  project_id: "uuid-string",
  
  // Anonymized content
  anonymized_content: "I've been taking [DRUG] and experiencing [SYMPTOM]...",
  pii_detected: true,
  pii_types: ["name", "location"],
  
  // Medical entity extraction
  entities: {
    drugs: [
      {
        name: "Drug-Y",
        dosage: "50mg",
        frequency: "twice daily",
        confidence: 0.95
      }
    ],
    symptoms: [
      {
        name: "severe headaches",
        severity: "high",
        confidence: 0.89
      }
    ],
    conditions: [
      {
        name: "migraine",
        confidence: 0.72
      }
    ]
  },
  
  // Sentiment analysis
  sentiment: {
    overall: "negative",
    score: -0.75, // -1 to 1
    emotions: ["frustration", "concern"],
    confidence: 0.88
  },
  
  // Trend & virality
  virality: {
    score: 78.5, // 0-100
    trend: "rising", // rising, stable, declining
    engagement_rate: 0.15,
    viral_potential: "high" // low, medium, high
  },
  
  // Safety audit
  safety_audit: {
    is_adverse_event: true,
    severity: "high", // low, medium, high, critical
    known_side_effect: false,
    requires_investigation: true,
    confidence: 0.91
  },
  
  // Agent execution metadata
  agent_pipeline: {
    anonymizer: { status: "completed", duration_ms: 120 },
    extractor: { status: "completed", duration_ms: 450 },
    sentiment: { status: "completed", duration_ms: 200 },
    trend: { status: "completed", duration_ms: 180 },
    auditor: { status: "completed", duration_ms: 350 }
  },
  
  // Traceability
  langsmith_trace_id: "trace_abc123",
  langsmith_run_id: "run_xyz789",
  
  // Signal classification
  signal_type: "adverse_event", // adverse_event, quality_issue, sentiment_spike, null
  signal_priority: "high", // low, medium, high, critical
  archived_to_postgres: false,
  postgres_signal_id: null, // UUID if archived
  
  // Retention
  retention_policy: "high_value",
  
  processed_at: ISODate("2026-05-06T10:36:00Z"),
  created_at: ISODate("2026-05-06T10:36:00Z")
}

// Indexes
db.analyzed_posts.createIndex({ raw_post_id: 1 });
db.analyzed_posts.createIndex({ project_id: 1, processed_at: -1 });
db.analyzed_posts.createIndex({ "safety_audit.is_adverse_event": 1, "safety_audit.severity": 1 });
db.analyzed_posts.createIndex({ signal_priority: 1 });
db.analyzed_posts.createIndex({ archived_to_postgres: 1 });
```

#### 3. **agent_traces**
Detailed execution traces for explainability.

```javascript
{
  _id: ObjectId("..."),
  trace_id: "trace_abc123",
  run_id: "run_xyz789",
  analyzed_post_id: ObjectId("..."),
  
  // Execution details
  agent_name: "medical_entity_extractor",
  input: { /* agent input */ },
  output: { /* agent output */ },
  
  // LLM details
  llm_provider: "openai",
  model: "gpt-4",
  prompt_tokens: 450,
  completion_tokens: 120,
  total_cost: 0.0234,
  
  // Performance
  duration_ms: 450,
  status: "success", // success, failed, timeout
  error: null,
  
  // Caching
  cache_hit: false,
  cache_key: "hash_of_input",
  
  started_at: ISODate("2026-05-06T10:36:00Z"),
  completed_at: ISODate("2026-05-06T10:36:00.450Z"),
  created_at: ISODate("2026-05-06T10:36:00.450Z")
}

// Indexes
db.agent_traces.createIndex({ trace_id: 1 });
db.agent_traces.createIndex({ analyzed_post_id: 1 });
db.agent_traces.createIndex({ agent_name: 1, created_at: -1 });
db.agent_traces.createIndex({ cache_key: 1 });
```

---

## Data Flow Between Databases

### Write Flow
1. **Search Initiated** → PostgreSQL `search_executions` (create record with unique ID)
2. **Raw Pages Fetched** → MongoDB `raw_pages` (store HTML, links, metadata with search_execution_id)
3. **Posts Extracted** → MongoDB `raw_posts` (extract posts from pages with raw_page_id reference)
4. **Update Search** → PostgreSQL `search_executions` (update with MongoDB ObjectIds)
5. **AI Processing** → MongoDB `analyzed_posts` (flexible schema for analysis results)
6. **High-Value Signals** → PostgreSQL `safety_signals` (permanent archive with MongoDB references)
7. **Reports Generated** → PostgreSQL `reports` (structured data)

### Read Flow
1. **Dashboard Real-Time View** → MongoDB `analyzed_posts` (recent data)
2. **Historical Trends** → PostgreSQL `safety_signals` (aggregated data)
3. **Search History** → PostgreSQL `search_executions` → MongoDB `raw_pages`/`raw_posts`
4. **Explainability** → MongoDB `agent_traces` + LangSmith
5. **Admin Configuration** → PostgreSQL (projects, keywords, sources)

### Data Retention Policy
- **Raw Pages** (MongoDB): 30-day TTL for low-value, permanent for high-value
- **Raw Posts** (MongoDB): 30-day TTL for low-value, permanent for high-value
- **Analyzed Posts** (MongoDB): Permanent for high-value signals
- **High Value Signals** (PostgreSQL): Permanent storage
- **Agent Traces** (MongoDB): 90-day retention for compliance
- **Search Executions** (PostgreSQL): Permanent metadata, optional cleanup of MongoDB references after 90 days

---

## Relationships & Foreign Keys

### PostgreSQL Relationships
```
users (1) ──→ (N) projects
projects (1) ──→ (N) keywords
projects (1) ──→ (N) data_sources
projects (1) ──→ (N) search_executions
data_sources (1) ──→ (N) search_executions
projects (1) ──→ (N) safety_signals
safety_signals (1) ──→ (N) reports
users (1) ──→ (N) audit_logs
```

### MongoDB Relationships
```
raw_pages (1) ──→ (N) raw_posts (via raw_page_id)
raw_posts (1) ──→ (1) analyzed_posts (via raw_post_id)
analyzed_posts (1) ──→ (N) agent_traces (via analyzed_post_id)
```

### Cross-Database References
- PostgreSQL `search_executions.id` → MongoDB `raw_pages.search_execution_id`
- PostgreSQL `search_executions.id` → MongoDB `raw_posts.search_execution_id`
- PostgreSQL `search_executions.mongodb_page_ids[]` ← MongoDB `raw_pages._id`
- PostgreSQL `search_executions.mongodb_post_ids[]` ← MongoDB `raw_posts._id`
- MongoDB `raw_pages.search_execution_id` → PostgreSQL `search_executions.id`
- MongoDB `analyzed_posts` → PostgreSQL `safety_signals.source_ids[]`
- PostgreSQL `safety_signals.langsmith_trace_id` → MongoDB `agent_traces.trace_id`

---

## Performance Considerations

### PostgreSQL Optimizations
- Partitioning `safety_signals` by `first_detected_at` (monthly partitions)
- Materialized views for dashboard aggregations
- Connection pooling (PgBouncer)

### MongoDB Optimizations
- Sharding `raw_posts` by `project_id` for horizontal scaling
- Compound indexes for common query patterns
- TTL indexes for automatic data expiration
- Read replicas for analytics queries

---

## Next Steps

1. ✅ Review and approve schema design
2. 🔧 Create migration scripts for PostgreSQL
3. 🔧 Create initialization scripts for MongoDB
4. 🔧 Set up database connection pooling
5. 🔧 Implement ORM models (SQLAlchemy + Motor)

---

**Last Updated**: May 6, 2026
