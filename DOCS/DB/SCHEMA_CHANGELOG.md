# Database Schema Changelog

## Version 1.1.0 - Enhanced AI Analysis (May 6, 2026)

### MongoDB: `analyzed_posts` Collection

#### Added Fields

**Relevance Filtering**:
- `relevance` (object) - Complete relevance assessment
  - `is_relevant` (boolean)
  - `relevance_score` (double)
  - `matched_keywords` (array)
  - `filter_reason` (string)
  - `is_noise` (boolean)
  - `language_match` (boolean)

**Enhanced Anonymizer**:
- `pii_redaction_map` (object) - Mapping for potential reversal
- `anonymizer_confidence` (double) - Confidence score

**Enhanced Entity Extraction**:
- `entities.drugs[]` - Added: `generic_name`, `brand_name`, `route`, `context`
- `entities.symptoms[]` - Added: `onset`, `duration`, `context`
- `entities.conditions[]` - Added: `icd_code`, `context`
- `entities.procedures[]` - New array for medical procedures
- `entity_extraction_confidence` (double)

**Enhanced Sentiment**:
- `sentiment.emotion_scores` (object) - Individual emotion scores
- `sentiment.context` (string) - Sentiment context explanation
- `sentiment.is_patient_experience` (boolean)

**Enhanced Virality**:
- `virality.velocity` (double) - Engagement growth rate
- `virality.similar_posts_count` (int)
- `virality.is_trending` (boolean)

**Enhanced Safety Audit**:
- `safety_audit.risk_category` (enum) - 5-level risk classification
- `safety_audit.medical_database_match` (boolean)
- `safety_audit.fda_label_check` (boolean)
- `safety_audit.similar_reports_count` (int)

**AI Interpretation** (NEW):
- `ai_interpretation` (object)
  - `summary` (string) - Human-readable summary
  - `key_findings` (array) - Key findings list
  - `clinical_significance` (string)
  - `recommended_action` (enum) - monitor, investigate, escalate, archive, ignore
  - `action_rationale` (string)
  - `suggested_tags` (array)
  - `related_signals` (array)
  - `confidence_overall` (double)

**Classification**:
- `signal_type` - Added: `treatment_efficacy`, `drug_interaction`, `off_label_use`, `noise`
- `signal_priority` - Added: `filtered_out`
- `should_escalate` (boolean) - Escalation flag
- `escalation_reason` (string)

**Agent Pipeline**:
- `agent_pipeline.relevance_filter` (object) - New agent tracking
- `agent_pipeline.interpreter` (object) - New agent tracking
- Added `model_used` field to all agents

#### New Indexes

```javascript
db.analyzed_posts.createIndex({ "relevance.is_relevant": 1 });
db.analyzed_posts.createIndex({ "relevance.is_noise": 1 });
db.analyzed_posts.createIndex({ "ai_interpretation.recommended_action": 1 });
db.analyzed_posts.createIndex({ should_escalate: 1 });
db.analyzed_posts.createIndex({ "virality.is_trending": 1 });
```

---

### PostgreSQL: `safety_signals` Table

#### Added Columns

**AI Analysis**:
- `ai_summary` TEXT - Concise AI-generated summary
- `key_findings` TEXT[] - Array of key findings
- `clinical_significance` TEXT
- `recommended_action` VARCHAR(50)
- `action_rationale` TEXT

**Risk Assessment**:
- `risk_category` VARCHAR(50)
- `known_side_effect` BOOLEAN
- `fda_label_match` BOOLEAN
- `similar_reports_count` INTEGER

**Patient Impact**:
- `patient_impact_score` DECIMAL(3,2)
- `quality_of_life_impact` VARCHAR(50)

**Status & Assignment**:
- `escalated_at` TIMESTAMP
- `escalation_reason` TEXT

**Tags & Classification**:
- `tags` TEXT[] - User or AI-generated tags
- `categories` TEXT[] - Categorization

**Review & Validation**:
- `reviewed_by` UUID
- `reviewed_at` TIMESTAMP
- `review_notes` TEXT
- `is_validated` BOOLEAN
- `overall_confidence` DECIMAL(3,2)

#### New Indexes

