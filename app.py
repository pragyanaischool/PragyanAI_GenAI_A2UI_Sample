import streamlit as st
from graph import build_travel_graph
from a2ui import build_ui_spec, render_a2ui
from config import get_settings

st.set_page_config(
    page_title="PragyanAI | Agentic Travel Planner",
    page_icon="✈️",
    layout="wide",
)

st.title(" PragyanAI -Agentic AI Travel Planner")
st.caption("Streamlit · LangGraph · Groq · MCP-style tools · A2UI")
st.write(
    "Plan a trip with specialist AI agents for destination research, "
    "itinerary design, budget planning and recommendations."
)

try:
    settings = get_settings()
except Exception as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.header("Trip requirements")
    destination = st.text_input("Destination", "Kerala")
    days = st.number_input("Number of days", min_value=1, max_value=30, value=4)
    travelers = st.number_input("Number of travellers", min_value=1, max_value=20, value=2)
    budget = st.number_input("Total budget (₹)", min_value=1000, value=30000, step=1000)
    preferences = st.text_area(
        "Preferences",
        "Nature, local food, less crowded destinations",
        height=110,
    )
    run = st.button(" Generate travel plan", type="primary", use_container_width=True)

if run:
    if not destination.strip():
        st.warning("Please enter a destination.")
        st.stop()

    initial_state = {
        "destination": destination.strip(),
        "days": int(days),
        "travelers": int(travelers),
        "budget": float(budget),
        "preferences": preferences.strip(),
        "errors": [],
    }

    graph = build_travel_graph(settings)
    progress = st.progress(0, text="Starting LangGraph workflow...")
    status = st.empty()

    try:
        # LangGraph invokes specialist nodes sequentially and stores shared state.
        result = graph.invoke(initial_state)
        progress.progress(100, text="Travel plan completed")
        status.success("All specialist agents completed.")

        st.session_state["travel_result"] = result
        st.session_state["a2ui_spec"] = build_ui_spec(result)

    except Exception as exc:
        progress.empty()
        status.error(f"Workflow failed: {type(exc).__name__}: {exc}")
        with st.expander("Technical details"):
            st.exception(exc)

if "travel_result" in st.session_state:
    result = st.session_state["travel_result"]
    spec = st.session_state.get("a2ui_spec") or build_ui_spec(result)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1. A2UI Dashboard",
        "2. Destination Research",
        "3. Itinerary",
        "4. Budget",
        "5. Recommendations",
        "6. Workflow & JSON",
    ])

    with tab1:
        render_a2ui(spec)

    with tab2:
        st.markdown(result.get("research", "No research generated."))

    with tab3:
        st.markdown(result.get("itinerary", "No itinerary generated."))

    with tab4:
        st.markdown(result.get("budget_analysis", "No budget analysis generated."))

    with tab5:
        st.markdown(result.get("recommendations", "No recommendations generated."))

    with tab6:
        st.subheader("LangGraph execution state")
        st.write({
            "destination": result.get("destination"),
            "days": result.get("days"),
            "travelers": result.get("travelers"),
            "agent_sequence": [
                "MCP tools",
                "Destination Agent",
                "Itinerary Agent",
                "Budget Agent",
                "Recommendation Agent",
                "A2UI specification",
            ],
            "errors": result.get("errors", []),
        })
        st.subheader("A2UI JSON specification")
        st.json(spec)
        st.download_button(
            "Download A2UI JSON",
            data=json.dumps(spec, indent=2, ensure_ascii=False),
            file_name="travel_a2ui_spec.json",
            mime="application/json",
        )
else:
    st.info("Enter your trip requirements in the sidebar and select **Generate travel plan**.")
