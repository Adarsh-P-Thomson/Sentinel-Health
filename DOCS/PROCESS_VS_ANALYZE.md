# Process vs Analyze - Two-Step Workflow

## Overview

The system now has a **two-step workflow** for handling search results:

1. **PROCESS** = Clean & Anonymize (NO AI)
2. **ANALYZE** = Send to AI Agents for Analysis

---

## Step 1: PROCESS (Clean & Anonymize)

**Button:** "Clean & Anonymize Data"  
**Endpoint:** `POST /api/v1/clean/latest`  
**Service:** `CleaningService`  
**Agent Used:** `Anonymizer Agent` (from `Backend/app/agents/anonymizer.py`)

### What It Does:
1. Finds latest unprocessed search results (`processing_status = "pending"`)
2. Cleans text using `text_cleaner.py`:
   - Removes formatting (\n, ???, +++, etc.)
   - Normalizes whitespace
   - Cleans URLs, emails, phones
3. Anonymizes PII/PHI using `anonymizer.py` (LOCAL regex, NO AI):
   - Removes emails, phones, SSN, dates
   - Removes addresses, ZIP codes, names
   - Removes locations, MRN, insurance IDs
4. Stores in `cleaned_posts` collection
5. Marks raw posts as `processing_status = "cleaned"`

### MongoDB Collections:
- **Input:** `raw_posts` (status: "pending")
- **Output:** `cleaned_posts` (status: "pending" for AI analysis)
- **Update:** `raw_posts` (status: "cleaned")

### NO AI CALLS - Completely Local Processing

---

## Step 2: ANALYZE (AI Analysis)

**Button:** "Analyze with AI"  
**Endpoint:** `POST /api/v1/analyze/latest`  
**Service:** `AnalysisService` + LangGraph Workflow  
**Agents Used:** ALL AI agents

### What It Does:
1. Finds cleaned posts (`ai_analysis_status = "pending"`)
2. Sends through LangGraph multi-agent workflow:
   - **Medical Entity Extractor** - Identifies drugs, dosages, symptoms
   - **Sentiment Analyst** - Evaluates emotional tone
   - **Trend & Virality Agent** - Checks engagement metrics
   - **Safety Auditor** - Verifies symptoms against known side effects
3. Stores results in `processed_categories` collection
4. Marks cleaned posts as `ai_analysis_status = "analyzed"`

### MongoDB Collections:
- **Input:** `cleaned_posts` (status: "pending")
- **Output:** `processed_categories` (categorized AI insights)
- **Update:** `cleaned_posts` (status: "analyzed")

### USES AZURE OPENAI - AI Analysis

---

## Frontend Flow

### Suggestions Page (`Frontend/app/suggestions/page.tsx`)

```
┌─────────────────────────────────────┐
│  Step 1: Process Data               │
│  ┌───────────────────────────────┐  │
│  │ Clean & Anonymize Data        │  │
│  │ (Purple Button)               │  │
│  └───────────────────────────────┘  │
│  Removes PII/PHI, normalizes text   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Step 2: Analyze with AI            │
│  ┌───────────────────────────────┐  │
│  │ Analyze with AI               │  │
│  │ (Sky Blue Button)             │  │
│  └───────────────────────────────┘  │
│  Sends to AI agents for analysis    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  View Categories                    │
│  - Medicine, Hospital, Drug, etc.   │
│  - AI Suggestions & Info            │
│  - Sentiment & Severity             │
└─────────────────────────────────────┘
```

---

## API Endpoints

### Process Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/clean/latest` | POST | Clean & anonymize latest unprocessed data |
| `/api/v1/process/latest` | POST | DEPRECATED - Use /clean/latest |

### Analyze Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze/latest` | POST | Analyze cleaned posts with AI agents |
| `/api/v1/analyze` | POST | Analyze single post with mission parameters |

### View Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/categories` | GET | List all processed categories |
| `/api/v1/categories/{name}` | GET | Get category details with AI insights |

---

## Data Flow

```
Search Results
      ↓
┌─────────────────┐
│   raw_posts     │ ← Search results stored here
│ status: pending │
└─────────────────┘
      ↓
   [PROCESS]  ← Clean & Anonymize (NO AI)
      ↓
┌─────────────────┐
│ cleaned_posts   │ ← Cleaned data stored here
│ status: pending │
└─────────────────┘
      ↓
   [ANALYZE]  ← Send to AI Agents
      ↓
┌──────────────────────┐
│ processed_categories │ ← AI insights stored here
│ - Medicine           │
│ - Hospital           │
│ - Drug               │
│ - Condition          │
│ - Symptom            │
└──────────────────────┘
```

---

## Why Two Steps?

### Privacy & Cost
- **PROCESS** is free (local regex)
- **ANALYZE** costs money (Azure OpenAI API calls)
- User can review cleaned data before sending to AI

### Control
- User decides WHEN to send data to AI
- Can clean 1000 posts, then analyze only 100
- Prevents accidental AI costs

### Compliance
- PII/PHI removed BEFORE sending to AI
- Meets HIPAA requirements
- Audit trail: raw → cleaned → analyzed

---

## Example Usage

### 1. Run Search
```bash
POST /api/v1/search
{
  "query": "Lisinopril side effects",
  "sources": ["reddit_json"],
  "limit": 100
}
```

### 2. Clean Data (PROCESS)
```bash
POST /api/v1/clean/latest
```

Response:
```json
{
  "message": "Cleaned 100 posts",
  "search_execution_id": "abc-123",
  "status": "completed",
  "total_cleaned": 100
}
```

### 3. Analyze with AI (ANALYZE)
```bash
POST /api/v1/analyze/latest
```

Response:
```json
{
  "message": "Started AI analysis for 100 posts",
  "status": "started",
  "total_posts": 100
}
```

### 4. View Results
```bash
GET /api/v1/categories?category_type=medicine
```

---

## Next Steps

1. ✅ PROCESS button implemented
2. ✅ ANALYZE button implemented
3. ⏳ **TODO:** Implement batch processing for ANALYZE
4. ⏳ **TODO:** Add progress tracking for AI analysis
5. ⏳ **TODO:** Show cleaned post count before analyzing
6. ⏳ **TODO:** Add cost estimation before AI analysis
