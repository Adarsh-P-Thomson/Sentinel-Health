// Sentinel Health - MongoDB Schema
// Version: 1.0
// Description: Unstructured data for raw posts, AI analysis, and agent traces

// ============================================================================
// DATABASE SETUP
// ============================================================================

use Sentinel_health;

// ============================================================================
// COLLECTION: raw_pages
// Purpose: Raw page data (HTML, links, metadata) from web scraping
// ============================================================================

db.createCollection("raw_pages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["search_execution_id", "url", "fetched_at"],
      properties: {
        search_execution_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL search_executions.id"
        },
        project_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL projects.id"
        },
        source_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL data_sources.id"
        },
        
        // Page identification
        url: {
          bsonType: "string",
          description: "Full URL of the page"
        },
        url_hash: {
          bsonType: "string",
          description: "Hash of URL for deduplication"
        },
        canonical_url: {
          bsonType: "string",
          description: "Canonical URL if different from fetched URL"
        },
        
        // Raw content
        html_content: {
          bsonType: "string",
          description: "Raw HTML content of the page"
        },
        text_content: {
          bsonType: "string",
          description: "Extracted text content (no HTML tags)"
        },
        
        // Page metadata
        title: {
          bsonType: "string",
          description: "Page title"
        },
        description: {
          bsonType: "string",
          description: "Meta description"
        },
        author: {
          bsonType: "string",
          description: "Page author if available"
        },
        published_date: {
          bsonType: "date",
          description: "Original publication date if available"
        },
        
        // Links found on page
        links: {
          bsonType: "array",
          description: "All links found on the page",
          items: {
            bsonType: "object",
            properties: {
              href: { bsonType: "string" },
              text: { bsonType: "string" },
              type: { enum: ["internal", "external", "social"] }
            }
          }
        },
        
        // Media found on page
        media: {
          bsonType: "array",
          description: "Images, videos found on page",
          items: {
            bsonType: "object",
            properties: {
              type: { enum: ["image", "video", "audio"] },
              url: { bsonType: "string" },
              alt_text: { bsonType: "string" }
            }
          }
        },
        
        // HTTP metadata
        http_status: {
          bsonType: "int",
          description: "HTTP status code (200, 404, etc.)"
        },
        headers: {
          bsonType: "object",
          description: "Relevant HTTP headers"
        },
        
        // Processing status
        processing_status: {
          enum: ["pending", "processing", "completed", "failed"],
          description: "Post extraction status"
        },
        posts_extracted_count: {
          bsonType: "int",
          minimum: 0,
          description: "Number of posts extracted from this page"
        },
        
        // Timing
        fetched_at: {
          bsonType: "date",
          description: "When the page was fetched"
        },
        processed_at: {
          bsonType: "date",
          description: "When post extraction completed"
        },
        
        // Retention
        retention_policy: {
          enum: ["low_value", "high_value"],
          description: "Data retention classification"
        },
        expires_at: {
          bsonType: "date",
          description: "TTL expiration date"
        }
      }
    }
  }
});

// Indexes for raw_pages
db.raw_pages.createIndex({ search_execution_id: 1 });
db.raw_pages.createIndex({ project_id: 1, fetched_at: -1 });
db.raw_pages.createIndex({ url_hash: 1 }, { unique: true });
db.raw_pages.createIndex({ url: 1 });
db.raw_pages.createIndex({ processing_status: 1 });
db.raw_pages.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 }); // TTL index
db.raw_pages.createIndex({ text_content: "text" }); // Full-text search

print("✓ Created collection: raw_pages");

// ============================================================================
// COLLECTION: raw_posts
// Purpose: Individual posts/comments extracted from raw pages
// ============================================================================

db.createCollection("raw_posts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["search_execution_id", "source_type", "content", "posted_at", "extracted_at"],
      properties: {
        search_execution_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL search_executions.id"
        },
        raw_page_id: {
          bsonType: "objectId",
          description: "Reference to raw_pages._id where this post was found"
        },
        project_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL projects.id"
        },
        source_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL data_sources.id"
        },
        source_type: {
          enum: ["twitter", "reddit", "quora", "forum"],
          description: "Type of social media source"
        },
        source_post_id: {
          bsonType: "string",
          description: "Original platform post ID"
        },
        source_url: {
          bsonType: "string",
          description: "URL to original post"
        },
        content: {
          bsonType: "string",
          description: "Raw post content"
        },
        author_username: {
          bsonType: "string",
          description: "Author username (may contain PII)"
        },
        likes: {
          bsonType: "int",
          minimum: 0
        },
        shares: {
          bsonType: "int",
          minimum: 0
        },
        comments: {
          bsonType: "int",
          minimum: 0
        },
        views: {
          bsonType: "int",
          minimum: 0
        },
        posted_at: {
          bsonType: "date",
          description: "When the post was originally published"
        },
        extracted_at: {
          bsonType: "date",
          description: "When we extracted this post from the raw page"
        },
        processing_status: {
          enum: ["pending", "processing", "completed", "failed"],
          description: "AI processing status"
        },
        retention_policy: {
          enum: ["low_value", "high_value"],
          description: "Data retention classification"
        },
        expires_at: {
          bsonType: "date",
          description: "TTL expiration date (30 days for low_value)"
        }
      }
    }
  }
});

