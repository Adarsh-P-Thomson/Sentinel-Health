# AI Analysis Fields - Comprehensive Guide

## Overview

This document details all AI-generated fields stored in the database for each analyzed post. The multi-agent system processes each post through specialized agents, with each agent contributing specific analysis fields.

---

## Agent Pipeline Flow

```
Raw Post
    ↓
[1] Relevance Filter → Filter out noise/irrelevant posts
    ↓
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

---

## 1. Relevance Filter

**Purpose**: Filter out noise, spam, and irrelevant posts before expensive AI processing.

### Fields (MongoDB: `analyzed_posts.relevance`)

```javascript
relevance: {
  is_relevant: true,              // Boolean: Pass/fail filter
  relevance_score: 0.87,          // 0.0-1.0: Relevance to project keywords
  matched_keywords: [             // Keywords that matched
    "Drug-Y",
    "headache",
    "side effect"
  ],
  filter_reason: null,            // Reason if filtered out
  is_noise: false,                // Flagged as noise/spam
  language_match: true            // Language matches project requirements
}
```

### Filtering Logic

- **is_relevant = false** → Post is stored in PostgreSQL `filtered_posts` table
- **is_noise = true** → Marked as spam/noise
- **relevance_score < 0.5** → Low relevance, may be filtered

### PostgreSQL: `filtered_posts` Table

Tracks all filtered-out posts for analytics:

```sql
SELECT 
    filter_reason,
    COUNT(*) as count,
    AVG(relevance_score) as avg_score
