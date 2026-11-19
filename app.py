import json
import streamlit as st
from graph import build_travel_graph
from a2ui import (
    build_ui_spec,
    render_a2ui,
    inject_a2ui_css,
    DASHBOARD_OPTIONS,
)
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
    st.markdown("### 1 · Your trip")
    destination = st.text_input("Destination", "Kerala")
    days = st.number_input("Duration (days)", min_value=1, max_value=30, value=4)
    travelers = st.number_input("Travellers", min_value=1, max_value=20, value=2)
    budget = st.number_input("Target budget (₹)", min_value=1000, value=30000, step=1000)
    preferences = st.text_area(
        "What do you enjoy?",
        "Nature, local food, less crowded destinations",
        height=100,
    )

    st.divider()
    st.markdown("### 2 · Choose your dashboard")
    dashboard_type = st.radio(
        "Which dashboard should I create?",
        options=list(DASHBOARD_OPTIONS.keys()),
        format_func=lambda option: f"{DASHBOARD_OPTIONS[option]['icon']}  {option}",
        index=0,
        help="Choose the layout that best matches what you want to explore.",
    )
    st.caption(DASHBOARD_OPTIONS[dashboard_type]["description"])
    run = st.button("✨ Create my dashboard", type="primary", use_container_width=True)
    st.divider()
    st.caption("LangGraph · Groq · A2UI-style component renderer")

st.markdown(
    """
    <div class="a2ui-eyebrow">INTELLIGENT TRAVEL PLANNING</div>
    <h1 style="margin-bottom:.15rem">Your journey, your dashboard.</h1>
    <p style="color:#64748b;font-size:1.05rem">
    Choose the dashboard experience you want. Your AI agents will prepare the
    travel plan and the A2UI renderer will assemble the selected interface.
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
            st.write("🗓️ Itinerary planning agent")
            st.write("💰 Budget analysis agent")
            st.write("⭐ Recommendation agent")
            result = graph.invoke(initial_state)
            st.write(f"🎨 Creating your **{dashboard_type}**")
            spec = build_ui_spec(result, dashboard_type=dashboard_type)
            st.session_state["travel_result"] = result
            st.session_state["a2ui_spec"] = spec
            st.session_state["selected_dashboard_type"] = dashboard_type
            status.update(label="Your dashboard is ready", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="Dashboard creation failed", state="error")
            st.exception(exc)

if "travel_result" in st.session_state:
    result = st.session_state["travel_result"]
    spec = st.session_state["a2ui_spec"]
    previous_type = st.session_state.get("selected_dashboard_type", "Complete Travel Dashboard")

    # Let the user switch the dashboard after generation without rerunning LLM agents.
    with st.container(border=True):
        st.markdown("#### Change dashboard view")
        selected_view = st.selectbox(
            "Select another dashboard layout",
            options=list(DASHBOARD_OPTIONS.keys()),
            index=list(DASHBOARD_OPTIONS.keys()).index(previous_type)
            if previous_type in DASHBOARD_OPTIONS else 0,
            format_func=lambda option: f"{DASHBOARD_OPTIONS[option]['icon']}  {option}",
            key="post_generation_dashboard_choice",
        )
        if selected_view != previous_type:
            st.session_state["a2ui_spec"] = build_ui_spec(result, dashboard_type=selected_view)
            st.session_state["selected_dashboard_type"] = selected_view
            st.rerun()

    tabs = st.tabs(["✨ Dashboard", "🧭 Research", "🗓️ Itinerary", "💳 Budget", "🌟 Recommendations", "🧩 A2UI JSON"])
    with tabs[0]:
        render_a2ui(st.session_state["a2ui_spec"])
    with tabs[1]:
        st.markdown(result.get("research") or "No research generated.")
    with tabs[2]:
        st.markdown(result.get("itinerary") or "No itinerary generated.")
    with tabs[3]:
        st.markdown(result.get("budget_analysis") or "No budget analysis generated.")
    with tabs[4]:
        st.markdown(result.get("recommendations") or "No recommendations generated.")
    with tabs[5]:
        st.caption("This validated JSON defines the selected dashboard component tree.")
        st.json(st.session_state["a2ui_spec"])
        st.download_button(
            "Download UI specification",
            data=json.dumps(st.session_state["a2ui_spec"], indent=2, ensure_ascii=False),
            file_name="pragyanai_a2ui_spec.json",
            mime="application/json",
        )
else:
    st.markdown("### Choose the experience you want")
    cols = st.columns(2)
    for idx, (name, meta) in enumerate(DASHBOARD_OPTIONS.items()):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="a2ui-card" style="margin-bottom:12px">
                  <div style="font-size:1.5rem">{meta['icon']}</div>
                  <div style="font-weight:800;color:#0f172a;margin:.35rem 0">{name}</div>
                  <div style="color:#64748b;font-size:.88rem">{meta['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
