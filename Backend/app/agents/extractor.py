"""
Module C: The Medical Entity Extractor Agent
Specialist in identifying drugs, dosages, and symptoms from messy, slang-heavy social text.
"""
from app.graph.state import AgentState
from app.schemas.agent import MedicalExtractionResult, ExtractedEntities
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_structured_llm

async def extract_entities_node(state: AgentState) -> dict:
    """
    LangGraph Node: Medical Entity Extractor
    """
    text_to_analyze = state.get("anonymized_text", "")
    keyword = state.get("keyword", "")
    
    print("--- [Medical Entity Extractor] Identifying drugs and symptoms via Azure OpenAI ---")
    
    try:
        # Get Azure OpenAI LLM with structured output
        structured_llm = get_structured_llm(
            schema=MedicalExtractionResult,
            temperature=0.0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert medical data extractor specializing in social media posts.
            
Extract the following from the text:
- **Drugs**: Include name, generic_name, brand_name, dosage, frequency, duration, route, confidence, context
- **Symptoms**: Include name, severity (mild/moderate/severe/critical), onset, duration, confidence, context
- **Conditions**: Include name, icd_code (if known), confidence, context
- **Procedures**: Include name, confidence

The target keyword for this monitoring session is '{keyword}'.
Be thorough but accurate. If information is not mentioned, leave fields empty.
"""),
            ("human", "Text to analyze:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"keyword": keyword, "text": text_to_analyze})
        
        print(f"  ✅ Extracted: {len(result.entities.drugs) + len(result.entities.symptoms)} entities")
        return {"extraction": result}
        
    except Exception as e:
        print(f"❌ Extractor Error: {e}")
        # Return proper empty result with correct structure
        return {
            "extraction": MedicalExtractionResult(
                entities=ExtractedEntities(
                    drugs=[],
                    symptoms=[],
                    conditions=[],
                    procedures=[]
                ),
                entity_extraction_confidence=0.0,
                summary="Extraction failed due to error"
            )
        }