```sql
CREATE INDEX idx_signals_risk_category ON safety_signals(risk_category);
CREATE INDEX idx_signals_recommended_action ON safety_signals(recommended_action);
CREATE INDEX idx_signals_validated ON safety_signals(is_validated);
CREATE INDEX idx_signals_tags ON safety_signals USING GIN(tags);
CREATE INDEX idx_signals_categories ON safety_signals USING GIN(categories);
```

---

### PostgreSQL: New Table `filtered_posts`

**Purpose**: Track posts that were filtered out for analytics and model improvement.

```sql
CREATE TABLE filtered_posts (
    id UUID PRIMARY KEY,
    project_id UUID,
    search_execution_id UUID,
    mongodb_post_id TEXT,
    filter_reason VARCHAR(255),
    relevance_score DECIMAL(3,2),
    is_noise BOOLEAN,
    is_spam BOOLEAN,
    matched_keywords TEXT[],
    language_detected VARCHAR(10),
    ai_explanation TEXT,
    confidence DECIMAL(3,2),
    filtered_at TIMESTAMP,
    created_at TIMESTAMP
);
```

---

## Version 1.0.0 - Initial Schema (May 6, 2026)

### PostgreSQL Tables Created
- `users` - User authentication
- `projects` - Monitoring projects
- `keywords` - Keywords to monitor
- `data_sources` - Social media sources
- `search_executions` - Search tracking
- `safety_signals` - High-value signals
- `reports` - Generated reports
- `audit_logs` - Audit trail

### MongoDB Collections Created
- `raw_pages` - Raw HTML/page data
- `raw_posts` - Extracted posts
- `analyzed_posts` - AI-processed posts
- `agent_traces` - Execution traces

---

## Migration Notes

### From 1.0.0 to 1.1.0

**MongoDB**:
- No breaking changes
- All new fields are optional
- Existing documents remain valid
- Update application code to populate new fields

**PostgreSQL**:
- Run migration script to add new columns
- New `filtered_posts` table created
- Existing data remains intact
- Update queries to use new indexes

### Migration Script

```sql
-- Add new columns to safety_signals
ALTER TABLE safety_signals 
ADD COLUMN ai_summary TEXT,
ADD COLUMN key_findings TEXT[],
ADD COLUMN clinical_significance TEXT,
ADD COLUMN recommended_action VARCHAR(50),
ADD COLUMN action_rationale TEXT,
ADD COLUMN risk_category VARCHAR(50),
ADD COLUMN known_side_effect BOOLEAN DEFAULT false,
ADD COLUMN fda_label_match BOOLEAN DEFAULT false,
ADD COLUMN similar_reports_count INTEGER DEFAULT 0,
ADD COLUMN patient_impact_score DECIMAL(3,2),
ADD COLUMN quality_of_life_impact VARCHAR(50),
ADD COLUMN escalated_at TIMESTAMP,
ADD COLUMN escalation_reason TEXT,
ADD COLUMN tags TEXT[],
ADD COLUMN categories TEXT[],
ADD COLUMN reviewed_by UUID,
ADD COLUMN reviewed_at TIMESTAMP,
ADD COLUMN review_notes TEXT,
ADD COLUMN is_validated BOOLEAN DEFAULT false,
ADD COLUMN overall_confidence DECIMAL(3,2);

-- Create new indexes
CREATE INDEX idx_signals_risk_category ON safety_signals(risk_category);
CREATE INDEX idx_signals_recommended_action ON safety_signals(recommended_action);
CREATE INDEX idx_signals_validated ON safety_signals(is_validated);
CREATE INDEX idx_signals_tags ON safety_signals USING GIN(tags);
CREATE INDEX idx_signals_categories ON safety_signals USING GIN(categories);

-- Create filtered_posts table
-- (See schema.sql for full definition)
```

---

## Upcoming Features (Roadmap)

### Version 1.2.0 (Planned)
- Multimodal analysis (images, videos)
- Drug interaction detection
- Temporal pattern analysis
- Automated report generation
- Integration with external medical databases

### Version 1.3.0 (Planned)
- Real-time alerting system
- Advanced NLP for medical terminology
- Predictive analytics
- Enhanced visualization data

---

**Last Updated**: May 6, 2026