FROM filtered_posts
WHERE project_id = 'project-uuid'
GROUP BY filter_reason;
```

---

## 2. Anonymizer Agent

**Purpose**: Remove PII/PHI to ensure HIPAA compliance.

### Fields (MongoDB: `analyzed_posts`)

```javascript
{
  anonymized_content: "I've been taking [DRUG] and experiencing [SYMPTOM]...",
  pii_detected: true,
  pii_types: ["name", "location", "email"],
  pii_redaction_map: {
    "[NAME_1]": "John Smith",
    "[LOCATION_1]": "New York"
  },
  anonymizer_confidence: 0.95
}
```

### PII Types Detected

- `name` - Person names
- `email` - Email addresses
- `phone` - Phone numbers
- `location` - Geographic locations
- `ssn` - Social Security Numbers
- `medical_record_number` - MRN
- `date_of_birth` - DOB
- `ip_address` - IP addresses

### Redaction Map

The `pii_redaction_map` allows potential reversal for authorized users (stored encrypted).

---

## 3. Medical Entity Extractor

**Purpose**: Extract structured medical information from unstructured text.

### Fields (MongoDB: `analyzed_posts.entities`)

```javascript
entities: {
  drugs: [
    {
      name: "Drug-Y",
      generic_name: "generic-drug-y",
      brand_name: "Brand-Y",
      dosage: "50mg",
      frequency: "twice daily",
      duration: "2 weeks",
      route: "oral",
      confidence: 0.95,
      context: "I've been taking Drug-Y 50mg twice daily"
    }
  ],
  symptoms: [
    {
      name: "severe headaches",
      severity: "severe",
      onset: "after 2 weeks",
      duration: "ongoing",
      confidence: 0.89,
      context: "experiencing severe headaches"
    }
  ],
  conditions: [
    {
      name: "migraine",
      icd_code: "G43.909",
      confidence: 0.72,
      context: "diagnosed with migraine"
    }
  ],
  procedures: [
    {
      name: "MRI scan",
      confidence: 0.85
    }
  ]
}
```

### Severity Levels

- `mild` - Minor discomfort
- `moderate` - Noticeable impact
- `severe` - Significant impact on daily life
- `critical` - Life-threatening or emergency

---

## 4. Sentiment Analyst

**Purpose**: Understand emotional tone and patient experience context.

### Fields (MongoDB: `analyzed_posts.sentiment`)

```javascript
sentiment: {
  overall: "negative",
  score: -0.75,                   // -1.0 (very negative) to 1.0 (very positive)
  emotions: [
    "frustration",
    "concern",
    "fear"
  ],
  emotion_scores: {
    frustration: 0.82,
    concern: 0.71,
    fear: 0.45,
    anger: 0.23
  },
  confidence: 0.88,
  context: "frustration with side effect",
  is_patient_experience: true     // First-hand vs. second-hand report
}
```

### Sentiment Classifications

- `very_negative` - Severe dissatisfaction/distress
- `negative` - Dissatisfaction/concern
- `neutral` - Factual reporting
- `positive` - Satisfaction
- `very_positive` - High satisfaction

### Context Types

- `frustration with side effect` - Patient frustrated with adverse event
- `general dissatisfaction` - Overall treatment dissatisfaction
- `concern for safety` - Safety concerns
- `positive outcome` - Treatment success
- `seeking advice` - Information seeking

---

## 5. Trend & Virality Agent

**Purpose**: Assess engagement metrics and viral potential.

### Fields (MongoDB: `analyzed_posts.virality`)

```javascript
virality: {
  score: 78.5,                    // 0-100: Virality score
  trend: "rising",
  engagement_rate: 0.15,          // (likes+shares+comments) / views
  viral_potential: "high",
  velocity: 12.5,                 // Engagement growth rate
  similar_posts_count: 47,        // Similar posts in timeframe
  is_trending: true
}
```

### Trend Classifications

- `viral` - Exponential growth, widespread attention
- `rising` - Increasing engagement
- `stable` - Consistent engagement
- `declining` - Decreasing engagement

### Viral Potential

- `low` - Limited spread expected
- `medium` - Moderate spread possible
- `high` - High likelihood of going viral
- `critical` - Already viral or imminent

---

## 6. Safety Auditor

**Purpose**: Verify against medical databases and assess risk.

### Fields (MongoDB: `analyzed_posts.safety_audit`)

```javascript
safety_audit: {
  is_adverse_event: true,
  severity: "high",
  known_side_effect: false,       // Not in FDA label
  requires_investigation: true,
  confidence: 0.91,
  risk_category: "high_risk",
  medical_database_match: true,   // Checked against knowledge base
  fda_label_check: true,          // Checked against FDA labels
  similar_reports_count: 23       // Similar AE reports found
}
```

### Risk Categories

- `no_risk` - No safety concern
- `low_risk` - Minor, known side effect
- `moderate_risk` - Moderate concern, monitoring needed
- `high_risk` - Serious concern, investigation needed
- `critical_risk` - Life-threatening, immediate action

### Database Checks

- **medical_database_match**: Checked against medical knowledge bases (e.g., SIDER, DrugBank)
- **fda_label_check**: Verified against FDA drug labels
- **similar_reports_count**: Number of similar reports in FAERS or internal database

---

## 7. AI Interpreter

**Purpose**: Generate human-readable summary and actionable recommendations.

### Fields (MongoDB: `analyzed_posts.ai_interpretation`)

```javascript
ai_interpretation: {
  summary: "Patient reports severe headaches after 2 weeks of Drug-Y 50mg twice daily. Symptom not listed in FDA label.",
  
  key_findings: [
    "Unlisted adverse event: severe headaches",
    "Symptom onset after 2 weeks of treatment",
    "23 similar reports found in database",
    "High engagement suggests widespread concern"
  ],
  
  clinical_significance: "Potential new safety signal. Severe headaches not documented in FDA label for Drug-Y. Pattern suggests possible causal relationship.",
  
  recommended_action: "escalate",
  
  action_rationale: "Unknown side effect with high severity and multiple similar reports warrants immediate investigation and potential FDA reporting.",
  
  suggested_tags: [
    "neurological",
    "unlisted-side-effect",
    "requires-investigation"
  ],
  
  related_signals: [
    "signal-uuid-1",
    "signal-uuid-2"
  ],
  
  confidence_overall: 0.87
}
```

### Recommended Actions

| Action | Description | Typical Use Case |
|--------|-------------|------------------|
| `ignore` | No action needed | Noise, spam, irrelevant |
| `monitor` | Track for patterns | Low-severity, known side effect |
| `investigate` | Requires analysis | Moderate concern, unclear pattern |
| `escalate` | Immediate attention | High-severity, unknown side effect |
| `archive` | Store for reference | Resolved or validated signal |

---

## 8. Classification & Filtering

### Signal Types

```javascript
signal_type: "adverse_event"
```

Options:
- `adverse_event` - Drug side effect or adverse reaction
- `quality_issue` - Product quality concern
- `sentiment_spike` - Sudden sentiment change
- `treatment_efficacy` - Treatment effectiveness report
- `drug_interaction` - Interaction between drugs
- `off_label_use` - Off-label usage report
- `noise` - Filtered as irrelevant

### Signal Priority

```javascript
signal_priority: "high"
```

Options:
- `critical` - Immediate action required
- `high` - Urgent attention needed
- `medium` - Standard review
- `low` - Monitor only
- `filtered_out` - Removed from analysis

### Escalation

```javascript
should_escalate: true
escalation_reason: "Unknown severe adverse event with multiple reports"
```

---

## 9. Agent Pipeline Metadata

**Purpose**: Track execution details for each agent.

### Fields (MongoDB: `analyzed_posts.agent_pipeline`)

```javascript
agent_pipeline: {
  anonymizer: {
    status: "completed",
    duration_ms: 120,
    model_used: "presidio-analyzer",
    error: null
  },
  relevance_filter: {
    status: "completed",
    duration_ms: 85,
    model_used: "gpt-4-turbo"
  },
  extractor: {
    status: "completed",
    duration_ms: 450,
    model_used: "gpt-4"
  },
  sentiment: {
    status: "completed",
    duration_ms: 200,
    model_used: "gpt-4"
  },
  trend: {
    status: "completed",
    duration_ms: 180,
    model_used: "custom-algorithm"
  },
  auditor: {
    status: "completed",
    duration_ms: 350,
    model_used: "gpt-4"
  },
  interpreter: {
    status: "completed",
    duration_ms: 280,
    model_used: "gpt-4"
  }
}
```

### Status Values

- `completed` - Agent executed successfully
- `failed` - Agent execution failed
- `skipped` - Agent skipped (e.g., filtered post)

---

## PostgreSQL: Aggregated Signals

High-value signals are aggregated and archived to PostgreSQL `safety_signals` table.

### Additional PostgreSQL Fields

```sql
-- AI Analysis Summary
ai_summary TEXT,
key_findings TEXT[],
clinical_significance TEXT,
recommended_action VARCHAR(50),
action_rationale TEXT,

