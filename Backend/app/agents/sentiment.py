"""
Module C: The Sentiment Analyst Agent
Evaluates emotional tone—distinguishing between patient frustration with a side effect vs general dissatisfaction.
"""
from app.graph.state import AgentState
from app.schemas.agent import SentimentResult
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_structured_llm

async def analyze_sentiment_node(state: AgentState) -> dict:
    """
    LangGraph Node: Sentiment Analyst
    """
    text_to_analyze = state.get("anonymized_text", "")
    keyword = state.get("keyword", "")
    
    print("--- [Sentiment Analyst] Evaluating emotional tone via Azure OpenAI ---")
    
    try:
        structured_llm = get_structured_llm(
            schema=SentimentResult,
            temperature=0.0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert sentiment analyst specializing in healthcare social media.

Analyze the emotional tone of the patient's post regarding '{keyword}'.

Provide:
- **overall**: very_negative, negative, neutral, positive, or very_positive
- **score**: -1.0 (very negative) to 1.0 (very positive)
- **emotions**: List of detected emotions (e.g., fear, anger, frustration, hope, relief)
- **emotion_scores**: Dictionary with scores for each emotion
- **confidence**: Your confidence in this analysis (0.0-1.0)
- **context**: Brief explanation of the sentiment context
- **is_patient_experience**: Whether this is a first-hand patient experience (true/false)

Differentiate between:
- General frustration (e.g., price, pharmacy queues, insurance)
- Actual side-effect complaints (physical symptoms, adverse reactions)
"""),
            ("human", "Text to analyze:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        result = await chain.ainvoke({"keyword": keyword, "text": text_to_analyze})
        
        print(f"  ✅ Sentiment: {result.overall} (score: {result.score:.2f})")
        return {"sentiment": result}
        
    except Exception as e:
        print(f"❌ Sentiment Error: {e}")
        return {"sentiment": None}
