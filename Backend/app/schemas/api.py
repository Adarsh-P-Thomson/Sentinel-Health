"""
Pydantic schemas for the FastAPI endpoints.
These define the JSON payload for incoming requests and outgoing responses.
"""
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.agent import MedicalExtractionResult, SentimentResult, TrendResult, AuditResult

class MissionParameterRequest(BaseModel):
    """
    Module A: The Configurator payload.
    Admin defines the target keywords, interval, and data sources.
    """
    keyword: str = Field(..., description="Target keyword (e.g., Drug-Y)")
    source: str = Field(..., description="Data source to monitor (e.g., Reddit, X)")
    raw_text: Optional[str] = Field(None, description="Optional raw text for testing. If omitted, MCP will fetch data.")

class AnalysisResponse(BaseModel):
    """
    Module D: The Outcome payload.
    The response sent back to the User UI Dashboard.
    """
    keyword: str
    source: str
    extraction: Optional[MedicalExtractionResult] = None
    sentiment: Optional[SentimentResult] = None
    trend: Optional[TrendResult] = None
    audit: Optional[AuditResult] = None
    status: str = Field(description="Processing status (e.g., 'completed', 'failed')")
