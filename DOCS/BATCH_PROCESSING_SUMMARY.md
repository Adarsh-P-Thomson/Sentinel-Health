# Batch Processing System - Complete Summary

## ✅ What Was Built

### 1. MongoDB Collections
- **`processing_batches`** - Tracks batch status (pending → processing → completed)
- **`processed_categories`** - Stores categorized AI-processed content

### 2. Batch Processor Service (`app/services/batch_processor.py`)
- Creates batches with 8000 char limit (~2000 tokens)
- Processes with Azure OpenAI
- Categorizes results (medicine, hospital, drug, etc.)
- Tracks progress and marks as done

### 3. API Endpoints (`app/api/process.py`)
- `POST /api/v1/process/search` - Process all posts from search
- `POST /api/v1/process/batch` - Process single batch
- `GET /api/v1/process/batch/{id}/status` - Check batch status
- `GET /api/v1/categories` - List all categories
- `GET /api/v1/categories/{name}` - Get category details

### 4. Categorization System
AI extracts for each post:
- **category_name**: "Ibuprofen", "Mayo Clinic", "Diabetes"
- **category_type**: medicine, hospital, drug, condition, symptom, procedure, general
- **processed_text**: Clean summary
- **ai_suggestion**: Actionable recommendation
- **ai_info**: Additional context
- **sentiment**: very_negative → very_positive
- **severity**: low, medium, high, critical
- **is_adverse_event**: true/false

---

## 🎯 How It Works

```
1. Search → Raw Posts (100 posts)
              ↓
2. Create Batches (5 batches of ~20 posts each, 8000 chars max)
              ↓
3. Process Each Batch:
   - Clean & Anonymize (local, no AI)
   - Send to Azure OpenAI
   - Extract categories
   - Store in processed_categories
   - Mark batch as "completed"
              ↓
4. Results Organized by Category:
   - Ibuprofen (medicine): 45 entries
   - Lisinopril (medicine): 30 entries
   - Mayo Clinic (hospital): 5 entries
   - Headache (symptom): 60 entries
```

---

## 📊 Data Structure

### Processed Categories Collection

```javascript
{
  "category_name": "Ibuprofen",
  "category_type": "medicine",
  "processed_entries": [
    {
      "entry_id": "uuid-1",
      "original_post_id": ObjectId("..."),
      "batch_id": "batch-uuid",
      "processed_text": "Patient reports severe stomach pain after taking Ibuprofen 200mg three times daily.",
      "ai_suggestion": "Consider switching to acetaminophen or consulting gastroenterologist.",
      "ai_info": "Ibuprofen is an NSAID that can cause gastrointestinal issues.",
      "sentiment": "negative",
      "severity": "medium",
      "is_adverse_event": true,
      "processed_at": "2026-05-07T10:00:00Z"
    }
    // More entries keep getting added here
  ],
  "total_entries": 150,
  "tags": ["NSAID", "pain relief"]
}
```

**Key Feature:** Entries are **appended** to existing categories, so "Ibuprofen" category keeps growing as more posts are processed.

---

## 🚀 Usage

### Step 1: Perform Search
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Lisinopril side effects",
    "sources": ["reddit_json"],
    "limit": 100
  }'
```

**Response:** `{ "search_execution_id": "abc-123" }`

### Step 2: Process Results
```bash
curl -X POST "http://localhost:8000/api/v1/process/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_execution_id": "abc-123",
    "background": false
  }'
```

**Response:**
```json
{
  "message": "Batch processing completed",
  "total_batches": 5,
  "status": "completed",
  "batch_ids": ["batch-1", "batch-2", "batch-3", "batch-4", "batch-5"]
}
```

### Step 3: View Categories
```bash
# List all medicine categories
curl "http://localhost:8000/api/v1/categories?category_type=medicine"

# Get Lisinopril details
curl "http://localhost:8000/api/v1/categories/Lisinopril"
```

---

## 🔄 Background Processing

For large searches, use background processing:

```bash
curl -X POST "http://localhost:8000/api/v1/process/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_execution_id": "abc-123",
    "background": true
  }'
```

Returns immediately. Check status:
```bash
curl "http://localhost:8000/api/v1/process/batch/batch-1/status"
```

---

## 📋 Setup Instructions

### 1. Create MongoDB Collections
```bash
mongosh Sentinel_health < DOCS/DB/MONGODB/schema_processed_categories.js
```

### 2. Verify Azure OpenAI Config
Check `Backend/.env`:
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
# 1. Search for posts
# 2. Process with: POST /api/v1/process/search
# 3. View results: GET /api/v1/categories
```

---

## 💰 Cost & Performance

**Per Batch (20 posts, 8000 chars):**
- Processing Time: ~15-30 seconds
- Cost (GPT-4): ~$0.03-0.06
- Cost (GPT-3.5-Turbo): ~$0.002-0.004

**For 100 Posts (5 batches):**
- Total Time: ~2-3 minutes
- Total Cost (GPT-4): ~$0.15-0.30
- Total Cost (GPT-3.5-Turbo): ~$0.01-0.02

**Recommendation:** Use GPT-3.5-Turbo for development, GPT-4 for production.

---

## 🎯 Key Features

1. ✅ **Character Limits** - 8000 chars per batch (~2000 tokens)
2. ✅ **Automatic Categorization** - AI extracts category name and type
3. ✅ **Incremental Storage** - Categories keep growing as posts are added
4. ✅ **Progress Tracking** - Batch status (pending → processing → completed)
5. ✅ **Background Processing** - Process large searches asynchronously
6. ✅ **Privacy-First** - PII/PHI removed locally before AI processing
7. ✅ **Structured Output** - AI returns consistent JSON format

---

## 📚 Documentation

- **Full Guide:** `DOCS/BATCH_PROCESSING.md`
- **MongoDB Schema:** `DOCS/DB/MONGODB/schema_processed_categories.js`
- **API Docs:** http://localhost:8000/docs (after starting backend)

---

## ✅ Ready to Use!

1. Create MongoDB collections
2. Add Azure OpenAI credentials
3. Start backend
4. Search → Process → View Categories

**All batch processing is ready to go!** 🚀
