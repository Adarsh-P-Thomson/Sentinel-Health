## Batch Processing System

## Overview

The batch processing system processes raw Reddit/social media posts in batches with:
- **Character limits** (8000 chars per batch ~2000 tokens)
- **Automatic categorization** (medicine, hospital, drug, condition, etc.)
- **AI-powered analysis** (suggestions, info, sentiment, severity)
- **Progress tracking** (batch status, completion tracking)

---

## Architecture

```
Raw Posts → Create Batches → Process with AI → Store in Categories → Mark as Done
            (8000 chars)      (Azure OpenAI)    (MongoDB)           (Status: completed)
```

### Collections:

1. **`raw_posts`** - Original posts from search
2. **`processing_batches`** - Batch tracking and status
3. **`processed_categories`** - Categorized AI-processed content

---

## How It Works

### Step 1: Create Batches

Posts are grouped into batches based on:
- **Max characters**: 8000 per batch (~2000 tokens)
- **Max posts**: 20 per batch

```python
# Example: 100 posts → 5 batches
Batch 1: Posts 1-20 (7800 chars)
Batch 2: Posts 21-40 (8000 chars)
Batch 3: Posts 41-60 (7500 chars)
Batch 4: Posts 61-80 (8000 chars)
Batch 5: Posts 81-100 (6200 chars)
```

### Step 2: Process Each Batch

For each batch:
1. **Clean & Anonymize** - Remove PII/PHI locally
2. **Send to AI** - Process with Azure OpenAI
3. **Extract Categories** - Identify medicine, hospital, drug, etc.
4. **Store Results** - Save in categorized collections
5. **Mark as Done** - Update batch status to "completed"

### Step 3: Categorization

AI extracts:
- **category_name**: "Ibuprofen", "Mayo Clinic", "Diabetes"
- **category_type**: medicine, hospital, drug, condition, symptom, procedure, general
- **processed_text**: Clean summary (1-2 sentences)
- **ai_suggestion**: Actionable recommendation
- **ai_info**: Additional context
- **sentiment**: very_negative → very_positive
- **severity**: low, medium, high, critical
- **is_adverse_event**: true/false

### Step 4: Storage

Results are stored in `processed_categories` collection:

```javascript
{
  "category_name": "Ibuprofen",
  "category_type": "medicine",
  "processed_entries": [
    {
      "entry_id": "uuid-1",
      "original_post_id": ObjectId("..."),
      "batch_id": "batch-uuid",
      "processed_text": "Patient reports severe stomach pain after taking Ibuprofen 200mg three times daily for 2 weeks.",
      "ai_suggestion": "Consider switching to acetaminophen or consulting gastroenterologist.",
      "ai_info": "Ibuprofen is an NSAID that can cause gastrointestinal issues with prolonged use.",
      "sentiment": "negative",
      "severity": "medium",
      "is_adverse_event": true,
      "processed_at": ISODate("2026-05-07T10:00:00Z")
    },
    // More entries...
  ],
  "total_entries": 150,
  "last_updated": ISODate("2026-05-07T10:00:00Z"),
  "tags": ["NSAID", "pain relief", "anti-inflammatory"]
}
```

---

## API Endpoints

### 1. Process Latest Data (Automatic)

**POST** `/api/v1/process/latest`

**NEW!** Automatically finds and processes the most recent unprocessed search results. No need to know the search_execution_id!

**Request:**
```json
{}
```
(No body required - it automatically finds the latest unprocessed data)

**Response:**
```json
{
  "message": "Processing started for 100 posts in 5 batches",
  "search_execution_id": "auto-detected-uuid",
  "total_batches": 5,
  "status": "processing",
  "batch_ids": ["batch-1", "batch-2", "batch-3", "batch-4", "batch-5"]
}
```

**If no unprocessed data:**
```json
{
  "message": "No unprocessed data found",
  "search_execution_id": "",
  "total_batches": 0,
  "status": "no_posts_to_process",
  "batch_ids": []
}
```

**How it works:**
1. Queries `raw_posts` for posts with `processing_status = "pending"`
2. Groups by `search_execution_id`
3. Selects the most recent search_execution_id
4. Creates and processes batches automatically
5. Returns batch IDs for progress tracking

