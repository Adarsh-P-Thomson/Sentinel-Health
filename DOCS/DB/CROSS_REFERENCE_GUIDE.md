# Cross-Database Reference Guide

## Overview

Sentinel Health uses a hybrid database architecture where PostgreSQL tracks structured metadata and search operations, while MongoDB stores raw unstructured data (pages, posts, analysis results).

## Reference Flow

```
PostgreSQL (search_executions.id)
         ↓
MongoDB (raw_pages.search_execution_id)
         ↓
MongoDB (raw_posts.raw_page_id)
         ↓
MongoDB (analyzed_posts.raw_post_id)
         ↓
PostgreSQL (safety_signals.source_ids[])
```

---

## 1. Search Execution → Raw Pages

### PostgreSQL: `search_executions`
Tracks each search/crawl operation.

```sql
-- Create a search execution
INSERT INTO search_executions (
    id,
    project_id,
    source_id,
    search_query,
    keywords_used,
    search_type,
    status
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'project-uuid',
    'source-uuid',
    'Drug-Y side effects',
    ARRAY['Drug-Y', 'side effects', 'headache'],
    'keyword_search',
    'running'
);
```

### MongoDB: `raw_pages`
Stores raw HTML/page data with reference to search execution.

```javascript
// Store raw page data
db.raw_pages.insertOne({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000", // PostgreSQL UUID
  project_id: "project-uuid",
  source_id: "source-uuid",
  url: "https://reddit.com/r/pharmacy/new",
  url_hash: "sha256_hash_of_url",
  html_content: "<html>...</html>",
  text_content: "Extracted text...",
  title: "r/pharmacy - New Posts",
  links: [...],
  media: [...],
  http_status: 200,
  processing_status: "pending",
  fetched_at: new Date(),
  retention_policy: "low_value",
  expires_at: new Date(Date.now() + 30*24*60*60*1000) // 30 days
});
```

### Update PostgreSQL with MongoDB IDs

```sql
-- After storing pages in MongoDB, update search execution
UPDATE search_executions
SET 
    pages_found = 10,
    pages_stored = 10,
    mongodb_page_ids = ARRAY[
        '6645a1b2c3d4e5f6a7b8c9d0',
        '6645a1b2c3d4e5f6a7b8c9d1',
        '6645a1b2c3d4e5f6a7b8c9d2'
    ],
    status = 'completed',
    completed_at = CURRENT_TIMESTAMP
WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

---

## 2. Raw Pages → Raw Posts

### MongoDB: Extract posts from pages

```javascript
// Find a raw page
const page = db.raw_pages.findOne({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000"
});

// Extract posts from the page
db.raw_posts.insertOne({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000",
  raw_page_id: page._id, // MongoDB ObjectId reference
  project_id: "project-uuid",
  source_id: "source-uuid",
  source_type: "reddit",
  source_post_id: "reddit_abc123",
  source_url: "https://reddit.com/r/pharmacy/comments/abc123",
  content: "I've been taking Drug-Y and experiencing headaches...",
  author_username: "user123",
  likes: 45,
  posted_at: new Date("2026-05-06T08:30:00Z"),
  extracted_at: new Date(),
  processing_status: "pending",
  retention_policy: "low_value",
  expires_at: new Date(Date.now() + 30*24*60*60*1000)
});

// Update page with extraction count
db.raw_pages.updateOne(
  { _id: page._id },
  { 
    $set: { 
      processing_status: "completed",
      posts_extracted_count: 5,
      processed_at: new Date()
    }
  }
);
```

### Update PostgreSQL search execution

```sql
UPDATE search_executions
SET 
    posts_extracted = 5,
    mongodb_post_ids = ARRAY[
        '6645a1b2c3d4e5f6a7b8c9e0',
        '6645a1b2c3d4e5f6a7b8c9e1'
    ]
WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

---

## 3. Raw Posts → Analyzed Posts

