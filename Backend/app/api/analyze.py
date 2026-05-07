"""
API Endpoint for the Configurator and Analysis Workflow
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.api import MissionParameterRequest, AnalysisResponse
from app.services.analysis_service import run_safety_analysis

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