**Use this endpoint when:**
- User clicks "Process Latest Data" button
- You want to process the most recent search without knowing the ID
- Building a simple UX where users don't need to manage IDs

---

### 2. Process Search Execution (Manual)

**POST** `/api/v1/process/search`

Process all raw_posts from a specific search execution.

**Request:**
```json
{
  "search_execution_id": "uuid-here",
  "project_id": "optional-project-id",
  "background": false
}
```

**Response:**
```json
{
  "message": "Batch processing completed",
  "search_execution_id": "uuid-here",
  "total_batches": 5,
  "status": "completed",
  "batch_ids": ["batch-1", "batch-2", "batch-3", "batch-4", "batch-5"]
}
```

**Background Processing:**
Set `background: true` to process asynchronously:
```json
{
  "search_execution_id": "uuid-here",
  "background": true
}
```

Returns immediately with batch IDs. Check status with `/process/batch/{batch_id}/status`.

---

### 3. Process Single Batch

**POST** `/api/v1/process/batch`

Process a specific batch by ID.

**Request:**
```json
{
  "batch_id": "batch-uuid"
}
```

**Response:**
```json
{
  "batch_id": "batch-uuid",
  "status": "completed",
  "total_posts": 20,
  "processed_entries": 20,
  "processing_time_ms": 15000
}
```

---

### 3. Get Batch Status

**GET** `/api/v1/process/batch/{batch_id}/status`

Get the current status of a batch.

**Response:**
```json
{
  "batch_id": "batch-uuid",
  "status": "completed",
  "total_posts": 20,
  "processed_posts": 20,
  "failed_posts": 0,
  "character_count": 7800,
  "created_at": "2026-05-07T10:00:00Z",
  "started_at": "2026-05-07T10:00:05Z",
  "completed_at": "2026-05-07T10:02:30Z",
  "processing_time_ms": 145000
}
```

**Status Values:**
- `pending` - Batch created, not started
- `processing` - Currently being processed
- `completed` - Successfully completed
- `failed` - Processing failed (see error_message)

---

### 4. List Categories

**GET** `/api/v1/categories?category_type=medicine&limit=100`

List all processed categories.

**Query Parameters:**
- `category_type` (optional): Filter by type (medicine, hospital, drug, etc.)
- `limit` (default: 100): Max results

**Response:**
```json
[
  {
    "category_name": "Ibuprofen",
    "category_type": "medicine",
    "total_entries": 150,
    "last_updated": "2026-05-07T10:00:00Z",
    "tags": ["NSAID", "pain relief"]
  },
  {
    "category_name": "Lisinopril",
    "category_type": "medicine",
    "total_entries": 89,
    "last_updated": "2026-05-07T09:30:00Z",
    "tags": ["ACE inhibitor", "blood pressure"]
  }
]
```

---

### 5. Get Category Details

**GET** `/api/v1/categories/{category_name}?limit=50`

Get detailed information about a specific category.

**Response:**
```json
{
  "category_name": "Ibuprofen",
  "category_type": "medicine",
  "total_entries": 150,
  "entries": [
    {
      "entry_id": "uuid-1",
      "original_post_id": "post-id",
      "batch_id": "batch-uuid",
      "processed_text": "Patient reports severe stomach pain...",
      "ai_suggestion": "Consider switching to acetaminophen...",
      "ai_info": "Ibuprofen is an NSAID...",
      "sentiment": "negative",
      "severity": "medium",
      "is_adverse_event": true,
      "processed_at": "2026-05-07T10:00:00Z"
    }
    // More entries...
  ],
  "tags": ["NSAID", "pain relief"],
  "summary": {
    "total_adverse_events": 45,
    "avg_sentiment_score": -0.3,
    "severity_breakdown": {
      "low": 50,
      "medium": 70,
      "high": 25,
      "critical": 5
    }
  },
  "created_at": "2026-05-01T00:00:00Z",
  "last_updated": "2026-05-07T10:00:00Z"
}
```

---

## Usage Examples

### Example 1: Process Latest Data (Automatic - Recommended)

