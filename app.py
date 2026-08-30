import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai

from agents.growth_agent import run_growth_agent


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="GrowthPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.hero {
    padding: 2.5rem;
    border-radius: 28px;
    border: 1px solid rgba(128,128,128,.25);
    margin-bottom: 1.5rem;
    background: linear-gradient(
        135deg,
        rgba(99,102,241,.12),
        rgba(168,85,247,.08)
    );
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 850;
    letter-spacing: -2px;
    margin-bottom: .3rem;
}

.hero-subtitle {
    font-size: 1.08rem;
    opacity: .72;
    max-width: 850px;
}

.section-title {
    font-size: 1.65rem;
    font-weight: 800;
    margin-top: 1.4rem;
    margin-bottom: .2rem;
}

.section-description {
    opacity: .65;
    margin-bottom: 1rem;
}

.metric-card {
    padding: 1.4rem;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,.23);
    min-height: 130px;
}

.metric-icon {
    font-size: 1.5rem;
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 850;
    margin-top: .3rem;
}

.metric-label {
    opacity: .62;
    font-size: .9rem;
}

.feature-card {
    padding: 1.5rem;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,.23);
    min-height: 150px;
}

.result-card {
    padding: 1.6rem;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,.25);
    margin-top: 1rem;
}

.badge {
    display: inline-block;
    padding: .35rem .75rem;
    border-radius: 999px;
    border: 1px solid rgba(128,128,128,.3);
    font-size: .8rem;
    margin-right: .35rem;
}

div.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 13px;
    font-weight: 750;
}

[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.2);
    padding: 1rem;
    border-radius: 18px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "strategy": None,
    "agent_report": None,
    "customer_analysis": None,
    "marketing_message": None,
    "seven_day_plan": None,
    "customers": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None


@st.cache_resource
def create_gemini_client(key):
    if not key:
        return None
    return genai.Client(api_key=key)


client = create_gemini_client(api_key)


# ============================================================
# AI HELPER (single call path for the raw Gemini request)
# ============================================================

MODELS_TO_TRY = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
]


def generate_ai(prompt):
    """
    Central Gemini function.

    Keeps all AI requests in one place so that
    model changes and error handling are easier.
    """
    if client is None:
        raise RuntimeError("Gemini API key is not configured.")

    last_error = None

    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as error:
            last_error = error

    raise RuntimeError(f"Gemini request failed: {last_error}")


# ============================================================
# UNIFIED AI TASK RUNNER (single path for every button)
# ============================================================

def run_ai_task(prompt, state_key, spinner_text, success_text,
                 failure_text=None, guard=True, guard_message=None,
                 download_name=None):
    """
    Shared flow for every Gemini-backed button:
    guard check -> client check -> spinner -> generate -> store -> feedback -> download.

    guard: bool, must be True to proceed (e.g. business name provided)
    guard_message: shown as a warning if guard is False
    """
    if not guard:
        st.warning(guard_message or "Please fill in the required fields first.")
        return

    if not client:
        st.error("Gemini API key is not configured.")
        return

    with st.spinner(spinner_text):
        try:
            result = generate_ai(prompt)
            st.session_state[state_key] = result
            st.success(success_text)
        except Exception as error:
            st.error(failure_text or "AI generation failed.")
            st.code(str(error))
            return

    if download_name and st.session_state.get(state_key):
        st.download_button(
            "⬇️ Download as text",
            data=st.session_state[state_key],
            file_name=download_name,
            mime="text/plain",
            key=f"dl_{state_key}",
        )


def render_result(state_key, heading, download_name=None):
    """Render a stored AI result in a card, unconditionally, on every rerun."""
    content = st.session_state.get(state_key)
    if not content:
        return

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"### {heading}")
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)

    if download_name:
        st.download_button(
            "⬇️ Download as text",
            data=content,
            file_name=download_name,
            mime="text/plain",
            key=f"dl_render_{state_key}",
        )