### MongoDB: AI processing

```javascript
// Get pending posts
const rawPost = db.raw_posts.findOne({
  processing_status: "pending"
});

// After AI agent processing
db.analyzed_posts.insertOne({
  raw_post_id: rawPost._id, // MongoDB ObjectId reference
  project_id: rawPost.project_id,
  anonymized_content: "[DRUG] causing [SYMPTOM]...",
  pii_detected: true,
  pii_types: ["name", "location"],
  entities: {
    drugs: [{ name: "Drug-Y", dosage: "50mg", confidence: 0.95 }],
    symptoms: [{ name: "severe headaches", severity: "high", confidence: 0.89 }]
  },
  sentiment: {
    overall: "negative",
    score: -0.75,
    confidence: 0.88
  },
  virality: {
    score: 78.5,
    trend: "rising",
    viral_potential: "high"
  },
  safety_audit: {
    is_adverse_event: true,
    severity: "high",
    known_side_effect: false,
    requires_investigation: true,
    confidence: 0.91
  },
  signal_type: "adverse_event",
  signal_priority: "high",
  archived_to_postgres: false,
  postgres_signal_id: null,
  retention_policy: "high_value",
  langsmith_trace_id: "trace_abc123",
  processed_at: new Date()
});

// Update raw post status
db.raw_posts.updateOne(
  { _id: rawPost._id },
  { $set: { processing_status: "completed", processed_at: new Date() } }
);
```

---

## 4. Analyzed Posts → Safety Signals (Archive)

### High-value signals get archived to PostgreSQL

```javascript
// Find high-priority analyzed posts
const highPriorityPosts = db.analyzed_posts.find({
  signal_priority: { $in: ["high", "critical"] },
  archived_to_postgres: false
}).toArray();
```

### PostgreSQL: Create safety signal

```sql
-- Aggregate multiple posts into a single signal
INSERT INTO safety_signals (
    id,
    project_id,
    signal_type,
    severity,
    drug_name,
    symptom,
    mention_count,
    sentiment_score,
    virality_score,
    confidence_score,
    source_type,
    source_ids, -- Array of MongoDB analyzed_posts._id
    first_detected_at,
    trending_period,
    status,
    ai_analysis_summary,
    langsmith_trace_id
) VALUES (
    gen_random_uuid(),
    'project-uuid',
    'adverse_event',
    'high',
    'Drug-Y',
    'severe headaches',
    15, -- 15 mentions found
    -0.72, -- Average sentiment
    82.3, -- Virality score
    0.89, -- Confidence
    'reddit',
    ARRAY['6645a1b2c3d4e5f6a7b8c9e0', '6645a1b2c3d4e5f6a7b8c9e1'], -- MongoDB IDs
    '2026-05-06 08:30:00',
    '24h',
    'new',
    'Multiple users reporting severe headaches after taking Drug-Y 50mg',
    'trace_abc123'
) RETURNING id;
```

### MongoDB: Mark as archived

```javascript
// Update analyzed posts to mark as archived
db.analyzed_posts.updateMany(
  { 
    _id: { $in: [
      ObjectId("6645a1b2c3d4e5f6a7b8c9e0"),
      ObjectId("6645a1b2c3d4e5f6a7b8c9e1")
    ]}
  },
  { 
    $set: { 
      archived_to_postgres: true,
      postgres_signal_id: "postgres-signal-uuid",
      retention_policy: "high_value" // Prevent TTL deletion
    }
  }
);
```

---

## 5. Querying Across Databases

### Get complete search history

```sql
-- PostgreSQL: Get search execution
SELECT 
    se.id,
    se.search_query,
    se.status,
    se.pages_stored,
    se.posts_extracted,
    se.mongodb_page_ids,
    se.mongodb_post_ids,
    se.started_at,
    se.completed_at
FROM search_executions se
WHERE se.project_id = 'project-uuid'
ORDER BY se.started_at DESC
LIMIT 10;
```

