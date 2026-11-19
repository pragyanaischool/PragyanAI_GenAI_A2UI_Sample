from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from agents import (
    destination_agent,
    itinerary_agent,
    budget_agent,
    recommendation_agent,
)
from tools import get_destination_info, estimate_travel_cost

class TravelState(TypedDict, total=False):
    destination: str
    days: int
    travelers: int
    budget: float
    preferences: str
    destination_info: dict
    mcp_estimate: dict
    research: str
    itinerary: str
    budget_analysis: str
    recommendations: str
    errors: list[str]

def build_travel_graph(settings):
    def tools_node(state: TravelState):
        # MCP-tool layer: deterministic tool functions are called before the agents.
        info = get_destination_info(state["destination"])
        estimate = estimate_travel_cost(
            state["destination"], state["travelers"], state["days"]
        )
        return {"destination_info": info, "mcp_estimate": estimate}

    def research_node(state: TravelState):
        return {"research": destination_agent(state, settings)}

    def itinerary_node(state: TravelState):
        return {"itinerary": itinerary_agent(state, settings)}

    def budget_node(state: TravelState):
        return {"budget_analysis": budget_agent(state, settings)}

    def recommendation_node(state: TravelState):
        return {"recommendations": recommendation_agent(state, settings)}

    workflow = StateGraph(TravelState)
    workflow.add_node("travel_tools", tools_node)
    workflow.add_node("destination_agent", research_node)
    workflow.add_node("itinerary_agent", itinerary_node)
    workflow.add_node("budget_agent", budget_node)
    workflow.add_node("recommendation_agent", recommendation_node)

    workflow.add_edge(START, "travel_tools")
    workflow.add_edge("travel_tools", "destination_agent")
    workflow.add_edge("destination_agent", "itinerary_agent")
    workflow.add_edge("itinerary_agent", "budget_agent")
    workflow.add_edge("budget_agent", "recommendation_agent")
    workflow.add_edge("recommendation_agent", END)

    return workflow.compile()
