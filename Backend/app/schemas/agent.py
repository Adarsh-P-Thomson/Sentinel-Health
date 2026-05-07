"""
Pydantic schemas used for agent outputs and internal graph state management.
These schemas help validate the output of LLMs and maintain structure throughout the LangGraph workflow.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedEntity(BaseModel):
    """Schema representing an extracted medical entity."""
    entity_type: str = Field(description="The type of entity, e.g., 'Drug', 'Symptom', 'Dosage'")
    value: str = Field(description="The actual value extracted from the text")
    confidence: float = Field(description="Confidence score of the extraction between 0.0 and 1.0")

class MedicalExtractionResult(BaseModel):
    """Schema for the output of the Medical Entity Extractor agent."""
    entities: List[ExtractedEntity] = Field(default_factory=list, description="List of extracted entities")
    summary: str = Field(description="A brief summary of the medical context identified")

class SentimentResult(BaseModel):
    """Schema for the output of the Sentiment Analyst agent."""
    emotional_tone: str = Field(description="Overall emotional tone (e.g., Frustration, Concern, Neutral)")
    is_dissatisfaction: bool = Field(description="Whether the tone indicates general dissatisfaction")
    is_side_effect_complaint: bool = Field(description="Whether the tone indicates a specific complaint about a side effect")
    confidence_score: float = Field(description="Confidence score of the sentiment analysis")

class TrendResult(BaseModel):
    """Schema for the output of the Trend & Virality agent."""
    is_trending: bool = Field(description="Is the signal currently trending?")
    virality_score: float = Field(description="Score from 0.0 to 1.0 indicating viral potential")
    engagement_metrics_summary: str = Field(description="Summary of engagement metrics")

class AuditResult(BaseModel):
    """Schema for the output of the Safety Auditor agent."""
    is_unknown_risk: bool = Field(description="Whether the identified symptoms are unknown side effects for the drug")
    criticality: str = Field(description="Criticality level: 'Low', 'Medium', 'High', 'Critical'")
    reasoning: str = Field(description="Explanation of the audit decision")
