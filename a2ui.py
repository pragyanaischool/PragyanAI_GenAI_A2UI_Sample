from typing import Any
from pydantic import BaseModel, Field, ValidationError
import streamlit as st
import re

# A2UI-style schema: model/data describes components; renderer maps only
# approved component types to native Streamlit widgets.
class A2UIComponent(BaseModel):
    type: str
    title: str = ""
    value: str = ""
    description: str = ""
    content: str = ""
    items: list[str] = Field(default_factory=list)
    data: dict[str, float] = Field(default_factory=dict)

class A2UISpec(BaseModel):
    version: str = "1.1"
    title: str = "AI Travel Dashboard"
    subtitle: str = ""
    theme: str = "ocean"
    layout: str = "wide"
    components: list[A2UIComponent] = Field(default_factory=list, max_length=30)

def _clean(value: Any, limit: int = 12000) -> str:
    """Convert generated content to bounded plain text/Markdown."""
    if value is None:
        return ""
    return str(value)[:limit]


def _extract_budget_numbers(text: Any) -> dict[str, float]:
    """Safely extract INR category amounts; return {} if no usable values exist."""
    if not isinstance(text, str) or not text.strip():
        return {}

    labels = {
        "Transport": r"(?:intercity\s+)?transport",
        "Accommodation": r"accommodation|hotel|stay",
        "Food": r"food|meals",
        "Local transport": r"local\s+transport",
        "Activities": r"activities|entry\s+fees",
        "Miscellaneous": r"miscellaneous|buffer",
    }
    result: dict[str, float] = {}

    for label, pattern in labels.items():
        # Accept common formats: ₹12,500; INR 12500; 12500
        # The amount is a named group, so other regex groups cannot shift its index.
        amount_pattern = (
            r"(?:" + pattern + r")"
            r"[^₹\n]{0,80}?"
            r"(?:₹|INR\s*)?\s*(?P<amount>\d[\d,]*(?:\.\d+)?)"
        )
        match = re.search(amount_pattern, text, flags=re.IGNORECASE)

        if not match:
            continue

        raw_amount = match.groupdict().get("amount")
        if not raw_amount:
            continue

        try:
            value = float(raw_amount.replace(",", ""))
        except (TypeError, ValueError):
            continue

        if value >= 0:
            result[label] = value

    return result

def build_ui_spec(result: dict[str, Any]) -> dict[str, Any]:
    destination = _clean(result.get("destination", "Your destination"), 100)
    days = int(result.get("days", 0))
    travelers = int(result.get("travelers", 0))
    budget = float(result.get("budget", 0))

    research = _clean(result.get("research", ""))
    itinerary = _clean(result.get("itinerary", ""))
    budget_text = _clean(result.get("budget_analysis", ""))
    recommendations = _clean(result.get("recommendations", ""))

    # Component selection is data-driven. Add/remove/reorder components here
    # without changing the renderer.
    components = [
        {
            "type": "metric_grid",
            "title": "Your trip at a glance",
            "items": [
                f"Destination|{destination}|Selected destination",
                f"Duration|{days} days|Travel duration",
                f"Travellers|{travelers}|Number of people",
                f"Budget|₹{budget:,.0f}|Your target budget",
            ],
        },
        {
            "type": "hero",
            "title": f"Your {destination} escape",
            "description": (
                f"A personalized {days}-day travel plan for {travelers} "
                "traveller(s), shaped around your preferences."
            ),
        },
        {
            "type": "timeline",
            "title": "Day-wise itinerary",
            "content": itinerary or "No itinerary was generated.",
        },
        {
            "type": "budget",
            "title": "Budget intelligence",
            "content": budget_text or "No budget analysis was generated.",
            "data": _extract_budget_numbers(budget_text),
        },
        {
            "type": "markdown",
            "title": "Destination insights",
            "content": research or "No destination research was generated.",
        },
        {
            "type": "recommendations",
            "title": "Curated recommendations",
            "content": recommendations or "No recommendations were generated.",
        },
        {
            "type": "notice",
            "title": "Before you book",
            "content": (
                "AI-generated suggestions and sample estimates are not live "
                "quotes, confirmed availability, reservations or bookings. "
                "Verify current prices, opening hours, transport and local "
                "travel guidance before departure."
            ),
        },
    ]

    spec = {
        "version": "1.1",
        "title": f"{destination} Travel Studio",
        "subtitle": "An adaptive travel dashboard generated from your agent workflow",
        "theme": "ocean",
        "layout": "wide",
        "components": components,
    }
    return A2UISpec.model_validate(spec).model_dump()