-- Risk Assessment
risk_category VARCHAR(50),
known_side_effect BOOLEAN,
fda_label_match BOOLEAN,
similar_reports_count INTEGER,

-- Patient Impact
patient_impact_score DECIMAL(3,2),
quality_of_life_impact VARCHAR(50),

-- Tags & Classification
tags TEXT[],
categories TEXT[],

-- Review & Validation
reviewed_by UUID,
reviewed_at TIMESTAMP,
review_notes TEXT,
is_validated BOOLEAN
```

---

## Query Examples

### Find High-Priority Unreviewed Signals

```sql
SELECT 
    id,
    drug_name,
    symptom,
    severity,
    ai_summary,
    recommended_action
FROM safety_signals
WHERE signal_priority IN ('high', 'critical')
  AND is_validated = false
  AND status = 'new'
ORDER BY first_detected_at DESC;
```

### Find Posts Requiring Escalation

```javascript
db.analyzed_posts.find({
  should_escalate: true,
  archived_to_postgres: false
}).sort({ processed_at: -1 });
```

### Analyze Filtering Patterns

```sql
SELECT 
    filter_reason,
    COUNT(*) as count,
    AVG(relevance_score) as avg_relevance,
    AVG(confidence) as avg_confidence
FROM filtered_posts
WHERE project_id = 'project-uuid'
  AND filtered_at > NOW() - INTERVAL '7 days'
GROUP BY filter_reason
ORDER BY count DESC;
```

---

## Best Practices

1. **Always check `relevance.is_relevant`** before expensive AI processing
2. **Store `pii_redaction_map` encrypted** for compliance
3. **Use `confidence_overall`** to filter low-confidence results
4. **Track `agent_pipeline` metadata** for debugging and optimization
5. **Archive high-value signals** to PostgreSQL for permanent storage
6. **Use `langsmith_trace_id`** for full execution traceability
7. **Monitor `filtered_posts`** to improve relevance filtering

---

**Last Updated**: May 6, 2026
