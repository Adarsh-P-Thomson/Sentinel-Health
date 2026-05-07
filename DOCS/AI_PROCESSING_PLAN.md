# AI Processing Pipeline - Implementation Plan

## Current State Analysis

### ✅ What's Already Done:
1. **Agent Structure** - 5 specialized agents created:
   - `anonymizer.py` - PII/PHI removal (placeholder logic)
   - `extractor.py` - Medical entity extraction (Groq LLM)
   - `sentiment.py` - Emotional tone analysis (Groq LLM)
   - `trend.py` - Virality/engagement analysis (Groq LLM)
   - `auditor.py` - Safety verification (Groq LLM)

2. **LangGraph Workflow** - Sequential pipeline defined:
   - Flow: Anonymizer → Extractor → Sentiment → Trend → Auditor → END
   - State management with `AgentState` TypedDict
   - Compiled workflow ready to use

3. **Schemas** - Pydantic models for structured outputs:
   - `ExtractedEntity`, `MedicalExtractionResult`
   - `SentimentResult`, `TrendResult`, `AuditResult`

4. **API Endpoint** - `/api/v1/analyze` endpoint exists
   - Takes `MissionParameterRequest` (keyword, source, raw_text)
   - Returns `AnalysisResponse`

5. **MongoDB Schema** - `analyzed_posts` collection defined with all fields

### ❌ What's Missing:

1. **No batch processing** - Current system processes ONE post at a time
2. **No integration with search** - Search stores raw_posts, but nothing triggers AI processing
3. **Agents need updates**:
   - Anonymizer uses placeholder logic (needs Presidio or better LLM)
   - Extractor schema doesn't match MongoDB (needs drugs array with dosage, symptoms with severity)
   - Sentiment schema doesn't match MongoDB (needs overall enum, emotions array)
   - Trend needs actual engagement metrics from raw_posts
   - Auditor schema doesn't match MongoDB (needs is_adverse_event, severity enum)
4. **No storage** - Agents don't save results to MongoDB `analyzed_posts`
5. **No background processing** - Should process posts asynchronously
6. **No API key** - GROQ_API_KEY not in .env

---

## Implementation Plan

### Phase 1: Fix Agent Schemas & Logic (Priority: HIGH)

**Goal:** Make agent outputs match MongoDB `analyzed_posts` schema

#### 1.1 Update Extractor Agent
- Change output schema to match MongoDB:
  ```python
  drugs: [{ name, generic_name, brand_name, dosage, frequency, duration, route, confidence, context }]
  symptoms: [{ name, severity: "mild|moderate|severe|critical", onset, duration, confidence, context }]
  conditions: [{ name, icd_code, confidence, context }]
  procedures: [{ name, confidence }]
  ```
- Update LLM prompt to extract detailed drug/symptom info

#### 1.2 Update Sentiment Agent
- Change output schema:
  ```python
  overall: "very_negative|negative|neutral|positive|very_positive"
  score: float (-1.0 to 1.0)
  emotions: List[str]
  emotion_scores: Dict[str, float]
  confidence: float
  context: str
  is_patient_experience: bool
  ```

#### 1.3 Update Trend Agent
- Use actual engagement metrics from raw_posts:
  ```python
  score: float (0-100)
  trend: "rising|stable|declining|viral"
  engagement_rate: float
  viral_potential: "low|medium|high|critical"
  velocity: float
  similar_posts_count: int
  is_trending: bool
  ```
- Calculate from likes, shares, comments, views

#### 1.4 Update Auditor Agent
- Change output schema:
  ```python
  is_adverse_event: bool
  severity: "low|medium|high|critical"
  known_side_effect: bool
  requires_investigation: bool
  confidence: float
  risk_category: "no_risk|low_risk|moderate_risk|high_risk|critical_risk"
  ```

