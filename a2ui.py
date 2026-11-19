"""
A2UI-style structured component specification and Streamlit renderer.

The LLM creates travel content. This module maps validated structured data
to a safe, deterministic Streamlit component tree. It does not execute
arbitrary HTML or arbitrary model-generated code.
"""

from typing import Any
from pydantic import BaseModel, Field, ValidationError
import streamlit as st

class A2UICard(BaseModel):
    title: str = Field(max_length=100)
    value: str = Field(max_length=500)
    description: str = Field(default="", max_length=500)

class A2UISection(BaseModel):
    title: str = Field(max_length=120)
    content: str = Field(max_length=12000)

class A2UISpec(BaseModel):
    version: str = "1.0"
    title: str = "AI Travel Dashboard"
    summary: str = ""
    cards: list[A2UICard] = Field(default_factory=list, max_length=8)
    sections: list[A2UISection] = Field(default_factory=list, max_length=10)

def build_ui_spec(result: dict[str, Any]) -> dict[str, Any]:
    destination = str(result.get("destination", "Your destination"))
    days = int(result.get("days", 0))
    travelers = int(result.get("travelers", 0))
    budget = float(result.get("budget", 0))

    spec = {
        "version": "1.0",
        "title": f"{destination} Travel Dashboard",
        "summary": (
            f"AI-generated {days}-day travel plan for {travelers} traveller(s). "
            f"Target budget: ₹{budget:,.0f}. Estimates and recommendations "
            "should be independently verified before booking."
        ),
        "cards": [
            {"title": "Destination", "value": destination, "description": "Selected travel destination"},
            {"title": "Duration", "value": f"{days} days", "description": "Planned trip duration"},
            {"title": "Travellers", "value": str(travelers), "description": "Number of travellers"},
            {"title": "Target budget", "value": f"₹{budget:,.0f}", "description": "User-provided budget"},
        ],
        "sections": [
            {"title": "Destination research", "content": result.get("research", "")},
            {"title": "Day-wise itinerary", "content": result.get("itinerary", "")},
            {"title": "Budget analysis", "content": result.get("budget_analysis", "")},
            {"title": "Recommendations", "content": result.get("recommendations", "")},
        ],
    }

    try:
        return A2UISpec.model_validate(spec).model_dump()
    except ValidationError:
        # Fallback keeps UI generation deterministic if model output/data is malformed.
        return A2UISpec(
            title=f"{destination} Travel Dashboard",
            summary="Travel plan generated. Some dashboard fields could not be validated.",
        ).model_dump()

def render_a2ui(spec: dict[str, Any]) -> None:
    """Render the validated A2UI specification as native Streamlit components."""
    try:
        ui = A2UISpec.model_validate(spec)
    except ValidationError as exc:
        st.error("Invalid A2UI specification.")
        st.code(str(exc))
        return

    st.subheader(ui.title)
    if ui.summary:
        st.info(ui.summary)

    if ui.cards:
        cols = st.columns(min(4, len(ui.cards)))
        for index, card in enumerate(ui.cards):
            with cols[index % len(cols)]:
                st.metric(card.title, card.value)
                if card.description:
                    st.caption(card.description)

    for section in ui.sections:
        with st.expander(section.title, expanded=section.title == "Day-wise itinerary"):
            st.markdown(section.content or "_No content generated._")