// Indexes for raw_posts
db.raw_posts.createIndex({ search_execution_id: 1 });
db.raw_posts.createIndex({ raw_page_id: 1 });
db.raw_posts.createIndex({ project_id: 1, extracted_at: -1 });
db.raw_posts.createIndex({ source_id: 1 });
db.raw_posts.createIndex({ source_post_id: 1 }, { unique: true, sparse: true });
db.raw_posts.createIndex({ processing_status: 1 });
db.raw_posts.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 }); // TTL index
db.raw_posts.createIndex({ content: "text" }); // Full-text search
db.raw_posts.createIndex({ posted_at: -1 });

print("✓ Created collection: raw_posts");

// ============================================================================
// COLLECTION: analyzed_posts
// Purpose: Posts after AI agent processing with comprehensive analysis
// ============================================================================

db.createCollection("analyzed_posts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["raw_post_id", "project_id", "anonymized_content", "processed_at"],
      properties: {
        raw_post_id: {
          bsonType: "objectId",
          description: "Reference to raw_posts._id"
        },
        project_id: {
          bsonType: "string",
          description: "UUID reference to PostgreSQL projects.id"
        },
        
        // ===== ANONYMIZER AGENT OUTPUT =====
        anonymized_content: {
          bsonType: "string",
          description: "Content with PII/PHI removed"
        },
        pii_detected: {
          bsonType: "bool",
          description: "Whether PII was found and removed"
        },
        pii_types: {
          bsonType: "array",
          description: "Types of PII found (name, email, phone, location, etc.)",
          items: { bsonType: "string" }
        },
        pii_redaction_map: {
          bsonType: "object",
          description: "Mapping of redacted entities for potential reversal"
        },
        anonymizer_confidence: {
          bsonType: "double",
          description: "Confidence that all PII was removed (0.0-1.0)"
        },
        
        // ===== RELEVANCE FILTER =====
        relevance: {
          bsonType: "object",
          description: "Relevance scoring and filtering decision",
          properties: {
            is_relevant: {
              bsonType: "bool",
              description: "Whether post is relevant to project keywords"
            },
            relevance_score: {
              bsonType: "double",
              description: "Relevance score (0.0-1.0)"
            },
            matched_keywords: {
              bsonType: "array",
              description: "Keywords from project that matched",
              items: { bsonType: "string" }
            },
            filter_reason: {
              bsonType: "string",
              description: "Reason for filtering out (if not relevant)"
            },
            is_noise: {
              bsonType: "bool",
              description: "Flagged as noise/spam"
            },
            language_match: {
              bsonType: "bool",
              description: "Whether language matches project requirements"
            }
          }
        },
        
        // ===== MEDICAL ENTITY EXTRACTOR OUTPUT =====
        entities: {
          bsonType: "object",
          description: "Extracted medical entities",
          properties: {
            drugs: {
              bsonType: "array",
              items: {
                bsonType: "object",
                properties: {
                  name: { bsonType: "string" },
                  generic_name: { bsonType: "string" },
                  brand_name: { bsonType: "string" },
                  dosage: { bsonType: "string" },
                  frequency: { bsonType: "string" },
                  duration: { bsonType: "string" },
                  route: { bsonType: "string" },
                  confidence: { bsonType: "double" },
                  context: { bsonType: "string" }
                }
              }
            },
            symptoms: {
              bsonType: "array",
              items: {
                bsonType: "object",
                properties: {
                  name: { bsonType: "string" },
                  severity: { enum: ["mild", "moderate", "severe", "critical"] },
                  onset: { bsonType: "string" },
                  duration: { bsonType: "string" },
                  confidence: { bsonType: "double" },
                  context: { bsonType: "string" }
                }
              }
            },
            conditions: {
              bsonType: "array",
              items: {
                bsonType: "object",
                properties: {
                  name: { bsonType: "string" },
                  icd_code: { bsonType: "string" },
                  confidence: { bsonType: "double" },
                  context: { bsonType: "string" }
                }
              }
            },
            procedures: {
              bsonType: "array",
              items: {
                bsonType: "object",
                properties: {
                  name: { bsonType: "string" },
                  confidence: { bsonType: "double" }
                }
              }
            }
          }
        },
        entity_extraction_confidence: {
          bsonType: "double",
          description: "Overall confidence in entity extraction"
        },
        
        // ===== SENTIMENT ANALYST OUTPUT =====
        sentiment: {
          bsonType: "object",
          description: "Sentiment analysis results",
          properties: {
            overall: {
              enum: ["very_negative", "negative", "neutral", "positive", "very_positive"],
              description: "Overall sentiment classification"
            },
            score: {
              bsonType: "double",
              description: "Sentiment score (-1.0 to 1.0)"
            },
            emotions: {
              bsonType: "array",
              description: "Detected emotions",
              items: { bsonType: "string" }
            },
            emotion_scores: {
              bsonType: "object",
              description: "Scores for each emotion (fear, anger, sadness, etc.)"
            },
            confidence: {
              bsonType: "double",
              description: "Confidence in sentiment analysis"
            },
            context: {
              bsonType: "string",
              description: "Context of sentiment (frustration with side effect vs general dissatisfaction)"
            },
            is_patient_experience: {
              bsonType: "bool",
              description: "Whether this is a first-hand patient experience"
            }
          }
        },
        
        // ===== TREND & VIRALITY AGENT OUTPUT =====
        virality: {
          bsonType: "object",
          description: "Virality and trend metrics",
          properties: {
            score: {
              bsonType: "double",
              description: "Virality score (0-100)"
            },
            trend: {
              enum: ["rising", "stable", "declining", "viral"],
              description: "Trend classification"
            },
            engagement_rate: {
              bsonType: "double",
              description: "Engagement rate (likes+shares+comments / views)"
            },
            viral_potential: {
              enum: ["low", "medium", "high", "critical"],
              description: "Potential for going viral"
            },
            velocity: {
              bsonType: "double",
              description: "Rate of engagement growth"
            },
            similar_posts_count: {
              bsonType: "int",
              description: "Number of similar posts found in timeframe"
            },
            is_trending: {
              bsonType: "bool",
              description: "Whether this topic is currently trending"
            }
          }
        },
        
        // ===== SAFETY AUDITOR OUTPUT =====
        safety_audit: {
          bsonType: "object",
          description: "Safety assessment results",
          properties: {
            is_adverse_event: {
              bsonType: "bool",
              description: "Whether this is an adverse drug event"
            },
            severity: {
              enum: ["low", "medium", "high", "critical"],
              description: "Severity of safety concern"
            },
            known_side_effect: {
              bsonType: "bool",
              description: "Whether symptom is a known side effect"
            },
            requires_investigation: {
              bsonType: "bool",
              description: "Whether this requires immediate investigation"
            },
            confidence: {
              bsonType: "double",
              description: "Confidence in safety assessment"
            },
            risk_category: {
              enum: ["no_risk", "low_risk", "moderate_risk", "high_risk", "critical_risk"],
              description: "Risk category classification"
            },
            medical_database_match: {
              bsonType: "bool",
              description: "Whether matched against medical knowledge base"
            },
            fda_label_check: {
              bsonType: "bool",
              description: "Whether checked against FDA drug labels"
            },
            similar_reports_count: {
              bsonType: "int",
              description: "Number of similar adverse event reports found"
            }
          }
        },
        
        // ===== AI INTERPRETATION & SUGGESTION =====
        ai_interpretation: {
          bsonType: "object",
          description: "AI-generated interpretation and suggestions",
          properties: {
            summary: {
              bsonType: "string",
              description: "Human-readable summary of the post"
            },
            key_findings: {
              bsonType: "array",
              description: "Key findings from analysis",
              items: { bsonType: "string" }
            },
            clinical_significance: {
              bsonType: "string",
              description: "Clinical significance explanation"
            },
            recommended_action: {
              enum: ["monitor", "investigate", "escalate", "archive", "ignore"],
              description: "Recommended action for this post"
            },
            action_rationale: {
              bsonType: "string",
              description: "Explanation for recommended action"
            },
            suggested_tags: {
              bsonType: "array",
              description: "AI-suggested tags for categorization",
              items: { bsonType: "string" }
            },
            related_signals: {
              bsonType: "array",
              description: "IDs of related signals/posts",
              items: { bsonType: "string" }
            },
            confidence_overall: {
              bsonType: "double",
              description: "Overall confidence in AI analysis (0.0-1.0)"
            }
          }
        },
        
        // ===== CLASSIFICATION & FILTERING =====
        signal_type: {
          enum: ["adverse_event", "quality_issue", "sentiment_spike", "treatment_efficacy", "drug_interaction", "off_label_use", "noise", null],
          description: "Classified signal type"
        },
        signal_priority: {
          enum: ["low", "medium", "high", "critical", "filtered_out", null],
          description: "Signal priority level"
        },
        should_escalate: {
          bsonType: "bool",
          description: "Whether this should be escalated immediately"
        },
        escalation_reason: {
          bsonType: "string",
          description: "Reason for escalation"
        },
        
        // ===== ARCHIVAL & RETENTION =====
        archived_to_postgres: {
          bsonType: "bool",
          description: "Whether archived to PostgreSQL safety_signals"
        },
        postgres_signal_id: {
          bsonType: ["string", "null"],
          description: "UUID of PostgreSQL safety_signals.id if archived"
        },
        retention_policy: {
          enum: ["low_value", "high_value"],
          description: "Data retention classification"
        },
        
        // ===== AGENT PIPELINE METADATA =====
        agent_pipeline: {
          bsonType: "object",
          description: "Execution metadata for each agent",
          properties: {
            anonymizer: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" },
                error: { bsonType: "string" }
              }
            },
            relevance_filter: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" }
              }
            },
            extractor: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" }
              }
            },
            sentiment: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" }
              }
            },
            trend: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" }
              }
            },
            auditor: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" }
              }
            },
            interpreter: {
              bsonType: "object",
              properties: {
                status: { enum: ["completed", "failed", "skipped"] },
                duration_ms: { bsonType: "int" },
                model_used: { bsonType: "string" }
              }
            }
          }
        },
        
        // ===== TRACEABILITY =====
        langsmith_trace_id: {
          bsonType: "string",
          description: "LangSmith trace ID for full execution trace"
        },
        langsmith_run_id: {
          bsonType: "string",
          description: "LangSmith run ID"
        },
        
        // ===== TIMESTAMPS =====
        processed_at: {
          bsonType: "date",
          description: "When AI processing completed"
        },
        created_at: {
          bsonType: "date",
          description: "When record was created"
        }
      }
    }
  }
});

