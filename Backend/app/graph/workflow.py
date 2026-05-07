"""
LangGraph Workflow Orchestration
This compiles all the specialized agents into a cohesive, sequential graph.
"""
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.agents.anonymizer import anonymize_node
from app.agents.extractor import extract_entities_node
from app.agents.sentiment import analyze_sentiment_node
from app.agents.trend import check_trend_node
from app.agents.auditor import audit_safety_node

def create_workflow():
    """
    Creates and compiles the Multi-Agent LangGraph workflow for processing
    patient safety signals.
    
    Flow:
    Input -> Anonymizer -> Extractor -> Sentiment -> Trend -> Auditor -> END
    """
    # 1. Initialize the StateGraph with our custom AgentState
    workflow = StateGraph(AgentState)
    
    # 2. Add all the specialized agent nodes to the graph
    workflow.add_node("anonymizer", anonymize_node)
    workflow.add_node("extractor", extract_entities_node)
    workflow.add_node("sentiment", analyze_sentiment_node)
    workflow.add_node("trend", check_trend_node)
    workflow.add_node("auditor", audit_safety_node)
    
    # 3. Define the edges (the flow of execution)
    workflow.set_entry_point("anonymizer")
    
    # Linear flow for now based on Idea.md processing pipeline
    workflow.add_edge("anonymizer", "extractor")
    workflow.add_edge("extractor", "sentiment")
    workflow.add_edge("sentiment", "trend")
    workflow.add_edge("trend", "auditor")
    workflow.add_edge("auditor", END)
    
    # 4. Compile the graph
    app = workflow.compile()
    
    return app

# Expose a compiled instance of the graph
agent_workflow = create_workflow()
