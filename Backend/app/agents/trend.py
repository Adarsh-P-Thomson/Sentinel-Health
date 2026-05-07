"""
Module C: The Trend & Virality Agent
Checks engagement metrics to determine if a specific safety signal is "Trending" or has "High Viral Potential".
"""
from app.graph.state import AgentState
from app.schemas.agent import TrendResult
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

async def check_trend_node(state: AgentState) -> dict:
    """
    LangGraph Node: Trend & Virality Agent
    """
    raw_text = state.get("raw_text", "")
    
    print("--- [Trend & Virality Agent] Analyzing engagement metrics via Groq ---")
    
    if not settings.groq_api_key:
        print("⚠️ GROQ_API_KEY not found. Returning mock data.")
        return {"trend": TrendResult(
            is_trending=False,
            virality_score=0.5,
            engagement_metrics_summary="[MOCK] Moderate engagement."
        )}
        
    try:
        llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", api_key=settings.groq_api_key)
        structured_llm = llm.with_structured_output(TrendResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a social media virality expert. Based on the text provided, evaluate if the post shows signs of going viral or trending (e.g. mentions of high upvotes, retweets, urgent tone). Note: Since we only have raw text, estimate based on the content's urgency and engagement markers if present."),
            ("human", "Post Content:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"text": raw_text})
        return {"trend": result}
        
    except Exception as e:
        print(f"❌ Trend Error: {e}")
        return {"trend": None}
