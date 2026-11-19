import json
import streamlit as st
from graph import build_travel_graph
from a2ui import build_ui_spec, render_a2ui, inject_a2ui_css
from config import get_settings

st.set_page_config(
    page_title="PragyanAI | Agentic Travel Studio",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_a2ui_css()

with st.sidebar:
    st.markdown("## ✈️ PragyanAI")
    st.caption("AGENTIC TRAVEL STUDIO")
    st.divider()
    st.markdown("### Plan your journey")
    destination = st.text_input("Destination", "Kerala")
    days = st.number_input("Duration (days)", min_value=1, max_value=30, value=4)
    travelers = st.number_input("Travellers", min_value=1, max_value=20, value=2)
    budget = st.number_input("Target budget (₹)", min_value=1000, value=30000, step=1000)
    preferences = st.text_area(
        "What do you enjoy?",
        "Nature, local food, less crowded destinations",
        height=110,
    )
    run = st.button("✨ Generate my travel plan", type="primary", use_container_width=True)
    st.divider()
    st.caption("Powered by LangGraph · Groq · A2UI-style renderer")

st.markdown(
    """
    <div class="a2ui-eyebrow">INTELLIGENT TRAVEL PLANNING</div>
    <h1 style="margin-bottom:.15rem">Your journey, thoughtfully designed.</h1>
    <p style="color:#64748b;font-size:1.05rem">
    A team of AI specialists researches, plans, estimates and recommends —
    then assembles your results into a dynamic dashboard.
    </p>
    """,
    unsafe_allow_html=True,
)

try:
    settings = get_settings()
except Exception as exc:
    st.error(str(exc))
    st.stop()

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
    with st.status("Your AI travel team is working...", expanded=True) as status:
        try:
            st.write("🔧 Preparing travel tools")
            st.write("🔎 Destination research agent")
            st.write("🗺️ Itinerary planning agent")
            st.write("💰 Budget analysis agent")
            st.write("⭐ Recommendation agent")
            result = graph.invoke(initial_state)
            st.write("🎨 Building dynamic A2UI dashboard")
            spec = build_ui_spec(result)
            st.session_state["travel_result"] = result
            st.session_state["a2ui_spec"] = spec
            status.update(label="Your travel plan is ready", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="Travel planning failed", state="error")
            st.exception(exc)

if "travel_result" in st.session_state:
    result = st.session_state["travel_result"]
    spec = st.session_state["a2ui_spec"]

    tabs = st.tabs(["✨ Overview", "🧭 Research", "🗓️ Itinerary", "💳 Budget", "🌟 Recommendations", "🧩 A2UI JSON"])
    with tabs[0]:
        render_a2ui(spec)
    with tabs[1]:
        st.markdown(result.get("research", "No research generated."))
    with tabs[2]:
        st.markdown(result.get("itinerary", "No itinerary generated."))
    with tabs[3]:
        st.markdown(result.get("budget_analysis", "No budget analysis generated."))
    with tabs[4]:
        st.markdown(result.get("recommendations", "No recommendations generated."))
    with tabs[5]:
        st.caption("The JSON describes the UI components. The renderer maps approved component types to Streamlit widgets.")
        st.json(spec)
        st.download_button(
            "Download UI specification",
            data=json.dumps(spec, indent=2, ensure_ascii=False),
            file_name="pragyanai_a2ui_spec.json",
            mime="application/json",
        )
else:
    st.markdown(
        """
        <div class="a2ui-section">
        <h3>One request. Four specialist agents. One adaptive dashboard.</h3>
        <p>Enter your destination and preferences in the sidebar, then generate
        your plan. The dashboard is assembled from a structured UI specification.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
