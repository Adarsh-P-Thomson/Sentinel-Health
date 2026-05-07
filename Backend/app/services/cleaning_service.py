"""
Cleaning Service
Uses the Anonymizer Agent to clean and anonymize raw posts in batches
This is the PROCESS step - NO AI analysis, just cleaning
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.agents.anonymizer import anonymize_node
from app.graph.state import AgentState


class CleaningService:
    """
    Cleans and anonymizes raw posts using the Anonymizer Agent
    Does NOT send to AI for analysis - just prepares data
    """
    
    def __init__(self, mongodb: AsyncIOMotorDatabase):
        self.mongodb = mongodb
    
    async def process_latest(self) -> Dict[str, Any]:
        """
        Find and clean the latest unprocessed search results
        
        Returns:
            Summary of cleaning operation
        """
        print(f"\n{'='*80}")
        print(f"🧹 Finding Latest Unprocessed Data")
        print(f"{'='*80}\n")
        
        # Find the most recent search_execution_id with pending posts
        pipeline = [
            {"$match": {"processing_status": "pending"}},
            {"$group": {
                "_id": "$search_execution_id",
                "latest_created": {"$max": "$created_at"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"latest_created": -1}},
            {"$limit": 1}
        ]
        
        cursor = self.mongodb.raw_posts.aggregate(pipeline)
        results = await cursor.to_list(length=1)
        
        if not results:
            return {
                "status": "no_posts_to_clean",
                "message": "No unprocessed data found",
                "total_cleaned": 0
            }
        
        search_execution_id = results[0]["_id"]
        pending_count = results[0]["count"]
        
        print(f"📝 Found {pending_count} pending posts for search: {search_execution_id}")
        
        # Clean all posts for this search
        return await self.clean_search(search_execution_id)
    
    async def clean_search(self, search_execution_id: str) -> Dict[str, Any]:
        """
        Clean all raw posts for a search execution
        
        Args:
            search_execution_id: Search execution ID to clean
            
        Returns:
            Summary of cleaning operation
        """
        print(f"\n{'='*80}")
        print(f"🧹 Starting Data Cleaning for Search: {search_execution_id}")
        print(f"{'='*80}\n")
        
        # Query raw_posts that need cleaning
        query = {
            "search_execution_id": search_execution_id,
            "processing_status": "pending"
        }
        
        # Fetch posts
        cursor = self.mongodb.raw_posts.find(query).sort("created_at", 1)
        posts = await cursor.to_list(length=None)
        
        if not posts:
            return {
                "status": "no_posts_to_clean",
                "message": "No pending posts found",
                "search_execution_id": search_execution_id,
                "total_cleaned": 0
            }
        
        print(f"📝 Cleaning {len(posts)} posts...")
        
        # Clean each post using the Anonymizer Agent
        cleaned_count = 0
        failed_count = 0
        
        for post in posts:
            try:
                await self._clean_post(post)
                cleaned_count += 1
                
                if cleaned_count % 10 == 0:
                    print(f"  ✓ Cleaned {cleaned_count}/{len(posts)} posts...")
                    
            except Exception as e:
                print(f"  ✗ Failed to clean post {post['_id']}: {e}")
                failed_count += 1
        
        print(f"\n{'='*80}")
        print(f"✅ Data Cleaning Complete!")
        print(f"{'='*80}")
        print(f"Total Posts Cleaned: {cleaned_count}")
        print(f"Total Posts Failed: {failed_count}")
        print(f"{'='*80}\n")
        
        return {
            "status": "completed",
            "message": f"Cleaned {cleaned_count} posts",
            "search_execution_id": search_execution_id,
            "total_cleaned": cleaned_count,
            "total_failed": failed_count
        }
    
    async def _clean_post(self, post: Dict) -> None:
        """
        Clean and anonymize a single post using the Anonymizer Agent
        
        Args:
            post: Raw post document
        """
        content = post.get("content", "")
        
        # Use the Anonymizer Agent to clean and anonymize
        state = AgentState(
            raw_text=content,
            source=post.get("source_type", "unknown")
        )
        
        result = await anonymize_node(state)
        
        anonymized_text = result.get("anonymized_text", "")
        anonymizer_result = result.get("anonymizer_result")
        
        # Create cleaned post document
        cleaned_post = {
            "cleaned_post_id": str(uuid.uuid4()),
            "original_post_id": post["_id"],
            "search_execution_id": post["search_execution_id"],
            "source_id": post.get("source_id"),
            "source_type": post.get("source_type"),
            "source_post_id": post.get("source_post_id"),
            "source_url": post.get("source_url"),
            
            # Original content (for reference)
            "original_content": content,
            
            # Cleaned content
            "cleaned_content": anonymized_text,
            
            # Anonymizer metadata
            "pii_detected": anonymizer_result.pii_detected if anonymizer_result else False,
            "pii_types": anonymizer_result.pii_types if anonymizer_result else [],
            "pii_redaction_map": anonymizer_result.pii_redaction_map if anonymizer_result else {},
            "anonymizer_confidence": anonymizer_result.anonymizer_confidence if anonymizer_result else 0.0,
            
            # Lengths
            "original_length": len(content),
            "cleaned_length": len(anonymized_text),
            
            # Metadata
            "author_username": post.get("author_username"),
            "posted_at": post.get("posted_at"),
            "extracted_at": post.get("extracted_at"),
            "cleaned_at": datetime.utcnow(),
            
            # Status
            "ai_analysis_status": "pending",  # Ready for AI analysis
            "created_at": datetime.utcnow()
        }
        
        # Insert into cleaned_posts collection
        await self.mongodb.cleaned_posts.insert_one(cleaned_post)
        
        # Mark raw post as cleaned
        await self.mongodb.raw_posts.update_one(
            {"_id": post["_id"]},
            {"$set": {"processing_status": "cleaned"}}
        )