# ============================================================
# CUSTOMER DATA
# ============================================================

DATA_FILE = Path("data/customers.csv")

REQUIRED_CUSTOMER_COLUMNS = ["visits", "purchases", "total_spent"]


def load_default_customer_data():
    """Load the bundled sample CSV once, without overwriting an active upload."""
    if st.session_state.customers is not None:
        return st.session_state.customers

    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
            st.session_state.customers = df
            return df
        except Exception as error:
            st.warning(f"Couldn't load the bundled sample data: {error}")
            return None

    return None


def calculate_customer_scores(df):
    """Add an opportunity_score column, or warn and return unchanged if columns are missing."""
    missing = [c for c in REQUIRED_CUSTOMER_COLUMNS if c not in df.columns]

    if missing:
        st.warning(
            "Can't compute opportunity scores — the CSV is missing required "
            f"column(s): {', '.join(missing)}."
        )
        return df

    result = df.copy()
    result["opportunity_score"] = (
        result["visits"] * 2
        + result["purchases"] * 5
        + result["total_spent"] / 1000
    )
    return result.sort_values("opportunity_score", ascending=False)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🚀 GrowthPilot AI")
    st.caption("AI-powered business growth intelligence")

    st.divider()

    st.markdown("### 🧭 Platform")
    st.markdown(
        """
        📊 **Dashboard**

        🧠 **Growth Strategy**

        🤖 **Growth Agent**

        👥 **Customer Intelligence**

        ✍️ **Marketing**

        📅 **7-Day Plan**
        """
    )

    st.divider()

    if client:
        st.success("🟢 AI Connected")
    else:
        st.error("🔴 AI Not Connected")

    st.divider()

    st.caption("GrowthPilot AI • Intelligent Growth Platform")


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
<div class="hero">

<div class="hero-title">
🚀 GrowthPilot AI
</div>

<div class="hero-subtitle">
Turn your business data into actionable growth decisions.
Discover opportunities, understand customers and build
AI-powered strategies in seconds.
</div>

<br>

<span class="badge">🤖 AI Powered</span>
<span class="badge">📊 Data Driven</span>
<span class="badge">⚡ Fast Insights</span>

</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# BUSINESS PROFILE
# ============================================================

