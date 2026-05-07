"""
Pydantic schemas used for agent outputs and internal graph state management.
These schemas help validate the output of LLMs and maintain structure throughout the LangGraph workflow.
Updated to match MongoDB analyzed_posts schema.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# ANONYMIZER SCHEMAS
# ============================================================================

class AnonymizerResult(BaseModel):
    """Schema for the output of the Anonymizer agent."""
    anonymized_content: str = Field(description="Content with PII/PHI removed")
    pii_detected: bool = Field(description="Whether PII was found and removed")
    pii_types: List[str] = Field(default_factory=list, description="Types of PII found (name, email, phone, location, etc.)")
    pii_redaction_map: Dict[str, str] = Field(default_factory=dict, description="Mapping of redacted entities for potential reversal")
    anonymizer_confidence: float = Field(description="Confidence that all PII was removed (0.0-1.0)")


# ============================================================================
# EXTRACTOR SCHEMAS
# ============================================================================

class DrugEntity(BaseModel):
    """Extracted drug information"""
    name: str = Field(description="Drug name as mentioned")
    generic_name: Optional[str] = Field(default=None, description="Generic/chemical name")
    brand_name: Optional[str] = Field(default=None, description="Brand name")
    dosage: Optional[str] = Field(default=None, description="Dosage amount (e.g., '50mg')")
    frequency: Optional[str] = Field(default=None, description="How often taken (e.g., 'twice daily')")
    duration: Optional[str] = Field(default=None, description="How long taken (e.g., '2 weeks')")
    route: Optional[str] = Field(default=None, description="Route of administration (e.g., 'oral', 'IV')")
    confidence: float = Field(description="Confidence score (0.0-1.0)")
    context: Optional[str] = Field(default=None, description="Context from the text")


class SymptomSeverity(str, Enum):
    """Symptom severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class SymptomEntity(BaseModel):
    """Extracted symptom information"""
    name: str = Field(description="Symptom name")
    severity: Optional[SymptomSeverity] = Field(default=None, description="Severity level")
    onset: Optional[str] = Field(default=None, description="When it started (e.g., 'after 2 days')")
    duration: Optional[str] = Field(default=None, description="How long it lasted")
    confidence: float = Field(description="Confidence score (0.0-1.0)")
    context: Optional[str] = Field(default=None, description="Context from the text")


class ConditionEntity(BaseModel):
    """Extracted medical condition"""
    name: str = Field(description="Condition name")
    icd_code: Optional[str] = Field(default=None, description="ICD-10 code if known")
    confidence: float = Field(description="Confidence score (0.0-1.0)")
    context: Optional[str] = Field(default=None, description="Context from the text")


class ProcedureEntity(BaseModel):
    """Extracted medical procedure"""
    name: str = Field(description="Procedure name")
    confidence: float = Field(description="Confidence score (0.0-1.0)")


class ExtractedEntities(BaseModel):
    """All extracted medical entities"""
    drugs: List[DrugEntity] = Field(default_factory=list, description="Extracted drugs")
    symptoms: List[SymptomEntity] = Field(default_factory=list, description="Extracted symptoms")
    conditions: List[ConditionEntity] = Field(default_factory=list, description="Extracted conditions")
    procedures: List[ProcedureEntity] = Field(default_factory=list, description="Extracted procedures")


class MedicalExtractionResult(BaseModel):
    """Schema for the output of the Medical Entity Extractor agent."""
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities, description="Extracted medical entities")
    entity_extraction_confidence: float = Field(default=0.0, description="Overall confidence in entity extraction")
    summary: str = Field(description="A brief summary of the medical context identified")


# ============================================================================
# SENTIMENT SCHEMAS
# ============================================================================

class SentimentOverall(str, Enum):
    """Overall sentiment classification"""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class SentimentResult(BaseModel):
    """Schema for the output of the Sentiment Analyst agent."""
    overall: SentimentOverall = Field(description="Overall sentiment classification")
    score: float = Field(description="Sentiment score (-1.0 to 1.0)")
    emotions: List[str] = Field(default_factory=list, description="Detected emotions (e.g., fear, anger, frustration)")
    emotion_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for each emotion")
    confidence: float = Field(description="Confidence in sentiment analysis (0.0-1.0)")
    context: str = Field(description="Context of sentiment (frustration with side effect vs general dissatisfaction)")
    is_patient_experience: bool = Field(description="Whether this is a first-hand patient experience")


# ============================================================================
# TREND SCHEMAS
# ============================================================================

class TrendClassification(str, Enum):
    """Trend classification"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    VIRAL = "viral"


class ViralPotential(str, Enum):
    """Viral potential levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendResult(BaseModel):
    """Schema for the output of the Trend & Virality agent."""
    score: float = Field(description="Virality score (0-100)")
    trend: TrendClassification = Field(description="Trend classification")
    engagement_rate: float = Field(description="Engagement rate (0.0-1.0)")
    viral_potential: ViralPotential = Field(description="Potential for going viral")
    velocity: float = Field(description="Rate of engagement growth (0.0-1.0)")
    similar_posts_count: int = Field(default=0, description="Number of similar posts found in timeframe")
    is_trending: bool = Field(description="Whether this topic is currently trending")


# ============================================================================
# AUDITOR SCHEMAS
# ============================================================================

class SeverityLevel(str, Enum):
    """Severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Risk category classification"""
    NO_RISK = "no_risk"
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"


class AuditResult(BaseModel):
    """Schema for the output of the Safety Auditor agent."""
    is_adverse_event: bool = Field(description="Whether this is an adverse drug event")
    severity: SeverityLevel = Field(description="Severity of safety concern")
    known_side_effect: bool = Field(description="Whether symptom is a known side effect")
    requires_investigation: bool = Field(description="Whether this requires immediate investigation")
    confidence: float = Field(description="Confidence in safety assessment (0.0-1.0)")
    risk_category: RiskCategory = Field(description="Risk category classification")
    reasoning: str = Field(description="Explanation of the audit decision")


# ============================================================================
# LEGACY SCHEMAS (for backward compatibility)
# ============================================================================

class ExtractedEntity(BaseModel):
    """Legacy schema - kept for backward compatibility"""
    entity_type: str = Field(description="The type of entity, e.g., 'Drug', 'Symptom', 'Dosage'")
    value: str = Field(description="The actual value extracted from the text")
    confidence: float = Field(description="Confidence score of the extraction between 0.0 and 1.0")
