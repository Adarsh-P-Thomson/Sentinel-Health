"""
Module C: The Safety Auditor Agent
The final gatekeeper that loops back to the Medical MCP to verify symptoms against known drug side effects and flags "Unknown/Critical" events.
"""
from app.graph.state import AgentState
from app.schemas.agent import AuditResult
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_structured_llm

async def audit_safety_node(state: AgentState) -> dict:
    """
    LangGraph Node: Safety Auditor
    """
    extraction = state.get("extraction")
    keyword = state.get("keyword", "")
    
    print("--- [Safety Auditor] Verifying symptoms against known side effects via Azure OpenAI ---")
    
    if not extraction or not extraction.entities:
        print("⚠️ No extraction data. Skipping audit.")
        return {"audit": AuditResult(
            is_adverse_event=False,
            severity="low",
            known_side_effect=False,
            requires_investigation=False,
            confidence=0.0,
            risk_category="no_risk",
            reasoning="No entities extracted to audit."
        )}
        
    try:
        # Extract symptoms from entities
        symptoms = ", ".join([
            e.value for e in extraction.entities 
            if e.entity_type.lower() == "symptom"
        ])
        
        if not symptoms:
            return {"audit": AuditResult(
                is_adverse_event=False,
                severity="low",
                known_side_effect=False,
                requires_investigation=False,
                confidence=1.0,
                risk_category="no_risk",
                reasoning="No symptoms reported."
            )}
            
        structured_llm = get_structured_llm(
            schema=AuditResult,
            temperature=0.0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical safety auditor specializing in pharmacovigilance.

Evaluate the reported symptoms: '{symptoms}' for the drug '{keyword}'.

Determine:
- **is_adverse_event**: Is this an adverse drug event? (true/false)
- **severity**: low, medium, high, or critical
- **known_side_effect**: Are these known/documented side effects? (true/false)
- **requires_investigation**: Does this require immediate investigation? (true/false)
- **confidence**: Your confidence in this assessment (0.0-1.0)
- **risk_category**: no_risk, low_risk, moderate_risk, high_risk, or critical_risk
- **reasoning**: Clear explanation of your decision

Consider:
- Severity of symptoms
- Whether symptoms are commonly associated with this drug
- Potential for serious harm
- Need for regulatory reporting
"""),
            ("human", "Please audit the safety risk based on the provided symptoms and drug.")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"keyword": keyword, "symptoms": symptoms})
        
        print(f"  ✅ Audit: {result.risk_category} (severity: {result.severity})")
        return {"audit": result}
        
    except Exception as e:
        print(f"❌ Auditor Error: {e}")
        return {"audit": None}