#### 1.5 Improve Anonymizer Agent
- Options:
  - **Option A:** Use Presidio (Microsoft's PII detection library)
  - **Option B:** Use LLM-based anonymization (Groq/OpenAI)
  - **Option C:** Simple regex patterns for now (names, emails, phones, locations)
- Output:
  ```python
  anonymized_content: str
  pii_detected: bool
  pii_types: List[str]
  pii_redaction_map: Dict
  anonymizer_confidence: float
  ```

---

### Phase 2: Create Processing Service (Priority: HIGH)

**Goal:** Process raw_posts and store results in analyzed_posts

#### 2.1 Create `app/services/post_processor.py`
```python
async def process_raw_post(raw_post_id: str, project_id: str):
    """
    Process a single raw post through the AI pipeline
    
    Steps:
    1. Fetch raw_post from MongoDB
    2. Run through LangGraph workflow
    3. Store result in analyzed_posts
    4. Update raw_post.processing_status = "completed"
    """
```

#### 2.2 Create Batch Processor
```python
async def process_search_execution(search_execution_id: str):
    """
    Process all raw_posts from a search execution
    
    Steps:
    1. Query raw_posts where search_execution_id matches
    2. Filter: processing_status = "pending"
    3. Process each post (with rate limiting)
    4. Update search_execution status in PostgreSQL
    """
```

---

### Phase 3: API Endpoints (Priority: MEDIUM)

#### 3.1 Create `/api/v1/process` endpoint
```python
POST /api/v1/process/search/{search_execution_id}
- Triggers batch processing for all posts in a search
- Returns: { "status": "processing", "total_posts": 50 }
```

#### 3.2 Create `/api/v1/process/post/{post_id}` endpoint
```python
POST /api/v1/process/post/{post_id}
- Process a single post
- Returns: analyzed_post result
```

#### 3.3 Update `/api/v1/search` endpoint
```python
- Add optional parameter: auto_process=true
- If true, automatically trigger AI processing after search completes
```

---

### Phase 4: Background Processing (Priority: LOW)

**Goal:** Process posts asynchronously without blocking API

#### 4.1 Options:
- **Option A:** Celery + Redis (full task queue)
- **Option B:** FastAPI BackgroundTasks (simple, built-in)
- **Option C:** asyncio.create_task() (simplest)

#### 4.2 Implementation (Option B - Recommended)
```python
from fastapi import BackgroundTasks

@router.post("/search")
async def search(request: SearchRequest, background_tasks: BackgroundTasks):
    # ... perform search ...
    
    if request.auto_process:
        background_tasks.add_task(process_search_execution, search_execution_id)
    
    return result
```

---

### Phase 5: Configuration & Setup (Priority: HIGH)

#### 5.1 Add GROQ API Key to .env
```bash
GROQ_API_KEY=your_groq_api_key_here
```

#### 5.2 Alternative: Use OpenAI instead
```bash
OPENAI_API_KEY=your_openai_key
```
- Update agents to use `ChatOpenAI` instead of `ChatGroq`

#### 5.3 Add LangSmith (Optional - for debugging)
```bash
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=sentinel-health-dev
```

---

## Recommended Implementation Order

### Week 1: Core Processing
1. ✅ Add GROQ_API_KEY to .env
2. ✅ Fix all agent schemas to match MongoDB
3. ✅ Test each agent individually
4. ✅ Create `post_processor.py` service
5. ✅ Test end-to-end: raw_post → analyzed_post

### Week 2: Integration
6. ✅ Create `/api/v1/process` endpoints
7. ✅ Integrate with search endpoint
8. ✅ Add background processing
9. ✅ Test full flow: search → store → process → analyze

### Week 3: Polish
10. ✅ Add error handling & retries
11. ✅ Add progress tracking
12. ✅ Add rate limiting for LLM calls
13. ✅ Frontend integration (display analyzed results)

---

## Key Decisions Needed

### 1. LLM Provider
- **Groq** (current): Fast, cheap, good for development
- **OpenAI**: More accurate, better for production
- **Anthropic Claude**: Best for medical/safety analysis

### 2. Anonymization Strategy
- **Presidio**: Most accurate, requires installation
- **LLM-based**: Flexible, costs API calls
- **Regex**: Fast, cheap, less accurate

### 3. Processing Trigger
- **Manual**: User clicks "Process" button
- **Auto**: Automatically process after search
- **Scheduled**: Batch process every X minutes

### 4. Background Processing
- **BackgroundTasks**: Simple, good for < 100 posts
- **Celery**: Complex, good for > 1000 posts
- **None**: Synchronous (blocks API)

---

## Next Steps

**Immediate Actions:**
1. Get GROQ API key (or OpenAI key)
2. Decide on anonymization strategy
3. Fix agent schemas (1-2 hours)
4. Create post_processor service (2-3 hours)
5. Test with real Reddit data

**Questions for You:**
1. Do you have a GROQ API key? (Free tier available)
2. Should we process posts automatically after search, or manually?
3. Do you want to use Presidio for anonymization, or keep it simple for now?
4. Should we process replies/comments too, or just main posts?
