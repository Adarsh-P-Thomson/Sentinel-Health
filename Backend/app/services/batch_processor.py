"""
Batch Processing Service
Processes raw_posts in batches with character limits and categorization
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.llm import get_structured_llm
from app.utils.text_cleaner import clean_text
from app.utils.anonymizer import anonymize_text
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS
# ============================================================================

class ProcessedEntry(BaseModel):
    """Schema for a single processed entry"""
    category_name: str = Field(description="Name of the category (e.g., 'Ibuprofen', 'Mayo Clinic')")
    category_type: str = Field(description="Type: medicine, hospital, drug, condition, symptom, procedure, general")
    processed_text: str = Field(description="Cleaned and processed text")
    ai_suggestion: str = Field(description="AI-generated suggestion or recommendation")
    ai_info: str = Field(description="Additional context or information from AI")
    sentiment: str = Field(description="very_negative, negative, neutral, positive, very_positive")
    severity: str = Field(description="low, medium, high, critical")
    is_adverse_event: bool = Field(description="Whether this is an adverse event")


class BatchProcessingResult(BaseModel):
    """Result of batch processing"""
    entries: List[ProcessedEntry] = Field(description="List of processed entries")


# ============================================================================
# BATCH PROCESSOR
# ============================================================================

class BatchProcessor:
    """
    Processes raw posts in batches with character limits
    """
    
    def __init__(
        self,
        mongodb: AsyncIOMotorDatabase,
        max_chars_per_batch: int = 8000,  # ~2000 tokens for GPT-4
        max_posts_per_batch: int = 20
    ):
        self.mongodb = mongodb
        self.max_chars_per_batch = max_chars_per_batch
        self.max_posts_per_batch = max_posts_per_batch
    
    async def create_batches(
        self,
        search_execution_id: str,
        project_id: Optional[str] = None
    ) -> List[str]:
        """
        Create batches from raw_posts
        
        Args:
            search_execution_id: Search execution ID to process
            project_id: Optional project ID filter
            
        Returns:
            List of batch IDs created
        """
        # Query raw_posts that need processing
        query = {
            "search_execution_id": search_execution_id,
            "processing_status": "pending"
        }
        if project_id:
            query["project_id"] = project_id
        
        # Fetch posts
        cursor = self.mongodb.raw_posts.find(query).sort("created_at", 1)
        posts = await cursor.to_list(length=None)
        
        if not posts:
            print(f"⚠️  No pending posts found for search_execution_id: {search_execution_id}")
            return []
        
        print(f"📦 Creating batches for {len(posts)} posts...")
        
        # Create batches
        batches = []
        current_batch = []
        current_char_count = 0
        
        for post in posts:
            content = post.get("content", "")
            content_length = len(content)
            
            # Check if adding this post would exceed limits
            if (current_char_count + content_length > self.max_chars_per_batch or
                len(current_batch) >= self.max_posts_per_batch):
                
                # Save current batch
                if current_batch:
                    batch_id = await self._save_batch(
                        current_batch,
                        search_execution_id,
                        current_char_count
                    )
                    batches.append(batch_id)
                
                # Start new batch
                current_batch = [post]
                current_char_count = content_length
            else:
                current_batch.append(post)
                current_char_count += content_length
        
        # Save last batch
        if current_batch:
            batch_id = await self._save_batch(
                current_batch,
                search_execution_id,
                current_char_count
            )
            batches.append(batch_id)
        
        print(f"✅ Created {len(batches)} batches")
        return batches
    
    async def _save_batch(
        self,
        posts: List[Dict],
        search_execution_id: str,
        char_count: int
    ) -> str:
        """Save batch to processing_batches collection"""
        batch_id = str(uuid.uuid4())
        
        batch_doc = {
            "batch_id": batch_id,
            "search_execution_id": search_execution_id,
            "status": "pending",
            "total_posts": len(posts),
            "processed_posts": 0,
            "failed_posts": 0,
            "post_ids": [post["_id"] for post in posts],
            "character_count": char_count,
            "max_characters": self.max_chars_per_batch,
            "created_at": datetime.utcnow()
        }
        
        await self.mongodb.processing_batches.insert_one(batch_doc)
        return batch_id
    
    async def process_batch(self, batch_id: str) -> Dict[str, Any]:
        """
        Process a single batch
        
        Args:
            batch_id: Batch ID to process
            
        Returns:
            Processing result with statistics
        """
        print(f"\n{'='*80}")
        print(f"🔄 Processing Batch: {batch_id}")
        print(f"{'='*80}")
        
        start_time = datetime.utcnow()
        
        # Get batch
        batch = await self.mongodb.processing_batches.find_one({"batch_id": batch_id})
        if not batch:
            raise ValueError(f"Batch not found: {batch_id}")
        
        # Update status to processing
        await self.mongodb.processing_batches.update_one(
            {"batch_id": batch_id},
            {
                "$set": {
                    "status": "processing",
                    "started_at": start_time
                }
            }
        )
        
        try:
            # Fetch posts
            post_ids = batch["post_ids"]
            cursor = self.mongodb.raw_posts.find({"_id": {"$in": post_ids}})
            posts = await cursor.to_list(length=None)
            
            print(f"📝 Processing {len(posts)} posts...")
            
            # Prepare batch text
            batch_text = self._prepare_batch_text(posts)
            
            print(f"📊 Batch size: {len(batch_text)} characters")
            
            # Process with AI
            processed_entries = await self._process_with_ai(batch_text, posts)
            
            print(f"✅ AI processed {len(processed_entries)} entries")
            
            # Store in categorized collections
            await self._store_categorized(processed_entries, batch_id)
            
            # Update batch status
            end_time = datetime.utcnow()
            processing_time = int((end_time - start_time).total_seconds() * 1000)
            
            await self.mongodb.processing_batches.update_one(
                {"batch_id": batch_id},
                {
                    "$set": {
                        "status": "completed",
                        "processed_posts": len(posts),
                        "completed_at": end_time,
                        "processing_time_ms": processing_time
                    }
                }
            )
            
            # Mark posts as processed
            await self.mongodb.raw_posts.update_many(
                {"_id": {"$in": post_ids}},
                {"$set": {"processing_status": "completed"}}
            )
            
            print(f"✅ Batch completed in {processing_time}ms")
            
            return {
                "batch_id": batch_id,
                "status": "completed",
                "total_posts": len(posts),
                "processed_entries": len(processed_entries),
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            
            # Update batch status to failed
            await self.mongodb.processing_batches.update_one(
                {"batch_id": batch_id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": str(e),
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            raise
    
    def _prepare_batch_text(self, posts: List[Dict]) -> str:
        """Prepare batch text for AI processing"""
        batch_lines = []
        
        for i, post in enumerate(posts):
            content = post.get("content", "")
            
            # Clean and anonymize
            cleaned = clean_text(content)
            anonymized, _ = anonymize_text(cleaned)
            
            # Add to batch with separator
            batch_lines.append(f"--- POST {i+1} (ID: {post['_id']}) ---")
            batch_lines.append(anonymized)
            batch_lines.append("")  # Empty line separator
        
        return "\n".join(batch_lines)
    
    async def _process_with_ai(
        self,
        batch_text: str,
        posts: List[Dict]
    ) -> List[Dict]:
        """Process batch with AI"""
        
        structured_llm = get_structured_llm(
            schema=BatchProcessingResult,
            temperature=0.0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical data analyst processing patient posts about medications and health experiences.

For each post in the batch, extract:

1. **category_name**: The main subject (drug name, hospital name, condition, etc.)
   - Examples: "Ibuprofen", "Lisinopril", "Mayo Clinic", "Diabetes", "Headache"

2. **category_type**: One of: medicine, hospital, drug, condition, symptom, procedure, general
   - medicine/drug: Medications (Ibuprofen, Lisinopril, Advil)
   - hospital: Healthcare facilities (Mayo Clinic, Johns Hopkins)
   - condition: Medical conditions (Diabetes, Hypertension)
   - symptom: Symptoms (Headache, Nausea, Dizziness)
   - procedure: Medical procedures (Surgery, MRI, Blood Test)
   - general: Other health-related topics

3. **processed_text**: Clean summary of the post (1-2 sentences)

4. **ai_suggestion**: Actionable suggestion or recommendation
   - Examples: "Consider consulting a doctor", "This is a known side effect", "Monitor symptoms"

5. **ai_info**: Additional context or medical information
   - Examples: "Ibuprofen is an NSAID that can cause stomach issues", "Common side effect of ACE inhibitors"

6. **sentiment**: very_negative, negative, neutral, positive, very_positive

7. **severity**: low, medium, high, critical

8. **is_adverse_event**: true if this describes an adverse drug event, false otherwise

Process ALL posts in the batch. Return one entry per post.
"""),
            ("human", "Batch of posts to process:\n\n{batch_text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"batch_text": batch_text})
        
        # Combine with original post IDs
        processed = []
        for i, entry in enumerate(result.entries):
            if i < len(posts):
                processed.append({
                    "entry": entry,
                    "post_id": posts[i]["_id"]
                })
        
        return processed
    
    async def _store_categorized(
        self,
        processed_entries: List[Dict],
        batch_id: str
    ):
        """Store processed entries in categorized collections"""
        
        for item in processed_entries:
            entry = item["entry"]
            post_id = item["post_id"]
            
            # Create entry document
            entry_doc = {
                "entry_id": str(uuid.uuid4()),
                "original_post_id": post_id,
                "batch_id": batch_id,
                "processed_text": entry.processed_text,
                "ai_suggestion": entry.ai_suggestion,
                "ai_info": entry.ai_info,
                "sentiment": entry.sentiment,
                "severity": entry.severity,
                "is_adverse_event": entry.is_adverse_event,
                "processed_at": datetime.utcnow(),
                "metadata": {}
            }
            
            # Upsert into category
            await self.mongodb.processed_categories.update_one(
                {
                    "category_name": entry.category_name,
                    "category_type": entry.category_type
                },
                {
                    "$push": {"processed_entries": entry_doc},
                    "$inc": {"total_entries": 1},
                    "$set": {"last_updated": datetime.utcnow()},
                    "$setOnInsert": {
                        "created_at": datetime.utcnow(),
                        "tags": []
                    }
                },
                upsert=True
            )
            
            print(f"  ✓ Stored: {entry.category_name} ({entry.category_type})")
    
    async def process_all_batches(self, search_execution_id: str) -> Dict[str, Any]:
        """
        Create and process all batches for a search execution
        
        Args:
            search_execution_id: Search execution ID
            
        Returns:
            Summary of all batch processing
        """
        print(f"\n{'='*80}")
        print(f"🚀 Starting Batch Processing for Search: {search_execution_id}")
        print(f"{'='*80}\n")
        
        # Create batches
        batch_ids = await self.create_batches(search_execution_id)
        
        if not batch_ids:
            return {
                "search_execution_id": search_execution_id,
                "total_batches": 0,
                "status": "no_posts_to_process"
            }
        
        # Process each batch
        results = []
        for batch_id in batch_ids:
            try:
                result = await self.process_batch(batch_id)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to process batch {batch_id}: {e}")
                results.append({
                    "batch_id": batch_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Summary
        total_processed = sum(r.get("total_posts", 0) for r in results)
        total_entries = sum(r.get("processed_entries", 0) for r in results)
        
        print(f"\n{'='*80}")
        print(f"✅ Batch Processing Complete!")
        print(f"{'='*80}")
        print(f"Total Batches: {len(batch_ids)}")
        print(f"Total Posts Processed: {total_processed}")
        print(f"Total Entries Created: {total_entries}")
        print(f"{'='*80}\n")
        
        return {
            "search_execution_id": search_execution_id,
            "total_batches": len(batch_ids),
            "total_posts_processed": total_processed,
            "total_entries_created": total_entries,
            "batch_results": results,
            "status": "completed"
        }