// Indexes for analyzed_posts
db.analyzed_posts.createIndex({ raw_post_id: 1 }, { unique: true });
db.analyzed_posts.createIndex({ project_id: 1, processed_at: -1 });
db.analyzed_posts.createIndex({ "safety_audit.is_adverse_event": 1, "safety_audit.severity": 1 });
db.analyzed_posts.createIndex({ signal_priority: 1 });
db.analyzed_posts.createIndex({ archived_to_postgres: 1 });
db.analyzed_posts.createIndex({ "entities.drugs.name": 1 });
db.analyzed_posts.createIndex({ "entities.symptoms.name": 1 });
db.analyzed_posts.createIndex({ langsmith_trace_id: 1 });
db.analyzed_posts.createIndex({ "relevance.is_relevant": 1 });
db.analyzed_posts.createIndex({ "relevance.is_noise": 1 });
db.analyzed_posts.createIndex({ "ai_interpretation.recommended_action": 1 });
db.analyzed_posts.createIndex({ should_escalate: 1 });
db.analyzed_posts.createIndex({ "virality.is_trending": 1 });

print("✓ Created collection: analyzed_posts");

// ============================================================================
// COLLECTION: agent_traces
// Purpose: Detailed execution traces for explainability
// ============================================================================

db.createCollection("agent_traces", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["trace_id", "agent_name", "status", "started_at"],
      properties: {
        trace_id: {
          bsonType: "string",
          description: "LangSmith trace ID"
        },
        run_id: {
          bsonType: "string",
          description: "LangSmith run ID"
        },
        analyzed_post_id: {
          bsonType: "objectId",
          description: "Reference to analyzed_posts._id"
        },
        agent_name: {
          bsonType: "string",
          description: "Name of the agent (anonymizer, extractor, etc.)"
        },
        llm_provider: {
          bsonType: "string",
          description: "LLM provider (openai, anthropic, etc.)"
        },
        model: {
          bsonType: "string",
          description: "Model name (gpt-4, claude-3, etc.)"
        },
        prompt_tokens: {
          bsonType: "int",
          minimum: 0
        },
        completion_tokens: {
          bsonType: "int",
          minimum: 0
        },
        total_cost: {
          bsonType: "double",
          minimum: 0
        },
        duration_ms: {
          bsonType: "int",
          minimum: 0
        },
        status: {
          enum: ["success", "failed", "timeout"],
          description: "Execution status"
        },
        cache_hit: {
          bsonType: "bool",
          description: "Whether result was retrieved from cache"
        },
        cache_key: {
          bsonType: "string",
          description: "Redis cache key for this operation"
        }
      }
    }
  }
});