st.markdown('<div class="section-title">🏢 Business Profile</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">Tell GrowthPilot about your business.</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    business = st.text_input("Business Name", placeholder="e.g. ABC Fashion").strip()

with col2:
    industry = st.selectbox(
        "Industry",
        ["Retail", "Food", "Education", "Technology", "Healthcare",
         "Finance", "Real Estate", "Other"],
    )

with col3:
    goal = st.selectbox(
        "Primary Growth Goal",
        ["Increase Sales", "Get More Customers", "Improve Retention",
         "Marketing", "Increase Revenue", "Build Brand Awareness"],
    )

if not business:
    st.caption("👋 Enter your business name above to unlock the tools below.")


# ============================================================
# KPI DASHBOARD
# ============================================================

customers = load_default_customer_data()

if customers is not None:
    customer_count = len(customers)
    total_revenue = customers["total_spent"].sum() if "total_spent" in customers.columns else 0
    total_purchases = customers["purchases"].sum() if "purchases" in customers.columns else 0
else:
    customer_count = 0
    total_revenue = 0
    total_purchases = 0

st.markdown('<div class="section-title">📊 Growth Dashboard</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("👥 Customers", f"{customer_count:,}")

with k2:
    st.metric("💰 Total Spend", f"₹{total_revenue:,.0f}")

with k3:
    st.metric("🛒 Purchases", f"{total_purchases:,}")

with k4:
    st.metric("🤖 AI Tools", "5")

st.divider()


# ============================================================
# GROWTH STRATEGY
# ============================================================

st.markdown('<div class="section-title">🧠 AI Growth Strategy</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">'
    'Generate a personalized growth strategy for your business.</div>',
    unsafe_allow_html=True,
)

if st.button("🚀 Generate Growth Strategy", key="strategy_button"):
    strategy_prompt = f"""
You are GrowthPilot AI, an expert business growth consultant.

Business:
{business}

Industry:
{industry}

Primary goal:
{goal}

Create a professional business growth strategy.

Include:

1. Executive summary
2. Three biggest growth opportunities
3. Three specific actions
4. Customer acquisition strategy
5. Customer retention strategy
6. Marketing campaign idea
7. Key metrics to track
8. Expected business impact
9. Recommended priority for the next 30 days

Make it practical, specific and measurable.
Avoid generic advice.
"""
    run_ai_task(
        strategy_prompt,
        state_key="strategy",
        spinner_text="🤖 GrowthPilot is analyzing your business...",
        success_text="Growth strategy generated!",
        failure_text="Unable to generate strategy.",
        guard=bool(business),
        guard_message="Please enter your business name first.",
        download_name="growth_strategy.txt",
    )

render_result("strategy", "📈 Your Growth Strategy", download_name="growth_strategy.txt")

st.divider()


# ============================================================
# AUTONOMOUS AGENT
# ============================================================

st.markdown('<div class="section-title">🤖 Autonomous Growth Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">'
    'Let the GrowthPilot agent evaluate your business and recommend your next moves.</div>',
    unsafe_allow_html=True,
)

if st.button("🤖 Run Growth Agent", key="agent_button"):
    if not business:
        st.warning("Enter your business name first.")
    else:
        with st.spinner("🤖 Growth Agent is working..."):
            try:
                result = run_growth_agent(business, industry, goal)
                st.session_state.agent_report = result
                st.success("Agent analysis completed!")
            except Exception as error:
                st.error("Growth Agent error.")
                st.code(str(error))

render_result("agent_report", "🧠 Agent Report", download_name="agent_report.txt")

st.divider()


# ============================================================
# CUSTOMER INTELLIGENCE
# ============================================================

st.markdown('<div class="section-title">👥 Customer Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">'
    'Find your highest-value customers and uncover revenue opportunities.</div>',
    unsafe_allow_html=True,
)

# Uploader is always visible so a user can replace data at any time,
# not just when nothing has been loaded yet.
uploaded_file = st.file_uploader(
    "📤 Upload customers.csv (optional — replaces the current data)",
    type=["csv"],
)

if uploaded_file:
    try:
        st.session_state.customers = pd.read_csv(uploaded_file)
        customers = st.session_state.customers
        st.success("Customer data updated!")
    except Exception as error:
        st.error("Could not read the CSV file.")
        st.code(str(error))
elif st.session_state.customers is not None:
    customers = st.session_state.customers

if customers is None:
    st.caption("No customer data loaded yet — upload a CSV to get started.")
else:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔎 Find Best Customers", key="best_customers"):
            scored_customers = calculate_customer_scores(customers)
            st.markdown("### 🏆 Top Opportunities")
            st.dataframe(scored_customers.head(10), use_container_width=True)

    with col2:
        if st.button("🤖 Analyze Customers with AI", key="customer_ai"):
            customer_data = customers.to_string(index=False)
            customer_prompt = f"""
You are GrowthPilot AI's customer intelligence analyst.

Analyze this customer dataset:

{customer_data}

Provide:

1. Top 3 customers to target
2. Why each is valuable
3. High-value customer segment
4. Customers needing re-engagement
5. Recommended offer for each segment
6. Customer acquisition opportunity
7. Retention opportunity
8. Next best action

Be specific and business-focused.
"""
            run_ai_task(
                customer_prompt,
                state_key="customer_analysis",
                spinner_text="🤖 AI is analyzing customer behavior...",
                success_text="Customer analysis completed!",
                failure_text="Customer AI analysis failed.",
                guard=True,
                download_name="customer_analysis.txt",
            )

render_result("customer_analysis", "🎯 AI Customer Insights", download_name="customer_analysis.txt")


# ============================================================
# CUSTOMER CHARTS
# ============================================================

if customers is not None:
    st.markdown("### 📈 Customer Analytics")

    chart_col1, chart_col2 = st.columns(2)

    if "total_spent" in customers.columns and "name" in customers.columns:
        top_spenders = (
            customers.sort_values("total_spent", ascending=False)
            .head(10)
            .set_index("name")
        )
        with chart_col1:
            st.markdown("**💰 Top Customers by Spend**")
            st.bar_chart(top_spenders["total_spent"])

    if "purchases" in customers.columns and "name" in customers.columns:
        top_buyers = (
            customers.sort_values("purchases", ascending=False)
            .head(10)
            .set_index("name")
        )
        with chart_col2:
            st.markdown("**🛒 Top Customers by Purchases**")
            st.bar_chart(top_buyers["purchases"])

st.divider()


# ============================================================
# PERSONALIZED MARKETING
# ============================================================

st.markdown('<div class="section-title">✍️ AI Personalized Marketing</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">'
    'Create personalized messages that feel human and drive action.</div>',
    unsafe_allow_html=True,
)

customer_name = st.text_input("Customer Name", placeholder="e.g. Rahul").strip()

marketing_tone = st.selectbox(
    "Message Style",
    ["Friendly", "Professional", "Premium", "Urgent", "WhatsApp Casual"],
)

if st.button("✨ Generate Personalized Message", key="marketing_button"):
    marketing_prompt = f"""
Create a personalized marketing message.

Customer:
{customer_name}

Business:
{business if business else "Our business"}

Industry:
{industry}

Tone:
{marketing_tone}

Goal:
{goal}

Requirements:

- Sound human
- Do not sound spammy
- Create curiosity
- Include a clear call to action
- Under 100 words
"""
    run_ai_task(
        marketing_prompt,
        state_key="marketing_message",
        spinner_text="✍️ Creating your message...",
        success_text="Message generated!",
        failure_text="Marketing generation failed.",
        guard=bool(customer_name),
        guard_message="Enter a customer name.",
        download_name="marketing_message.txt",
    )

render_result("marketing_message", "💬 Ready-to-Send Message", download_name="marketing_message.txt")

st.divider()


# ============================================================
# 7-DAY GROWTH PLAN
# ============================================================

st.markdown('<div class="section-title">📅 7-Day AI Growth Plan</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-description">'
    'Turn strategy into seven days of measurable execution.</div>',
    unsafe_allow_html=True,
)

if st.button("🚀 Create 7-Day Growth Plan", key="plan_button"):
    plan_prompt = f"""
You are GrowthPilot AI.

Create a highly practical 7-day growth execution plan.

Business:
{business}

Industry:
{industry}

Goal:
{goal}

For each day include:

Day X
- Main action
- Why it matters
- Exact steps
- Expected result
- KPI to measure

Also include:

- Quick win
- Biggest risk
- Success metric for the entire week

Make it realistic for a small business.
Focus on actions that can actually be completed.
"""
    run_ai_task(
        plan_prompt,
        state_key="seven_day_plan",
        spinner_text="📅 Building your 7-day growth plan...",
        success_text="Your 7-day plan is ready!",
        failure_text="Could not create the growth plan.",
        guard=bool(business),
        guard_message="Enter your business name first.",
        download_name="seven_day_plan.txt",
    )

render_result("seven_day_plan", "📅 Your 7-Day Growth Roadmap", download_name="seven_day_plan.txt")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
<div style="
text-align:center;
opacity:.55;
padding:1.5rem;
">

🚀 <b>GrowthPilot AI</b>

<br>

AI-powered business growth intelligence

<br><br>

Built to help businesses discover opportunities,
understand customers and execute growth strategies.

</div>
""",
    unsafe_allow_html=True,
)