def inject_a2ui_css():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1320px;}
        [data-testid="stAppViewContainer"] {
            background:
              radial-gradient(ellipse at 10% 0%, rgba(14,165,233,.12), transparent 35%),
              radial-gradient(ellipse at 95% 10%, rgba(99,102,241,.10), transparent 32%);
        }
        .a2ui-eyebrow {color:#0ea5e9; font-size:.76rem; font-weight:800;
            letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem;}
        .a2ui-hero {padding:1.6rem 1.8rem; border-radius:22px; color:white;
            background:linear-gradient(120deg,#0f3b5b 0%,#075985 48%,#4f46a5 100%);
            box-shadow:0 16px 42px rgba(15,59,91,.20); margin:.4rem 0 1.2rem 0;}
        .a2ui-hero h2 {color:white; margin:0 0 .5rem 0; font-size:1.8rem;}
        .a2ui-hero p {color:rgba(255,255,255,.86); margin:0; font-size:1rem;}
        .a2ui-card {border:1px solid rgba(148,163,184,.25); border-radius:17px;
            padding:1rem 1.05rem; background:rgba(255,255,255,.78);
            box-shadow:0 5px 20px rgba(15,23,42,.045); min-height:108px;}
        .a2ui-card-label {color:#64748b; font-size:.78rem; font-weight:700;
            text-transform:uppercase; letter-spacing:.06em;}
        .a2ui-card-value {color:#0f172a; font-size:1.45rem; font-weight:800;
            margin:.35rem 0 .15rem 0;}
        .a2ui-card-desc {color:#64748b; font-size:.78rem;}
        .a2ui-section {border:1px solid rgba(148,163,184,.22); border-radius:17px;
            padding:1.1rem 1.25rem; background:rgba(255,255,255,.68); margin:.5rem 0;}
        .a2ui-notice {border-left:4px solid #0ea5e9; border-radius:10px;
            background:rgba(14,165,233,.08); padding:.9rem 1rem; color:#334155;}
        div[data-testid="stMetric"] {background:rgba(255,255,255,.76);
            border:1px solid rgba(148,163,184,.25); padding:14px 16px;
            border-radius:16px; box-shadow:0 5px 20px rgba(15,23,42,.04);}
        div[data-testid="stTabs"] button {font-weight:700;}
        </style>
        """,
        unsafe_allow_html=True,
    )

def _render_metric_grid(component: A2UIComponent):
    entries = []
    for item in component.items:
        parts = item.split("|", 2)
        if len(parts) == 3:
            entries.append(parts)
    if not entries:
        return
    cols = st.columns(len(entries))
    for col, (label, value, desc) in zip(cols, entries):
        with col:
            st.markdown(
                f'<div class="a2ui-card"><div class="a2ui-card-label">{label}</div>'
                f'<div class="a2ui-card-value">{value}</div>'
                f'<div class="a2ui-card-desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )

def _render_timeline(component: A2UIComponent):
    text = component.content or ""
    # Preserve the agent's day structure as Markdown. The Streamlit renderer
    # owns the presentation; the LLM does not return executable HTML.
    with st.container(border=True):
        st.markdown(text)

def _render_budget(component: A2UIComponent):
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown(component.content or "No budget details.")
    with right:
        if component.data:
            st.markdown("**Detected category estimates**")
            st.bar_chart(component.data, horizontal=True)
        else:
            st.info("No category amounts could be reliably extracted for a chart. See the budget breakdown.")

def _render_markdown(component: A2UIComponent):
    with st.container(border=True):
        st.markdown(component.content or "No content available.")

def _render_recommendations(component: A2UIComponent):
    with st.container(border=True):
        st.markdown(component.content or "No recommendations available.")

def _render_notice(component: A2UIComponent):
    st.markdown(
        f'<div class="a2ui-notice"><strong>{component.title}</strong><br>{component.content}</div>',
        unsafe_allow_html=True,
    )

RENDERERS = {
    "metric_grid": _render_metric_grid,
    "timeline": _render_timeline,
    "budget": _render_budget,
    "markdown": _render_markdown,
    "recommendations": _render_recommendations,
    "notice": _render_notice,
}

def render_a2ui(spec: dict[str, Any]) -> None:
    try:
        ui = A2UISpec.model_validate(spec)
    except ValidationError as exc:
        st.error("Invalid A2UI specification.")
        st.code(str(exc))
        return

    st.markdown('<div class="a2ui-eyebrow">PRAGYANAI · AGENTIC EXPERIENCE</div>', unsafe_allow_html=True)
    st.title(ui.title)
    st.caption(ui.subtitle)

    for component in ui.components:
        if component.type == "hero":
            st.markdown(
                f'<div class="a2ui-hero"><div class="a2ui-eyebrow" style="color:#bae6fd">YOUR NEXT JOURNEY</div>'
                f'<h2>{component.title}</h2><p>{component.description}</p></div>',
                unsafe_allow_html=True,
            )
            continue

        renderer = RENDERERS.get(component.type)
        if renderer:
            if component.title and component.type != "notice":
                st.subheader(component.title)
            renderer(component)
        else:
            # Unknown component types are safely skipped rather than executed.
            st.warning(f"Unsupported A2UI component type: {component.type}")

