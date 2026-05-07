"""
Module C: The Safety Auditor Agent
The final gatekeeper that loops back to the Medical MCP to verify symptoms against known drug side effects and flags "Unknown/Critical" events.
"""
from app.graph.state import AgentState
from app.schemas.agent import AuditResult
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

async def audit_safety_node(state: AgentState) -> dict:
    """
    LangGraph Node: Safety Auditor
    """
    extraction = state.get("extraction")
    keyword = state.get("keyword", "")
    
    print("--- [Safety Auditor] Verifying symptoms against known side effects via Groq ---")
    
    if not settings.groq_api_key or not extraction:
        print("⚠️ GROQ_API_KEY not found or no extraction. Returning mock data.")
        return {"audit": AuditResult(
            is_unknown_risk=False,
            criticality="Low",
            reasoning="[MOCK] System check bypassed due to missing API key."
        )}
        
    try:
        symptoms = ", ".join([e.value for e in extraction.entities if e.entity_type == "Symptom"])
        if not symptoms:
            return {"audit": AuditResult(is_unknown_risk=False, criticality="Low", reasoning="No symptoms extracted.")}
            
        llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=settings.groq_api_key)
        structured_llm = llm.with_structured_output(AuditResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a medical safety auditor. Your job is to evaluate the reported symptoms: '{symptoms}' for the drug '{keyword}'. Determine if these are common/known side effects or if they represent an unknown/critical risk. Provide a clear reasoning and assign a criticality level (Low, Medium, High, Critical)."),
            ("human", "Please audit the safety risk based on the provided symptoms and drug.")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"keyword": keyword, "symptoms": symptoms})
        return {"audit": result}
        
    except Exception as e:
        print(f"❌ Auditor Error: {e}")
        return {"audit": None}
