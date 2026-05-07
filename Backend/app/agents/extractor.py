"""
Module C: The Medical Entity Extractor Agent
Specialist in identifying drugs, dosages, and symptoms from messy, slang-heavy social text.
"""
from app.graph.state import AgentState
from app.schemas.agent import MedicalExtractionResult, ExtractedEntity
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

async def extract_entities_node(state: AgentState) -> dict:
    """
    LangGraph Node: Medical Entity Extractor
    """
    text_to_analyze = state.get("anonymized_text", "")
    keyword = state.get("keyword", "")
    
    print("--- [Medical Entity Extractor] Identifying drugs and symptoms via Groq ---")
    
    if not settings.groq_api_key:
        print("⚠️ GROQ_API_KEY not found. Returning mock data.")
        mock_result = MedicalExtractionResult(
            entities=[ExtractedEntity(entity_type="Drug", value=keyword, confidence=0.95)],
            summary="[MOCK] User reported an issue."
        )
        return {"extraction": mock_result}
    
    try:
        llm = ChatGroq(
            temperature=0,
            model_name="llama3-70b-8192",
            api_key=settings.groq_api_key
        )
        structured_llm = llm.with_structured_output(MedicalExtractionResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert medical data extractor. Extract any mentioned drugs, dosages, and medical symptoms from the provided text. Ensure high accuracy. The target keyword for this monitoring session is '{keyword}'."),
            ("human", "Text to analyze:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"keyword": keyword, "text": text_to_analyze})
        
        return {"extraction": result}
        
    except Exception as e:
        print(f"❌ Extractor Error: {e}")
        return {"extraction": None}
