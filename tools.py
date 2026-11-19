"""
Travel tools used by the LangGraph workflow.

These are deterministic local tools that demonstrate the MCP tool layer.
They are deliberately labelled as sample estimates, not live travel data.
The functions can later be exposed through a FastMCP server without changing
the agent prompts or Streamlit UI.
"""

from typing import Any

DESTINATIONS = {
    "kerala": {
        "region": "South India",
        "highlights": ["Munnar", "Alappuzha backwaters", "Fort Kochi", "Thekkady"],
        "known_for": ["Hill stations", "Backwaters", "Cuisine", "Wildlife"],
    },
    "goa": {
        "region": "West India",
        "highlights": ["Panaji", "Old Goa", "South Goa beaches", "Chapora area"],
        "known_for": ["Beaches", "Portuguese heritage", "Seafood", "Water activities"],
    },
    "karnataka": {
        "region": "South India",
        "highlights": ["Mysuru", "Hampi", "Coorg", "Chikkamagaluru"],
        "known_for": ["Heritage", "Coffee estates", "Nature", "Architecture"],
    },
}

def get_destination_info(destination: str) -> dict[str, Any]:
    """Return illustrative destination context for supported sample destinations."""
    key = destination.strip().lower()
    return DESTINATIONS.get(key, {
        "region": "Not available in local sample dataset",
        "highlights": [],
        "known_for": [],
        "note": "The LLM research agent can still provide general planning suggestions.",
    })

def estimate_travel_cost(destination: str, travelers: int, days: int) -> dict[str, Any]:
    """Return a simple illustrative baseline estimate in INR, not a live quote."""
    travelers = max(1, int(travelers))
    days = max(1, int(days))
    # Explicit demo assumptions; replace with real supplier/booking APIs for production.
    per_person_per_day = 2200
    estimated_total = travelers * days * per_person_per_day
    return {
        "destination": destination,
        "travelers": travelers,
        "days": days,
        "illustrative_per_person_per_day_inr": per_person_per_day,
        "illustrative_total_inr": estimated_total,
        "disclaimer": "Sample estimate only; not a live quote or booking price.",
    }

def calculate_trip_budget(transport: float, accommodation: float, food: float,
                          activities: float, local_transport: float,
                          miscellaneous: float) -> dict[str, float]:
    """Calculate a trip total from user-supplied cost estimates."""
    items = {
        "transport": float(transport),
        "accommodation": float(accommodation),
        "food": float(food),
        "activities": float(activities),
        "local_transport": float(local_transport),
        "miscellaneous": float(miscellaneous),
    }
    return {**items, "total": round(sum(items.values()), 2)}