```bash
# 1. Perform search
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Lisinopril side effects",
    "sources": ["reddit_json"],
    "limit": 100
  }'

# Response: { "search_execution_id": "abc-123", ... }

# 2. Process the latest unprocessed data (no ID needed!)
curl -X POST "http://localhost:8000/api/v1/process/latest" \
  -H "Content-Type: application/json"

# Response: { "total_batches": 5, "status": "processing", "batch_ids": [...] }

# 3. Check batch status
curl "http://localhost:8000/api/v1/process/batch/batch-1/status"

# 4. View categories
curl "http://localhost:8000/api/v1/categories?category_type=medicine"

# 5. View specific category
curl "http://localhost:8000/api/v1/categories/Lisinopril"
```

---

### Example 2: Process Specific Search (Manual)

```bash
# 1. Perform search
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Lisinopril side effects",
    "sources": ["reddit_json"],
    "limit": 100
  }'

# Response: { "search_execution_id": "abc-123", ... }

# 2. Process the results with specific ID
curl -X POST "http://localhost:8000/api/v1/process/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_execution_id": "abc-123",
    "background": false
  }'

# Response: { "total_batches": 5, "status": "completed", ... }

# 3. View categories
curl "http://localhost:8000/api/v1/categories?category_type=medicine"

# 4. View specific category
curl "http://localhost:8000/api/v1/categories/Lisinopril"
```

---

### Example 3: Background Processing

```bash
# Start processing in background
curl -X POST "http://localhost:8000/api/v1/process/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_execution_id": "abc-123",
    "background": true
  }'

# Response: { "batch_ids": ["batch-1", "batch-2", ...], "status": "processing" }

# Check batch status
curl "http://localhost:8000/api/v1/process/batch/batch-1/status"

# Response: { "status": "processing", "processed_posts": 15, "total_posts": 20, ... }
```

---

## MongoDB Schema

### Collection: `processing_batches`

Tracks batch processing status.

```javascript
{
  "batch_id": "uuid",
  "search_execution_id": "uuid",
  "status": "completed",
  "total_posts": 20,
  "processed_posts": 20,
  "failed_posts": 0,
  "post_ids": [ObjectId("..."), ...],
  "character_count": 7800,
  "max_characters": 8000,
  "created_at": ISODate("..."),
  "started_at": ISODate("..."),
  "completed_at": ISODate("..."),
  "processing_time_ms": 145000,
  "ai_cost": 0.15
}
```

### Collection: `processed_categories`

Stores categorized processed content.

```javascript
{
  "category_name": "Ibuprofen",
  "category_type": "medicine",
  "processed_entries": [...],
  "total_entries": 150,
  "last_updated": ISODate("..."),
  "created_at": ISODate("..."),
  "tags": ["NSAID", "pain relief"],
  "summary": {
    "total_adverse_events": 45,
    "avg_sentiment_score": -0.3,
    "severity_breakdown": {...}
  }
}
```

---

## Setup

### 1. Create MongoDB Collections

```bash
mongosh Sentinel_health < DOCS/DB/MONGODB/schema_processed_categories.js
```

### 2. Configure Azure OpenAI

Make sure your `.env` has:
```bash
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### 3. Start Backend

```bash
cd Backend
uvicorn app.main:app --reload
```

### 4. Test

```bash
# Process a search
curl -X POST "http://localhost:8000/api/v1/process/search" \
  -H "Content-Type: application/json" \
  -d '{"search_execution_id": "your-search-id"}'
```

---

## Performance

- **Batch Size**: 8000 chars (~2000 tokens)
- **Processing Time**: ~15-30 seconds per batch (depends on Azure OpenAI)
- **Cost**: ~$0.03-0.06 per batch (GPT-4)
- **Throughput**: ~40-80 posts/minute

**Optimization Tips:**
- Use `background=true` for large searches
- Use GPT-3.5-Turbo for faster/cheaper processing
- Adjust `max_chars_per_batch` based on your needs

---

## Next Steps

1. ✅ Batch processing implemented
2. ✅ Categorization system created
3. ✅ API endpoints ready
4. ✅ **Frontend integration complete**
5. ✅ **Real-time progress tracking implemented**
6. ✅ **Automatic processing endpoint added**
7. ⏳ **Next:** Category analytics dashboard
8. ⏳ **Next:** Export functionality (CSV, PDF reports)
9. ⏳ **Next:** Advanced filtering and search within categories
