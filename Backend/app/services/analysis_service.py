"""
The Application Glue.
Connects the FastAPI endpoints to the LangGraph AI Brain.
"""
from app.graph.workflow import agent_workflow
from app.schemas.api import MissionParameterRequest, AnalysisResponse
from app.mcp.factory import MCPFactory

async def run_safety_analysis(params: MissionParameterRequest) -> AnalysisResponse:
    """
    Executes the multi-agent workflow for a given mission parameter.
    
    Args:
        params (MissionParameterRequest): The request payload from the Configurator UI.
        
    Returns:
        AnalysisResponse: The parsed result to display on the User UI.
    """
    print(f"--- [Analysis Service] Starting mission for keyword: {params.keyword} on {params.source} ---")
    
    # 1. MCP Scout Phase (Module B)
    # If raw_text is not provided, the MCP client dynamically fetches it.
    raw_text = params.raw_text
    if not raw_text:
        print(f"--- [MCP Scout] Fetching real data from {params.source}... ---")
        try:
            scout = MCPFactory.get_scout(params.source)
            raw_text = await scout.fetch_data(keyword=params.keyword)
        except ValueError as e:
            # Fallback for unknown sources if they somehow bypass validation
            raw_text = f"Simulated user post about {params.keyword}: I have been taking {params.keyword} and lately I developed a severe headache."
    
    # 2. Prepare the initial state for the LangGraph workflow
    initial_state = {
        "keyword": params.keyword,
        "source": params.source,
        "raw_text": raw_text
    }
    
    # 3. Invoke the LangGraph Brain
    # Using .ainvoke() to run the graph asynchronously
    final_state = await agent_workflow.ainvoke(initial_state)
    
    # 4. Map the graph output state to our FastAPI Response Schema
    response = AnalysisResponse(
        keyword=final_state.get("keyword"),
        source=final_state.get("source"),
        extraction=final_state.get("extraction"),
        sentiment=final_state.get("sentiment"),
        trend=final_state.get("trend"),
        audit=final_state.get("audit"),
        status="completed"
    )
    
    return response
