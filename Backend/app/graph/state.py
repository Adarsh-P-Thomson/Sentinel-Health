"""
LangGraph state definition.
This defines the 'memory' object passed between nodes (agents) during the workflow execution.
"""
from typing import TypedDict, Annotated, List, Optional
from app.schemas.agent import MedicalExtractionResult, SentimentResult, TrendResult, AuditResult
import operator

def merge_list(a: list, b: list) -> list:
    return a + b

class AgentState(TypedDict):
    """
    Represents the state of the multi-agent workflow.
    Each agent reads from and writes to this state.
    """
    keyword: str                  # The target keyword being monitored
    source: str                   # Data source (e.g., Reddit, X)
    raw_text: str                 # The original text fetched by the MCP Scout
    
    anonymized_text: Optional[str] # Text after PII/PHI scrubbing
    
    extraction: Optional[MedicalExtractionResult] # Entities identified by Extractor
    sentiment: Optional[SentimentResult]          # Tone evaluated by Sentiment Analyst
    trend: Optional[TrendResult]                  # Virality metrics evaluated by Trend Agent
    audit: Optional[AuditResult]                  # Final safety verification by Auditor
    
    # Example of a reducer, to append errors to a list over the workflow
    errors: Annotated[List[str], operator.add]
