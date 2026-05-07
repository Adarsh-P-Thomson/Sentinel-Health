// MongoDB Schema for Processed Categories Collection
// Purpose: Store AI-processed posts grouped by category (medicine, hospital, drug, etc.)

use Sentinel_health;

// ============================================================================
// COLLECTION: processed_categories
// Purpose: Categorized AI-processed content with suggestions
// ============================================================================

db.createCollection("processed_categories", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["category_name", "category_type", "created_at"],
      properties: {
        category_name: {
          bsonType: "string",
          description: "Name of the category (e.g., 'Ibuprofen', 'Mayo Clinic', 'Antibiotics')"
        },
        category_type: {
          enum: ["medicine", "hospital", "drug", "condition", "symptom", "procedure", "general"],
          description: "Type of category"
        },
        processed_entries: {
          bsonType: "array",
          description: "Array of processed text entries",
          items: {
            bsonType: "object",
            required: ["entry_id", "original_post_id", "processed_text", "processed_at"],
            properties: {
              entry_id: {
                bsonType: "string",
                description: "Unique ID for this entry (UUID)"
              },
              original_post_id: {
                bsonType: "objectId",
                description: "Reference to raw_posts._id"
              },
              batch_id: {
                bsonType: "string",
                description: "Batch ID this entry was processed in"
              },
              processed_text: {
                bsonType: "string",
                description: "AI-processed and cleaned text"
              },
              ai_suggestion: {
                bsonType: "string",
                description: "AI-generated suggestion or insight"
              },
              ai_info: {
                bsonType: "string",
                description: "Additional AI-generated information"
              },
              sentiment: {
                enum: ["very_negative", "negative", "neutral", "positive", "very_positive"],
                description: "Sentiment of the entry"
              },
              severity: {
                enum: ["low", "medium", "high", "critical"],
                description: "Severity level if applicable"
              },
              is_adverse_event: {
                bsonType: "bool",
                description: "Whether this is an adverse event"
              },
              processed_at: {
                bsonType: "date",
                description: "When this entry was processed"
              },
              metadata: {
                bsonType: "object",
                description: "Additional metadata from AI processing"
              }
            }
          }
        },
        total_entries: {
          bsonType: "int",
          minimum: 0,
          description: "Total number of entries in this category"
        },
        last_updated: {
          bsonType: "date",
          description: "Last time an entry was added"
        },
        created_at: {
          bsonType: "date",
          description: "When this category was created"
        },
        tags: {
          bsonType: "array",
          description: "Additional tags for this category",
          items: { bsonType: "string" }
        },
        summary: {
          bsonType: "object",
          description: "Summary statistics for this category",
          properties: {
            total_adverse_events: { bsonType: "int" },
            avg_sentiment_score: { bsonType: "double" },
            severity_breakdown: { bsonType: "object" },
            last_7_days_count: { bsonType: "int" }
          }
        }
      }
    }
  }
});

// Indexes for processed_categories
db.processed_categories.createIndex({ category_name: 1, category_type: 1 }, { unique: true });
db.processed_categories.createIndex({ category_type: 1 });
db.processed_categories.createIndex({ "processed_entries.entry_id": 1 });
db.processed_categories.createIndex({ "processed_entries.original_post_id": 1 });
db.processed_categories.createIndex({ "processed_entries.batch_id": 1 });
db.processed_categories.createIndex({ last_updated: -1 });
db.processed_categories.createIndex({ created_at: -1 });

print("✓ Created collection: processed_categories");

// ============================================================================
// COLLECTION: processing_batches
// Purpose: Track batch processing status
// ============================================================================

