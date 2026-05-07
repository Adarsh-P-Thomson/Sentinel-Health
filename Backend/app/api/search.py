"""
Search API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db, get_mongodb
from app.search.orchestrator import SearchOrchestrator

router = APIRouter(tags=["Search"])


# Request/Response Models
class SearchRequest(BaseModel):
    """Search request model"""
    project_id: Optional[str] = None  # Optional - for public searches
    source_ids: List[str]
    query: str
    keywords: Optional[List[str]] = None  # Optional - will use query if not provided
    search_params: Optional[Dict[str, Dict[str, Any]]] = None


class SearchResponse(BaseModel):
    """Search response model"""
    total_pages_found: int
    total_posts_extracted: int
    results_by_source: Dict[str, Any]
    errors: List[str]


@router.get("/sources", summary="Get available search sources")
async def get_search_sources(
    mongodb: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get list of available search sources
    
    Returns list of sources with their configuration
    """
    orchestrator = SearchOrchestrator(mongodb, None)
    sources = orchestrator.get_available_sources()
    
    return {
        "sources": sources,
        "total": len(sources),
        "enabled": len([s for s in sources if s["enabled"]])
    }


@router.post("/search", response_model=SearchResponse, summary="Execute search")
async def execute_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    mongodb: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Execute search across one or more sources
    
    - **project_id**: UUID of the project (optional - leave null for public searches)
    - **source_ids**: List of source IDs (reddit, twitter, google)
    - **query**: Search query string
    - **keywords**: List of keywords to search for
    - **search_params**: Optional source-specific parameters
    
    Example:
    ```json
    {
      "source_ids": ["reddit", "twitter"],
      "query": "Drug-Y side effects",
      "keywords": ["Drug-Y", "headache", "nausea"],
      "search_params": {
        "reddit": {
          "subreddit": "pharmacy",
          "sort": "new",
          "limit": 100
        },
        "twitter": {
          "count": 50,
          "result_type": "recent"
        }
      }
    }
    ```
    """
    orchestrator = SearchOrchestrator(mongodb, db)
    
    # Use query as keyword if no keywords provided
    keywords = request.keywords if request.keywords else [request.query]
    
    if len(request.source_ids) == 1:
        # Single source search
        result = await orchestrator.execute_search(
            project_id=request.project_id,
            source_id=request.source_ids[0],
            query=request.query,
            keywords=keywords,
            search_params=request.search_params.get(request.source_ids[0]) if request.search_params else None
        )
        
        return {
            "total_pages_found": result.get("pages_found", 0),
            "total_posts_extracted": result.get("posts_extracted", 0),
            "results_by_source": {request.source_ids[0]: result},
            "errors": result.get("errors", [])
        }
    else:
        # Multi-source search
        result = await orchestrator.execute_multi_source_search(
            project_id=request.project_id,
            source_ids=request.source_ids,
            query=request.query,
            keywords=keywords,
            search_params=request.search_params
        )
        
        return result


@router.get("/search/{search_execution_id}", summary="Get search execution status")
async def get_search_execution(
    search_execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status and results of a search execution
    
    Returns detailed information about a specific search execution
    """
    from app.models import SearchExecution
    from sqlalchemy import select
    
    stmt = select(SearchExecution).where(SearchExecution.id == search_execution_id)
    result = await db.execute(stmt)
    search_execution = result.scalar_one_or_none()
    
    if not search_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search execution {search_execution_id} not found"
        )
    
    return {
        "id": str(search_execution.id),
        "project_id": str(search_execution.project_id),
        "source_id": search_execution.source_id,
        "search_query": search_execution.search_query,
        "keywords_used": search_execution.keywords_used,
        "status": search_execution.status,
        "pages_found": search_execution.pages_found,
        "pages_stored": search_execution.pages_stored,
        "posts_extracted": search_execution.posts_extracted,
        "mongodb_page_ids": search_execution.mongodb_page_ids,
        "mongodb_post_ids": search_execution.mongodb_post_ids,
        "started_at": search_execution.started_at.isoformat() if search_execution.started_at else None,
        "completed_at": search_execution.completed_at.isoformat() if search_execution.completed_at else None,
        "duration_ms": search_execution.duration_ms,
        "error_message": search_execution.error_message
    }
