from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

def make_llm(settings, temperature=0.3):
    return ChatGroq(
        groq_api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=temperature,
        max_retries=2,
        timeout=90,
    )

def invoke_agent(settings, role, prompt, temperature=0.3):
    llm = make_llm(settings, temperature=temperature)
    response = llm.invoke([
        SystemMessage(content=role),
        HumanMessage(content=prompt),
    ])
    return response.content if isinstance(response.content, str) else str(response.content)

def destination_agent(state, settings):
    prompt = f"""
Destination: {state['destination']}
Trip length: {state['days']} days
Travellers: {state['travelers']}
Preferences: {state['preferences']}

Prepare practical destination research with:
1. Destination overview
2. Best experiences for these preferences
3. Suggested areas/places to explore
4. Local food and cultural experiences
5. Practical travel considerations
6. Assumptions and information that needs verification

Do not invent live weather, current prices, opening hours or availability.
Clearly label general suggestions and assumptions.
"""
    return invoke_agent(
        settings,
        "You are a careful destination research specialist. Be practical and distinguish estimates from verified facts.",
        prompt,
    )

def itinerary_agent(state, settings):
    prompt = f"""
Create a realistic {state['days']}-day itinerary for {state['destination']}.
Travellers: {state['travelers']}
Preferences: {state['preferences']}

Destination research:
{state.get('research', '')[:7000]}

For each day provide morning, afternoon, evening, places/activities,
food ideas, and a practical pacing note. Avoid overly packed days.
Do not claim that reservations or transport have been booked.
"""
    return invoke_agent(
        settings,
        "You are an experienced travel itinerary designer.",
        prompt,
    )

def budget_agent(state, settings):
    prompt = f"""
Prepare an indicative trip budget for {state['destination']}.
Duration: {state['days']} days
Travellers: {state['travelers']}
User's total budget: INR {state['budget']:,.0f}
Preferences: {state['preferences']}

Break down estimates in INR for:
- Intercity transport
- Accommodation
- Food
- Local transport
- Activities and entry fees
- Miscellaneous/emergency buffer

Show estimated total, per-person estimate, budget variance and cost-saving ideas.
If the requested budget is unrealistic, say so. State assumptions.
Do not represent estimates as live quotes.
"""
    return invoke_agent(
        settings,
        "You are a travel budget analyst. Use transparent assumptions and arithmetic.",
        prompt,
    )

def recommendation_agent(state, settings):
    prompt = f"""
Give personalized recommendations for {state['destination']}.
Preferences: {state['preferences']}
Budget: INR {state['budget']:,.0f}
Travellers: {state['travelers']}

Budget analysis:
{state.get('budget_analysis', '')[:5000]}

Recommend accommodation categories, local food, transport approach,
experiences, safety/practical tips and ways to save money.
Do not invent specific business availability, ratings or booking status.
"""
    return invoke_agent(
        settings,
        "You are a practical travel recommendation specialist.",
        prompt,
    )
