"""
API Endpoints for Batch Processing
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.core.database import get_mongodb
from app.services.batch_processor import BatchProcessor
from app.services.cleaning_service import CleaningService


router = APIRouter(tags=["Processing"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ProcessSearchRequest(BaseModel):
    """Request to process a search execution"""
    search_execution_id: str = Field(description="Search execution ID to process")
    project_id: Optional[str] = Field(default=None, description="Optional project ID filter")
    background: bool = Field(default=False, description="Process in background")


class ProcessBatchRequest(BaseModel):
    """Request to process a specific batch"""
    batch_id: str = Field(description="Batch ID to process")


class BatchStatusResponse(BaseModel):
    """Batch status response"""
    batch_id: str
    status: str
    total_posts: int
    processed_posts: int
    failed_posts: int
    character_count: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class ProcessingResponse(BaseModel):
    """Processing response"""
    message: str
    search_execution_id: str
    total_batches: int
    status: str
    batch_ids: Optional[List[str]] = None


class CategoryResponse(BaseModel):
    """Category response"""
    category_name: str
    category_type: str
    total_entries: int
    last_updated: str
    tags: List[str]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/clean/latest", response_model=ProcessingResponse, summary="Clean Latest Data (PROCESS Button)")
async def clean_latest_data():
    """
    **PROCESS Button** - Clean and anonymize the latest unprocessed search results
    
    This endpoint:
    1. Finds the most recent search_execution_id with pending posts
    2. Cleans text (removes formatting, normalizes)
    3. Anonymizes PII/PHI locally using Anonymizer Agent (NO AI analysis)
    4. Stores in `cleaned_posts` collection
    5. Marks posts as "cleaned" status
    
    **Does NOT send to AI for analysis** - just prepares data
    
    Use the `/analyze/latest` endpoint after this to send cleaned data to AI agents
    """
    try:
        print("[Clean Latest] Starting data cleaning...")
        
        mongodb = get_mongodb()
        cleaner = CleaningService(mongodb)
        
        result = await cleaner.process_latest()
        
        if result["status"] == "no_posts_to_clean":
            return ProcessingResponse(
                message=result["message"],
                search_execution_id="",
                total_batches=0,
                status="no_posts_to_clean",
                batch_ids=[]
            )
        
        return ProcessingResponse(
            message=result["message"],
            search_execution_id=result["search_execution_id"],
            total_batches=0,  # No batches yet, just cleaned
            status=result["status"],
            batch_ids=[]
        )
        
    except Exception as e:
        print(f"[Clean Latest] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean data: {str(e)}"
        )


@router.post("/process/latest", response_model=ProcessingResponse, summary="Process Latest Unprocessed Data")
async def process_latest_data(background_tasks: BackgroundTasks):
    """
    Automatically find and process the latest unprocessed search results
    
    - Finds the most recent search_execution_id with pending posts
    - Creates batches with character limits (8000 chars per batch)
    - Processes each batch with AI in background
    - Stores results in categorized collections
    - Marks posts as processed
    
    **Returns immediately with batch IDs for progress tracking**
    """
    try:
        print("[Process Latest] Finding latest unprocessed search execution...")
        
        mongodb = get_mongodb()
        
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
        
        cursor = mongodb.raw_posts.aggregate(pipeline)
        results = await cursor.to_list(length=1)
        
        if not results:
            print("[Process Latest] No pending posts found")
            return ProcessingResponse(
                message="No unprocessed data found",
                search_execution_id="",
                total_batches=0,
                status="no_posts_to_process",
                batch_ids=[]
            )
        
        search_execution_id = results[0]["_id"]
        pending_count = results[0]["count"]
        
        print(f"[Process Latest] Found search_execution_id: {search_execution_id} with {pending_count} pending posts")
        
        # Create batches
        processor = BatchProcessor(mongodb)
        batch_ids = await processor.create_batches(search_execution_id)
        
        if not batch_ids:
            return ProcessingResponse(
                message="No batches created",
                search_execution_id=search_execution_id,
                total_batches=0,
                status="no_posts_to_process",
                batch_ids=[]
            )
        
        # Process in background
        for batch_id in batch_ids:
            background_tasks.add_task(processor.process_batch, batch_id)
        
        print(f"[Process Latest] Started processing {len(batch_ids)} batches in background")
        
        return ProcessingResponse(
            message=f"Processing started for {pending_count} posts in {len(batch_ids)} batches",
            search_execution_id=search_execution_id,
            total_batches=len(batch_ids),
            status="processing",
            batch_ids=batch_ids
        )
        
    except Exception as e:
        print(f"[Process Latest] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process latest data: {str(e)}"
        )


@router.post("/process/search", response_model=ProcessingResponse, summary="Process Search Execution")
async def process_search_execution(
    request: ProcessSearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Process all raw_posts from a search execution in batches
    
    - Creates batches with character limits (8000 chars per batch)
    - Processes each batch with AI
    - Stores results in categorized collections
    - Marks posts as processed
    
    **Background Processing:**
    - Set `background=true` to process asynchronously
    - Returns immediately with batch IDs
    - Check status with `/process/batch/{batch_id}/status`
    """
    try:
        mongodb = get_mongodb()
        processor = BatchProcessor(mongodb)
        
        if request.background:
            # Create batches and return immediately
            batch_ids = await processor.create_batches(
                request.search_execution_id,
                request.project_id
            )
            
            # Process in background
            for batch_id in batch_ids:
                background_tasks.add_task(processor.process_batch, batch_id)
            
            return ProcessingResponse(
                message="Batch processing started in background",
                search_execution_id=request.search_execution_id,
                total_batches=len(batch_ids),
                status="processing",
                batch_ids=batch_ids
            )
        else:
            # Process synchronously
            result = await processor.process_all_batches(request.search_execution_id)
            
            return ProcessingResponse(
                message="Batch processing completed",
                search_execution_id=request.search_execution_id,
                total_batches=result["total_batches"],
                status=result["status"],
                batch_ids=[b["batch_id"] for b in result.get("batch_results", [])]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )


@router.post("/process/batch", response_model=Dict[str, Any], summary="Process Single Batch")
async def process_single_batch(request: ProcessBatchRequest):
    """
    Process a single batch by batch ID
    
    - Fetches posts from the batch
    - Processes with AI
    - Stores in categorized collections
    - Updates batch status
    """
    try:
        mongodb = get_mongodb()
        processor = BatchProcessor(mongodb)
        
        result = await processor.process_batch(request.batch_id)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.get("/process/batch/{batch_id}/status", response_model=BatchStatusResponse, summary="Get Batch Status")
async def get_batch_status(batch_id: str):
    """
    Get the status of a batch
    
    Returns:
    - Batch status (pending, processing, completed, failed)
    - Progress (processed_posts / total_posts)
    - Timing information
    - Error message if failed
    """
    try:
        print(f"[Batch Status] Fetching status for batch: {batch_id}")
        
        mongodb = get_mongodb()
        print(f"[Batch Status] MongoDB connection obtained")
        
        batch = await mongodb.processing_batches.find_one({"batch_id": batch_id})
        
        if not batch:
            print(f"[Batch Status] Batch not found: {batch_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch not found: {batch_id}"
            )
        
        print(f"[Batch Status] Found batch with status: {batch['status']}")
        
        return BatchStatusResponse(
            batch_id=batch["batch_id"],
            status=batch["status"],
            total_posts=batch["total_posts"],
            processed_posts=batch.get("processed_posts", 0),
            failed_posts=batch.get("failed_posts", 0),
            character_count=batch["character_count"],
            created_at=batch["created_at"].isoformat(),
            started_at=batch.get("started_at").isoformat() if batch.get("started_at") else None,
            completed_at=batch.get("completed_at").isoformat() if batch.get("completed_at") else None,
            processing_time_ms=batch.get("processing_time_ms"),
            error_message=batch.get("error_message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Batch Status] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get batch status: {str(e)}"
        )


@router.get("/categories", response_model=List[CategoryResponse], summary="List All Categories")
async def list_categories(
    category_type: Optional[str] = None,
    limit: int = 100
):
    """
    List all processed categories
    
    - Filter by category_type (medicine, hospital, drug, etc.)
    - Returns category name, type, entry count, and tags
    """
    try:
        print(f"[Categories] Fetching categories with filter: {category_type}, limit: {limit}")
        
        mongodb = get_mongodb()
        print(f"[Categories] MongoDB connection obtained")
        
        query = {}
        if category_type and category_type != 'all':
            query["category_type"] = category_type
        
        print(f"[Categories] Query: {query}")
        
        cursor = mongodb.processed_categories.find(query).sort("last_updated", -1).limit(limit)
        categories = await cursor.to_list(length=limit)
        
        print(f"[Categories] Found {len(categories)} categories")
        
        result = [
            CategoryResponse(
                category_name=cat["category_name"],
                category_type=cat["category_type"],
                total_entries=cat.get("total_entries", 0),
                last_updated=cat["last_updated"].isoformat(),
                tags=cat.get("tags", [])
            )
            for cat in categories
        ]
        
        print(f"[Categories] Returning {len(result)} categories")
        return result
        
    except Exception as e:
        print(f"[Categories] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list categories: {str(e)}"
        )


@router.get("/categories/{category_name}", response_model=Dict[str, Any], summary="Get Category Details")
async def get_category_details(
    category_name: str,
    limit: int = 50
):
    """
    Get detailed information about a specific category
    
    - Returns all processed entries for the category
    - Includes AI suggestions and info
    - Limited to most recent entries
    """
    try:
        print(f"[Category Details] Fetching details for: {category_name}, limit: {limit}")
        
        mongodb = get_mongodb()
        print(f"[Category Details] MongoDB connection obtained")
        
        category = await mongodb.processed_categories.find_one({"category_name": category_name})
        
        if not category:
            print(f"[Category Details] Category not found: {category_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category not found: {category_name}"
            )
        
        print(f"[Category Details] Found category with {len(category.get('processed_entries', []))} entries")
        
        # Get most recent entries
        entries = category.get("processed_entries", [])[-limit:]
        
        # Convert ObjectIds to strings
        for entry in entries:
            entry["original_post_id"] = str(entry["original_post_id"])
            entry["processed_at"] = entry["processed_at"].isoformat()
        
        result = {
            "category_name": category["category_name"],
            "category_type": category["category_type"],
            "total_entries": category.get("total_entries", 0),
            "entries": entries,
            "tags": category.get("tags", []),
            "summary": category.get("summary", {}),
            "created_at": category["created_at"].isoformat(),
            "last_updated": category["last_updated"].isoformat()
        }
        
        print(f"[Category Details] Returning {len(entries)} entries")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Category Details] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category details: {str(e)}"
        )