```javascript
// MongoDB: Get raw pages for a search
db.raw_pages.find({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000"
}).toArray();

// MongoDB: Get posts from those pages
db.raw_posts.find({
  search_execution_id: "550e8400-e29b-41d4-a716-446655440000"
}).toArray();
```

### Get signal with source data

```sql
-- PostgreSQL: Get signal
SELECT 
    ss.id,
    ss.drug_name,
    ss.symptom,
    ss.severity,
    ss.source_ids, -- MongoDB IDs
    ss.langsmith_trace_id
FROM safety_signals ss
WHERE ss.id = 'signal-uuid';
```

```javascript
// MongoDB: Get analyzed posts for this signal
db.analyzed_posts.find({
  _id: { $in: [
    ObjectId("6645a1b2c3d4e5f6a7b8c9e0"),
    ObjectId("6645a1b2c3d4e5f6a7b8c9e1")
  ]}
}).toArray();

// MongoDB: Get original raw posts
db.raw_posts.find({
  _id: { $in: analyzedPosts.map(p => p.raw_post_id) }
}).toArray();

// MongoDB: Get original pages
db.raw_pages.find({
  _id: { $in: rawPosts.map(p => p.raw_page_id) }
}).toArray();
```

---

## 6. Data Retention & Cleanup

### Low-value data (auto-purged after 30 days)

```javascript
// MongoDB TTL indexes handle this automatically
// raw_pages with retention_policy: "low_value" expire after 30 days
// raw_posts with retention_policy: "low_value" expire after 30 days
```

### High-value data (permanent)

```javascript
// Analyzed posts marked as high_value don't expire
db.analyzed_posts.updateMany(
  { signal_priority: { $in: ["high", "critical"] } },
  { $set: { retention_policy: "high_value", expires_at: null } }
);
```

### PostgreSQL cleanup (optional)

```sql
-- Archive old search executions (keep metadata, remove MongoDB references)
UPDATE search_executions
SET 
    mongodb_page_ids = NULL,
    mongodb_post_ids = NULL
WHERE completed_at < NOW() - INTERVAL '90 days'
  AND status = 'completed';
```

---

## 7. Reference Integrity

### Checking for orphaned records

```javascript
// Find analyzed posts without raw posts
db.analyzed_posts.aggregate([
  {
    $lookup: {
      from: "raw_posts",
      localField: "raw_post_id",
      foreignField: "_id",
      as: "raw_post"
    }
  },
  { $match: { raw_post: { $size: 0 } } }
]);

// Find raw posts without pages
db.raw_posts.aggregate([
  {
    $lookup: {
      from: "raw_pages",
      localField: "raw_page_id",
      foreignField: "_id",
      as: "raw_page"
    }
  },
  { $match: { raw_page: { $size: 0 } } }
]);
```

### Validating PostgreSQL → MongoDB references

```sql
-- Get search executions with MongoDB references
SELECT 
    id,
    mongodb_page_ids,
    array_length(mongodb_page_ids, 1) as page_count
FROM search_executions
WHERE mongodb_page_ids IS NOT NULL;
```

```javascript
// Verify MongoDB documents exist
const searchExecution = /* from PostgreSQL */;
const pageCount = db.raw_pages.countDocuments({
  _id: { $in: searchExecution.mongodb_page_ids.map(id => ObjectId(id)) }
});
```

---

## Best Practices

1. **Always create PostgreSQL search_execution first** before storing MongoDB data
2. **Store MongoDB ObjectIds as strings** in PostgreSQL arrays
3. **Update PostgreSQL with MongoDB IDs** after successful insertion
4. **Mark high-value data** to prevent TTL deletion
5. **Use transactions** where possible for consistency
6. **Log cross-database operations** in audit_logs
7. **Validate references** periodically to catch orphaned records

---

**Last Updated**: May 6, 2026
