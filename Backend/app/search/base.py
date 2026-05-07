"""
Base search engine interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseSearchEngine(ABC):
    """Base class for all search engines"""
    
    def __init__(
        self,
        source_config: Dict[str, Any],
        mongodb: AsyncIOMotorDatabase,
        project_id: str,
        search_execution_id: str
    ):
        self.source_config = source_config
        self.mongodb = mongodb
        self.project_id = project_id
        self.search_execution_id = search_execution_id
        
        self.source_id = source_config.get("id")
        self.source_name = source_config.get("name")
        self.rate_limit = source_config.get("rate_limit", {})
        
    @abstractmethod
    async def search(
        self,
        query: str,
        keywords: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute search and return results
        
        Returns:
            {
                "pages_found": int,
                "pages_stored": int,
                "posts_extracted": int,
                "mongodb_page_ids": List[str],
                "mongodb_post_ids": List[str],
                "errors": List[str]
            }
        """
        pass
    
    @abstractmethod
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a single page and return raw data"""
        pass
    
    @abstractmethod
    async def extract_posts(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract individual posts from page data"""
        pass
    
    async def store_raw_page(self, page_data: Dict[str, Any]) -> str:
        """
        Store raw page data in MongoDB
        
        Returns:
            MongoDB ObjectId as string
        """
        from bson import ObjectId
        import hashlib
        
        # Generate URL hash for deduplication
        url_hash = hashlib.sha256(page_data["url"].encode()).hexdigest()
        
        # Check if page already exists
        existing = await self.mongodb.raw_pages.find_one({"url_hash": url_hash})
        if existing:
            return str(existing["_id"])
        
        # Prepare document - only include fields that have values
        document = {
            "search_execution_id": self.search_execution_id,
            "source_id": self.source_id,
            "url": page_data["url"],
            "url_hash": url_hash,
            "canonical_url": page_data.get("canonical_url", page_data["url"]),
            "html_content": page_data.get("html_content", ""),
            "text_content": page_data.get("text_content", ""),
            "title": page_data.get("title", ""),
            "description": page_data.get("description", ""),
            "links": page_data.get("links", []),
            "media": page_data.get("media", []),
            "http_status": page_data.get("http_status", 200),
            "headers": page_data.get("headers", {}),
            "processing_status": "pending",
            "posts_extracted_count": 0,
            "fetched_at": datetime.utcnow(),
            "retention_policy": "low_value",
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "created_at": datetime.utcnow()
        }
        
        # Add optional fields only if they have values
        if self.project_id:
            document["project_id"] = self.project_id
        if page_data.get("author"):
            document["author"] = page_data["author"]
        if page_data.get("published_date"):
            document["published_date"] = page_data["published_date"]
        
        result = await self.mongodb.raw_pages.insert_one(document)
        return str(result.inserted_id)
    
    async def store_raw_post(
        self,
        post_data: Dict[str, Any],
        raw_page_id: Optional[str] = None
    ) -> str:
        """
        Store raw post data in MongoDB
        
        Returns:
            MongoDB ObjectId as string
        """
        from bson import ObjectId
        
        # Check for duplicate by source_post_id
        if post_data.get("source_post_id"):
            existing = await self.mongodb.raw_posts.find_one({
                "source_post_id": post_data["source_post_id"]
            })
            if existing:
                return str(existing["_id"])
        
        # Prepare document - only include fields that have values
        document = {
            "search_execution_id": self.search_execution_id,
            "source_id": self.source_id,
            "source_type": self._get_source_type(),  # Get proper source type
            "source_post_id": post_data.get("source_post_id"),
            "source_url": post_data.get("source_url"),
            "content": post_data.get("content", ""),
            "author_username": post_data.get("author_username"),
            "author_id": post_data.get("author_id"),
            "likes": post_data.get("likes", 0),
            "shares": post_data.get("shares", 0),
            "comments": post_data.get("comments", 0),
            "views": post_data.get("views", 0),
            "posted_at": post_data.get("posted_at", datetime.utcnow()),
            "extracted_at": datetime.utcnow(),
            "processing_status": "pending",
            "language": post_data.get("language", "en"),
            "hashtags": post_data.get("hashtags", []),
            "mentions": post_data.get("mentions", []),
            "media": post_data.get("media", []),
            "retention_policy": "low_value",
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "created_at": datetime.utcnow()
        }
        
        # Add optional replies field
        if post_data.get("replies"):
            document["replies"] = post_data["replies"]
        
        # Add optional fields
        if raw_page_id:
            document["raw_page_id"] = ObjectId(raw_page_id)
        if self.project_id:
            document["project_id"] = self.project_id
        
        result = await self.mongodb.raw_posts.insert_one(document)
        return str(result.inserted_id)
    
    def _get_source_type(self) -> str:
        """Get proper source type for MongoDB validation"""
        source_id = self.source_id.lower()
        
        # Map source IDs to valid MongoDB enum values
        if 'reddit' in source_id:
            return 'reddit'
        elif 'twitter' in source_id or 'x.com' in source_id:
            return 'twitter'
        elif 'quora' in source_id:
            return 'quora'
        else:
            return 'forum'  # Default fallback
    
    async def respect_rate_limit(self):
        """Implement rate limiting"""
        requests_per_minute = self.rate_limit.get("requests_per_minute", 60)
        delay = 60.0 / requests_per_minute
        await asyncio.sleep(delay)