db.createCollection("processing_batches", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["batch_id", "status", "created_at"],
      properties: {
        batch_id: {
          bsonType: "string",
          description: "Unique batch identifier (UUID)"
        },
        search_execution_id: {
          bsonType: "string",
          description: "Reference to search_executions.id in PostgreSQL"
        },
        status: {
          enum: ["pending", "processing", "completed", "failed"],
          description: "Current status of the batch"
        },
        total_posts: {
          bsonType: "int",
          minimum: 0,
          description: "Total number of posts in this batch"
        },
        processed_posts: {
          bsonType: "int",
          minimum: 0,
          description: "Number of posts processed so far"
        },
        failed_posts: {
          bsonType: "int",
          minimum: 0,
          description: "Number of posts that failed processing"
        },
        post_ids: {
          bsonType: "array",
          description: "Array of raw_post ObjectIds in this batch",
          items: { bsonType: "objectId" }
        },
        character_count: {
          bsonType: "int",
          description: "Total character count for this batch"
        },
        max_characters: {
          bsonType: "int",
          description: "Maximum characters allowed per batch"
        },
        created_at: {
          bsonType: "date",
          description: "When batch was created"
        },
        started_at: {
          bsonType: "date",
          description: "When processing started"
        },
        completed_at: {
          bsonType: "date",
          description: "When processing completed"
        },
        error_message: {
          bsonType: "string",
          description: "Error message if batch failed"
        },
        processing_time_ms: {
          bsonType: "int",
          description: "Total processing time in milliseconds"
        },
        ai_cost: {
          bsonType: "double",
          description: "Estimated AI processing cost for this batch"
        }
      }
    }
  }
});

// Indexes for processing_batches
db.processing_batches.createIndex({ batch_id: 1 }, { unique: true });
db.processing_batches.createIndex({ search_execution_id: 1 });
db.processing_batches.createIndex({ status: 1 });
db.processing_batches.createIndex({ created_at: -1 });
db.processing_batches.createIndex({ "post_ids": 1 });

print("✓ Created collection: processing_batches");

// ============================================================================
// SAMPLE DATA
// ============================================================================

// Sample category: Ibuprofen (Medicine)
db.processed_categories.insertOne({
  category_name: "Ibuprofen",
  category_type: "medicine",
  processed_entries: [
    {
      entry_id: "entry-001",
      original_post_id: new ObjectId(),
      batch_id: "batch-001",
      processed_text: "Patient reports severe stomach pain after taking Ibuprofen 200mg three times daily for 2 weeks.",
      ai_suggestion: "Consider switching to acetaminophen or consulting gastroenterologist. Stomach pain is a known side effect of NSAIDs.",
      ai_info: "Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) that can cause gastrointestinal issues with prolonged use.",
      sentiment: "negative",
      severity: "medium",
      is_adverse_event: true,
      processed_at: new Date(),
      metadata: {
        dosage: "200mg",
        frequency: "three times daily",
        duration: "2 weeks"
      }
    }
  ],
  total_entries: 1,
  last_updated: new Date(),
  created_at: new Date(),
  tags: ["NSAID", "pain relief", "anti-inflammatory"],
  summary: {
    total_adverse_events: 1,
    avg_sentiment_score: -0.6,
    severity_breakdown: { low: 0, medium: 1, high: 0, critical: 0 },
    last_7_days_count: 1
  }
});

// Sample batch
db.processing_batches.insertOne({
  batch_id: "batch-001",
  search_execution_id: "00000000-0000-0000-0000-000000000001",
  status: "completed",
  total_posts: 10,
  processed_posts: 10,
  failed_posts: 0,
  post_ids: [new ObjectId(), new ObjectId()],
  character_count: 5000,
  max_characters: 10000,
  created_at: new Date("2026-05-07T10:00:00Z"),
  started_at: new Date("2026-05-07T10:00:05Z"),
  completed_at: new Date("2026-05-07T10:02:30Z"),
  processing_time_ms: 145000,
  ai_cost: 0.15
});

print("✓ Inserted sample data");

print("\n========================================");
print("Processed Categories Schema Complete!");
print("========================================");
print("Collections created:");
print("  - processed_categories - Categorized AI-processed content");
print("  - processing_batches - Batch processing tracking");
print("========================================\n");
