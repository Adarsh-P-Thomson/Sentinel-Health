"""
Module C: The Trend & Virality Agent
Checks engagement metrics to determine if a specific safety signal is "Trending" or has "High Viral Potential".
"""
from app.graph.state import AgentState
from app.schemas.agent import TrendResult
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_structured_llm

async def check_trend_node(state: AgentState) -> dict:
    """
    LangGraph Node: Trend & Virality Agent
    """
    raw_text = state.get("raw_text", "")
    
    print("--- [Trend & Virality Agent] Analyzing engagement metrics via Azure OpenAI ---")
    
    try:
        structured_llm = get_structured_llm(
            schema=TrendResult,
            temperature=0.0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a social media virality expert specializing in health-related content.

Analyze the post for viral potential and trending indicators.

Provide:
- **score**: Virality score from 0-100
- **trend**: rising, stable, declining, or viral
- **engagement_rate**: Estimated engagement rate (0.0-1.0)
- **viral_potential**: low, medium, high, or critical
- **velocity**: Rate of engagement growth (0.0-1.0)
- **similar_posts_count**: Estimated number of similar posts (0-1000+)
- **is_trending**: Whether this topic is currently trending (true/false)

Consider:
- Urgency and emotional tone of the content
- Potential for sharing (shocking, relatable, actionable)
- Medical/safety implications
- Community engagement markers
- Time-sensitive nature
"""),
            ("human", "Post Content:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"text": raw_text})
        
        print(f"  ✅ Trend: {result.trend} (viral potential: {result.viral_potential})")
        return {"trend": result}
        
    except Exception as e:
        print(f"❌ Trend Error: {e}")
        return {"trend": None}
