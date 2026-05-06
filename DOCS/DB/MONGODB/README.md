# MongoDB Setup - Sentinel Health

## Overview

MongoDB stores high-volume, unstructured data including raw social media posts, AI analysis results, and agent execution traces.

## Collections

| Collection | Purpose | TTL |
|------------|---------|-----|
| `raw_posts` | Raw social media posts before processing | 30 days (low_value) |
| `analyzed_posts` | Posts after AI agent processing | Permanent (high_value) |
| `agent_traces` | Detailed execution traces for explainability | 90 days |
| `crawl_jobs` | Crawl job execution tracking | 30 days |

## Prerequisites

- MongoDB 6.0+
- MongoDB Shell (mongosh)

## Installation

### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

### Ubuntu/Debian
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

### Windows
Download and install from: https://www.mongodb.com/try/download/community

## Quick Setup

### 1. Start MongoDB
```bash
# Check if MongoDB is running
mongosh --eval "db.version()"
```

### 2. Create Database & Apply Schema
```bash
# Navigate to schema directory
cd DOCS/DB/MONGODB

# Apply schema
mongosh < schema.js
```

You should see:
```
✓ Created collection: raw_posts
✓ Created collection: analyzed_posts
✓ Created collection: agent_traces
✓ Created collection: crawl_jobs
✓ Inserted sample data
✓ Schema version recorded
```

### 3. Verify Setup
```bash
mongosh sentinel_health --eval "db.getCollectionNames()"
```

Expected output:
```javascript
[
  'raw_posts',
  'analyzed_posts',
  'agent_traces',
  'crawl_jobs',
  'schema_version'
]
```

## Configuration

### Connection String

**Development**:
```
mongodb://localhost:27017/sentinel_health
```

**Production** (with authentication):
```
mongodb://username:password@host:27017/sentinel_health?authSource=admin
```

### Environment Variables

Add to your `.env` file:
```env
MONGODB_URL=mongodb://localhost:27017/sentinel_health
MONGODB_DB_NAME=sentinel_health
```

## Schema Validation

All collections have JSON Schema validation enabled. Invalid documents will be rejected.

Example validation error:
```javascript
MongoServerError: Document failed validation
```

## Indexes

### Performance Indexes
- `raw_posts`: Compound index on `(project_id, crawled_at)`
- `analyzed_posts`: Index on `signal_priority` for fast filtering
- `agent_traces`: Index on `(agent_name, started_at)` for analytics

### TTL Indexes
- `raw_posts.expires_at`: Auto-delete after 30 days (low_value data)
- `agent_traces.started_at`: Auto-delete after 90 days
- `crawl_jobs.started_at`: Auto-delete after 30 days

## Data Retention

### Low Value Data (30 days)
```javascript
{
  retention_policy: "low_value",
  expires_at: ISODate("2026-06-05T10:00:00Z")
}
```

### High Value Data (Permanent)
```javascript
{
  retention_policy: "high_value",
  expires_at: null // No expiration
}
```

High-value signals are also archived to PostgreSQL for long-term storage.

## Common Operations

### View Recent Posts
```javascript
use sentinel_health;
db.raw_posts.find().sort({ crawled_at: -1 }).limit(10);
```

### Check Processing Status
```javascript
db.raw_posts.aggregate([
  { $group: { _id: "$processing_status", count: { $sum: 1 } } }
]);
```

### Find High-Priority Signals
```javascript
db.analyzed_posts.find({
  signal_priority: { $in: ["high", "critical"] },
  archived_to_postgres: false
}).sort({ processed_at: -1 });
```

### View Agent Performance
```javascript
db.agent_traces.aggregate([
  { $group: {
    _id: "$agent_name",
    avg_duration: { $avg: "$duration_ms" },
    total_cost: { $sum: "$total_cost" },
    cache_hit_rate: { $avg: { $cond: ["$cache_hit", 1, 0] } }
  }}
]);
```

## Backup & Restore

### Backup
```bash
mongodump --db sentinel_health --out /backup/$(date +%Y%m%d)
```

### Restore
```bash
mongorestore --db sentinel_health /backup/20260506/sentinel_health
```

## Monitoring

### Check Database Size
```javascript
use sentinel_health;
db.stats(1024*1024); // Size in MB
```

### Collection Statistics
```javascript
db.raw_posts.stats(1024*1024);
```

### Index Usage
```javascript
db.raw_posts.aggregate([{ $indexStats: {} }]);
```

## Troubleshooting

### Connection Refused
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

### Validation Errors
Check the schema validator:
```javascript
db.getCollectionInfos({ name: "raw_posts" })[0].options.validator;
```

### Slow Queries
Enable profiling:
```javascript
db.setProfilingLevel(1, { slowms: 100 });
db.system.profile.find().sort({ ts: -1 }).limit(5);
```

## Security

### Create Application User
```javascript
use admin;
db.createUser({
  user: "sentinel_app",
  pwd: "CHANGE_THIS_PASSWORD",
  roles: [
    { role: "readWrite", db: "sentinel_health" }
  ]
});
```

### Enable Authentication
Edit `/etc/mongod.conf`:
```yaml
security:
  authorization: enabled
```

Restart MongoDB:
```bash
sudo systemctl restart mongod
```

## Next Steps

1. ✅ MongoDB schema applied
2. 🔧 Configure connection in FastAPI backend
3. 🔧 Set up Motor (async MongoDB driver)
4. 🔧 Implement data models with Pydantic

---

**Last Updated**: May 6, 2026