// Indexes for agent_traces
db.agent_traces.createIndex({ trace_id: 1 });
db.agent_traces.createIndex({ run_id: 1 });
db.agent_traces.createIndex({ analyzed_post_id: 1 });
db.agent_traces.createIndex({ agent_name: 1, started_at: -1 });
db.agent_traces.createIndex({ cache_key: 1 });
db.agent_traces.createIndex({ started_at: -1 });

// TTL index - keep traces for 90 days
db.agent_traces.createIndex({ started_at: 1 }, { expireAfterSeconds: 7776000 }); // 90 days

print("✓ Created collection: agent_traces");



// ============================================================================
// SAMPLE DATA (for development/testing)
// ============================================================================

// Sample raw page
const samplePageId = new ObjectId();
db.raw_pages.insertOne({
  _id: samplePageId,
  search_execution_id: "00000000-0000-0000-0000-000000000001",
  project_id: "00000000-0000-0000-0000-000000000002",
  source_id: "00000000-0000-0000-0000-000000000003",
  url: "https://reddit.com/r/pharmacy/new",
  url_hash: "hash_abc123",
  canonical_url: "https://reddit.com/r/pharmacy/new",
  html_content: "<html>...</html>",
  text_content: "Discussion about Drug-Y side effects...",
  title: "r/pharmacy - New Posts",
  description: "Pharmacy subreddit discussions",
  links: [
    { href: "/r/pharmacy/comments/abc123", text: "Drug-Y side effects", type: "internal" }
  ],
  media: [],
  http_status: 200,
  headers: { "content-type": "text/html" },
  processing_status: "completed",
  posts_extracted_count: 5,
  fetched_at: new Date("2026-05-06T09:00:00Z"),
  processed_at: new Date("2026-05-06T09:01:00Z"),
  retention_policy: "low_value",
  expires_at: new Date("2026-06-05T09:00:00Z")
});

