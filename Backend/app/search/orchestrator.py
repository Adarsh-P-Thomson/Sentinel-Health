"""
Search orchestrator - coordinates searches across multiple sources
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.search.engines import RedditSearchEngine, TwitterSearchEngine, GoogleSearchEngine
from app.search.engines.simple_web import SimpleWebSearchEngine
from app.search.engines.duckduckgo import DuckDuckGoSearchEngine
from app.search.engines.bing import BingSearchEngine
from app.search.engines.serper import SerperSearchEngine
from app.search.engines.zyte import ZyteSearchEngine
from app.search.engines.reddit_json import RedditJSONSearchEngine


class SearchOrchestrator:
    """Orchestrates searches across multiple sources"""
    
    def __init__(self, mongodb: AsyncIOMotorDatabase, postgres_session: AsyncSession):
        self.mongodb = mongodb
        self.postgres_session = postgres_session
        self.sources_config = self._load_sources_config()
        
        # Map source types to engine classes
        self.engine_map = {
            "reddit": RedditSearchEngine,
            "reddit_json": RedditJSONSearchEngine,
            "twitter": TwitterSearchEngine,
            "google": SimpleWebSearchEngine,
            "duckduckgo": DuckDuckGoSearchEngine,
            "bing": BingSearchEngine,
            "serper": SerperSearchEngine,
            "serper_reddit": SerperSearchEngine,
            "serper_twitter": SerperSearchEngine,
            "zyte": ZyteSearchEngine,
            "simple_web": SimpleWebSearchEngine
        }
    
    def _load_sources_config(self) -> Dict[str, Any]:
        """Load sources configuration from JSON file"""
        config_path = Path(__file__).parent / "sources.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_available_sources(self) -> List[Dict[str, Any]]:
        """Get list of available search sources"""
        return [
            {
                "id": source["id"],
                "name": source["name"],
                "type": source["type"],
                "enabled": source["enabled"],
                "description": source["description"],
                "auth_required": source["auth_required"]
            }
            for source in self.sources_config["sources"]
        ]
    
    def get_source_config(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific source"""
        for source in self.sources_config["sources"]:
            if source["id"] == source_id:
                return source
        return None
    
    async def execute_search(
        self,
        project_id: str,
        source_id: str,
        query: str,
        keywords: List[str],
        search_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute search on a specific source
        
        Args:
            project_id: UUID of the project
            source_id: ID of the source to search (reddit, twitter, google)
            query: Search query string
            keywords: List of keywords from the project
            search_params: Additional search parameters
        
        Returns:
            {
                "search_execution_id": str,
                "status": str,
                "pages_found": int,
                "pages_stored": int,
                "posts_extracted": int,
                "mongodb_page_ids": List[str],
                "mongodb_post_ids": List[str],
                "errors": List[str],
                "duration_ms": int
            }
        """
        start_time = datetime.utcnow()
        
        # Get source configuration
        source_config = self.get_source_config(source_id)
        if not source_config:
            return {
                "status": "failed",
                "errors": [f"Source '{source_id}' not found"]
            }
        
        if not source_config["enabled"]:
            return {
                "status": "failed",
                "errors": [f"Source '{source_id}' is not enabled"]
            }
        
        # Create search execution record in PostgreSQL
        from app.models import SearchExecution, Project
        
        search_execution = SearchExecution(
            project_id=project_id,
            source_id=source_id,
            search_query=query,
            keywords_used=keywords,
            search_type="keyword_search",
            status="running"
        )
        
        self.postgres_session.add(search_execution)
        await self.postgres_session.commit()
        await self.postgres_session.refresh(search_execution)
        
        search_execution_id = str(search_execution.id)
        
        try:
            # Get the appropriate search engine
            engine_class = self.engine_map.get(source_id)
            if not engine_class:
                raise ValueError(f"No engine implementation for source '{source_id}'")
            
            # Initialize engine
            engine = engine_class(
                source_config=source_config,
                mongodb=self.mongodb,
                project_id=project_id,
                search_execution_id=search_execution_id
            )
            
            # Execute search
            search_params = search_params or {}
            results = await engine.search(query, keywords, **search_params)
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update search execution in PostgreSQL
            search_execution.status = "completed" if not results.get("errors") else "partial"
            search_execution.pages_found = results.get("pages_found", 0)
            search_execution.pages_stored = results.get("pages_stored", 0)
            search_execution.posts_extracted = results.get("posts_extracted", 0)
            search_execution.mongodb_page_ids = results.get("mongodb_page_ids", [])
            search_execution.mongodb_post_ids = results.get("mongodb_post_ids", [])
            search_execution.completed_at = end_time
            search_execution.duration_ms = duration_ms
            
            if results.get("errors"):
                search_execution.error_message = "; ".join(results["errors"])
            
            await self.postgres_session.commit()
            
            return {
                "search_execution_id": search_execution_id,
                "status": search_execution.status,
                "pages_found": results.get("pages_found", 0),
                "pages_stored": results.get("pages_stored", 0),
                "posts_extracted": results.get("posts_extracted", 0),
                "mongodb_page_ids": results.get("mongodb_page_ids", []),
                "mongodb_post_ids": results.get("mongodb_post_ids", []),
                "errors": results.get("errors", []),
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            # Update search execution with error
            search_execution.status = "failed"
            search_execution.error_message = str(e)
            search_execution.completed_at = datetime.utcnow()
            await self.postgres_session.commit()
            
            return {
                "search_execution_id": search_execution_id,
                "status": "failed",
                "errors": [str(e)]
            }
    
    async def execute_multi_source_search(
        self,
        project_id: str,
        source_ids: List[str],
        query: str,
        keywords: List[str],
        search_params: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute search across multiple sources in parallel
        
        Args:
            project_id: UUID of the project
            source_ids: List of source IDs to search
            query: Search query string
            keywords: List of keywords from the project
            search_params: Dict of source_id -> params
        
        Returns:
            {
                "total_pages_found": int,
                "total_posts_extracted": int,
                "results_by_source": Dict[str, Any],
                "errors": List[str]
            }
        """
        search_params = search_params or {}
        
        # Execute searches in parallel
        tasks = []
        for source_id in source_ids:
            params = search_params.get(source_id, {})
            task = self.execute_search(project_id, source_id, query, keywords, params)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        total_pages_found = 0
        total_posts_extracted = 0
        results_by_source = {}
        all_errors = []
        
        for source_id, result in zip(source_ids, results):
            if isinstance(result, Exception):
                all_errors.append(f"{source_id}: {str(result)}")
                results_by_source[source_id] = {"status": "failed", "error": str(result)}
            else:
                total_pages_found += result.get("pages_found", 0)
                total_posts_extracted += result.get("posts_extracted", 0)
                results_by_source[source_id] = result
                all_errors.extend(result.get("errors", []))
        
        return {
            "total_pages_found": total_pages_found,
            "total_posts_extracted": total_posts_extracted,
            "results_by_source": results_by_source,
            "errors": all_errors
        }
