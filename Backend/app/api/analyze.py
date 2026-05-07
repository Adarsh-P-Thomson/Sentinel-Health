"""
API Endpoint for the Configurator and Analysis Workflow
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, Any
from app.schemas.api import MissionParameterRequest, AnalysisResponse
from app.services.analysis_service import run_safety_analysis
from app.core.database import get_mongodb

router = APIRouter(tags=["Analysis"])

@router.post("/analyze", response_model=AnalysisResponse, summary="Run Patient Safety Analysis")
async def analyze_safety_signal(request: MissionParameterRequest):
    """
    Starts the Multi-Agent pipeline to detect safety signals.
    
    - Inputs 'Mission Parameters' (Module A)
    - Fetches data via MCP Scouts (Module B)
    - Processes data via LangGraph Brain (Module C)
    - Returns actionable insights (Module D)
    """
    try:
        # Trigger the service layer
        result = await run_safety_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline failed: {str(e)}"
        )


@router.post("/analyze/latest", summary="Analyze Latest Cleaned Data (ANALYZE Button)")
async def analyze_latest_cleaned_data(background_tasks: BackgroundTasks):
    """
    **ANALYZE Button** - Send cleaned posts through AI agents for analysis
    
    This endpoint:
    1. Finds cleaned posts with status "pending" for AI analysis
    2. Creates batches (10 posts per batch)
    3. Sends each batch through the LangGraph multi-agent workflow:
       - Medical Entity Extractor
       - Sentiment Analyst
       - Trend & Virality Agent
       - Safety Auditor
    4. Stores results in `processed_categories` collection
    5. Marks posts as "analyzed"
    
    **Use after /clean/latest** to analyze the cleaned data
    """
    try:
        print("[Analyze Latest] Finding cleaned posts ready for AI analysis...")
        
        mongodb = get_mongodb()
        
        # Find cleaned posts that need AI analysis
        query = {"ai_analysis_status": "pending"}
        cursor = mongodb.cleaned_posts.find(query).sort("cleaned_at", 1)
        cleaned_posts = await cursor.to_list(length=None)
        
        if not cleaned_posts:
            return {
                "status": "no_posts_to_analyze",
                "message": "No cleaned posts found. Run /clean/latest first!",
                "total_analyzed": 0
            }
        
        print(f"[Analyze Latest] Found {len(cleaned_posts)} cleaned posts to analyze")
        
        # Create batches of 10 posts each
        batch_size = 10
        batches = []
        for i in range(0, len(cleaned_posts), batch_size):
            batch = cleaned_posts[i:i + batch_size]
            batches.append(batch)
        
        print(f"[Analyze Latest] Created {len(batches)} batches of {batch_size} posts each")
        
        # Process each batch through LangGraph workflow in background
        for batch_idx, batch in enumerate(batches):
            background_tasks.add_task(
                process_batch_with_agents,
                mongodb,
                batch,
                batch_idx + 1,
                len(batches)
            )
        
        return {
            "status": "started",
            "message": f"Started AI analysis for {len(cleaned_posts)} posts in {len(batches)} batches",
            "total_posts": len(cleaned_posts),
            "total_batches": len(batches),
            "batch_size": batch_size
        }
        
    except Exception as e:
        print(f"[Analyze Latest] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze data: {str(e)}"
        )


async def process_batch_with_agents(
    mongodb,
    batch: list,
    batch_num: int,
    total_batches: int
):
    """
    Process a batch of cleaned posts through the LangGraph agents
    
    Args:
        mongodb: MongoDB database instance
        batch: List of cleaned post documents
        batch_num: Current batch number
        total_batches: Total number of batches
    """
    print(f"\n{'='*80}")
    print(f"🤖 Processing Batch {batch_num}/{total_batches} with AI Agents")
    print(f"{'='*80}")
    
    for idx, post in enumerate(batch):
        try:
            print(f"  [{batch_num}/{total_batches}] Analyzing post {idx+1}/{len(batch)}...")
            
            # Prepare mission parameters for this post
            params = MissionParameterRequest(
                keyword="general",  # We'll extract keywords from the post
                source=post.get("source_type", "unknown"),
                raw_text=post.get("cleaned_content", "")
            )
            
            # Run through LangGraph workflow
            result = await run_safety_analysis(params)
            
            # Store the analysis results
            # TODO: Store in processed_categories collection
            
            # Mark post as analyzed
            await mongodb.cleaned_posts.update_one(
                {"_id": post["_id"]},
                {"$set": {"ai_analysis_status": "analyzed"}}
            )
            
            print(f"  ✅ Post {idx+1}/{len(batch)} analyzed successfully")
            
        except Exception as e:
            print(f"  ❌ Failed to analyze post {idx+1}/{len(batch)}: {e}")
            # Mark as failed
            await mongodb.cleaned_posts.update_one(
                {"_id": post["_id"]},
                {"$set": {"ai_analysis_status": "failed", "error": str(e)}}
            )
    
    print(f"✅ Batch {batch_num}/{total_batches} completed!")


