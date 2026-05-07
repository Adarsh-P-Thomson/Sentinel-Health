"""
Module C: The Sentiment Analyst Agent
Evaluates emotional tone—distinguishing between patient frustration with a side effect vs general dissatisfaction.
"""
from app.graph.state import AgentState
from app.schemas.agent import SentimentResult
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

async def analyze_sentiment_node(state: AgentState) -> dict:
    """
    LangGraph Node: Sentiment Analyst
    """
    text_to_analyze = state.get("anonymized_text", "")
    keyword = state.get("keyword", "")
    
    print("--- [Sentiment Analyst] Evaluating emotional tone via Groq ---")
    
    if not settings.groq_api_key:
        print("⚠️ GROQ_API_KEY not found. Returning mock data.")
        return {"sentiment": SentimentResult(
            emotional_tone="[MOCK] Frustrated",
            is_dissatisfaction=True,
            is_side_effect_complaint=False,
            confidence_score=0.9
        )}
        
    try:
        llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=settings.groq_api_key)
        structured_llm = llm.with_structured_output(SentimentResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert sentiment analyst specializing in healthcare. Evaluate the emotional tone of the patient's post regarding '{keyword}'. Differentiate between general frustration (e.g., price, pharmacy queues) and actual side-effect complaints."),
            ("human", "Text to analyze:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"keyword": keyword, "text": text_to_analyze})
        return {"sentiment": result}
        
    except Exception as e:
        print(f"❌ Sentiment Error: {e}")
        return {"sentiment": None}
