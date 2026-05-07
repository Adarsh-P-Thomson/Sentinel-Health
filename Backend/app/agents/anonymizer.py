"""
Module C: The Anonymizer Agent
Focuses solely on scrubbing PII/PHI (Names, Locations) to ensure HIPAA compliance.
Uses LOCAL regex-based anonymization - NO AI/LLM calls for privacy
"""
from app.graph.state import AgentState
from app.schemas.agent import AnonymizerResult
from app.utils.anonymizer import anonymize_text
from app.utils.text_cleaner import clean_text

async def anonymize_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Anonymizer Agent
    
    Purpose:
        To remove Personally Identifiable Information (PII) and Protected Health Information (PHI)
        from the raw text to ensure HIPAA compliance.
        
    Process:
        1. Clean text (remove formatting, normalize)
        2. Anonymize PII/PHI using local regex patterns (NO AI)
        
    Args:
        state (AgentState): The current state of the graph containing the 'raw_text'.
        
    Returns:
        AgentState: The updated state containing the 'anonymized_text' and anonymizer results.
    """
    raw_text = state.get("raw_text", "")
    
    print(f"--- [Anonymizer Agent] Scrubbing PII/PHI locally (no AI) from source: {state.get('source')} ---")
    
    try:
        # Step 1: Clean the text (remove formatting, normalize)
        cleaned_text = clean_text(raw_text)
        print(f"  ✓ Text cleaned: {len(raw_text)} → {len(cleaned_text)} chars")
        
        # Step 2: Anonymize PII/PHI using local regex patterns
        anonymized_text, metadata = anonymize_text(cleaned_text)
        
        print(f"  ✓ PII detected: {metadata['pii_detected']} | Types: {metadata['pii_types']}")
        print(f"  ✓ Confidence: {metadata['anonymizer_confidence']:.2f}")
        
        # Create result object
        result = AnonymizerResult(
            anonymized_content=anonymized_text,
            pii_detected=metadata["pii_detected"],
            pii_types=metadata["pii_types"],
            pii_redaction_map=metadata["pii_redaction_map"],
            anonymizer_confidence=metadata["anonymizer_confidence"]
        )
        
        return {
            "anonymized_text": anonymized_text,
            "anonymizer_result": result
        }
        
    except Exception as e:
        print(f"❌ Anonymizer Error: {e}")
        # Fallback: return cleaned text without anonymization
        cleaned = clean_text(raw_text)
        return {
            "anonymized_text": cleaned,
            "anonymizer_result": AnonymizerResult(
                anonymized_content=cleaned,
                pii_detected=False,
                pii_types=[],
                pii_redaction_map={},
                anonymizer_confidence=0.5
            )
        }