// Sample raw post extracted from page
db.raw_posts.insertOne({
  search_execution_id: "00000000-0000-0000-0000-000000000001",
  raw_page_id: samplePageId,
  project_id: "00000000-0000-0000-0000-000000000002",
  source_id: "00000000-0000-0000-0000-000000000003",
  source_type: "reddit",
  source_post_id: "reddit_abc123",
  source_url: "https://reddit.com/r/pharmacy/comments/abc123",
  content: "I've been taking Drug-Y 50mg twice daily for 2 weeks and experiencing severe headaches. Anyone else?",
  author_username: "healthuser123",
  author_id: "reddit_user_456",
  likes: 45,
  shares: 12,
  comments: 23,
  views: 890,
  posted_at: new Date("2026-05-06T08:30:00Z"),
  extracted_at: new Date("2026-05-06T09:01:00Z"),
  processing_status: "pending",
  language: "en",
  hashtags: [],
  mentions: [],
  media: [],
  retention_policy: "low_value",
  expires_at: new Date("2026-06-05T09:00:00Z"),
  created_at: new Date()
});

print("✓ Inserted sample data");

// ============================================================================
// SCHEMA VERSION
// ============================================================================

db.createCollection("schema_version");
db.schema_version.insertOne({
  version: "1.0.0",
  applied_at: new Date(),
  description: "Initial schema with raw_pages, raw_posts, analyzed_posts, and agent_traces. Search tracking via PostgreSQL search_executions."
});

print("✓ Schema version recorded");

// ============================================================================
// SUMMARY
// ============================================================================

print("\n========================================");
print("MongoDB Schema Setup Complete!");
print("========================================");
print("Collections created:");
print("  - raw_pages (with TTL index) - Raw HTML/page data");
print("  - raw_posts (with TTL index) - Extracted posts from pages");
print("  - analyzed_posts - AI-processed posts");
print("  - agent_traces (with 90-day TTL) - Execution traces");
print("  - schema_version");
print("\nIndexes created for optimal query performance");
print("Validation rules applied to all collections");
print("Cross-references to PostgreSQL via UUID strings");
print("========================================\n");
