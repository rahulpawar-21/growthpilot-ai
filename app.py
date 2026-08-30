import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from agents.growth_agent import run_growth_agent

load_dotenv()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GrowthPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.main-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.7;
    margin-bottom: 2rem;
}

.hero {
    padding: 2rem;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 2rem;
}

.card {
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 1rem;
}

.metric-card {
    padding: 1.4rem;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.25);
    text-align: center;
}

.metric-number {
    font-size: 2rem;
    font-weight: 800;
}

.metric-label {
    opacity: 0.7;
}

.section-title {
    font-size: 1.7rem;
    font-weight: 750;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.small-text {
    opacity: 0.7;
}

div.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.65rem 1rem;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# GEMINI CLIENT
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🚀 GrowthPilot AI")

    st.caption("AI-powered business growth platform")

    st.divider()

    st.markdown("### 🧭 Navigation")

    st.markdown("""
    **📊 Dashboard**

    **🧠 AI Growth Strategy**

    **🤖 Growth Agent**

    **👥 Customer Intelligence**

    **✍️ Marketing Message**

    **📅 7-Day Growth Plan**
    """)

    st.divider()

    if api_key:
        st.success("🟢 Gemini AI Connected")
    else:
        st.error("🔴 Gemini API Not Connected")

    st.caption("GrowthPilot AI • MVP")

# =========================================================
# HERO
# =========================================================

st.markdown(
    '<div class="hero">'
    '<div class="main-title">🚀 GrowthPilot AI</div>'
    '<div class="subtitle">'
    'Your intelligent business growth assistant — analyze customers, '
    'generate strategies and discover your next growth opportunity.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# DASHBOARD METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">🤖 1</div>
        <div class="metric-label">AI Agent</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">🎯 4</div>
        <div class="metric-label">Growth Tools</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">👥 AI</div>
        <div class="metric-label">Customer Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">📈 24/7</div>
        <div class="metric-label">Growth Assistant</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# BUSINESS PROFILE
# =========================================================

st.markdown(
    '<div class="section-title">🏢 Business Profile</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    business = st.text_input(
        "Business Name",
        placeholder="e.g. ABC Fashion"
    )

with col2:
    industry = st.selectbox(
        "Industry",
        [
            "Retail",
            "Food",
            "Education",
            "Technology",
            "Healthcare",
            "Other"
        ]
    )

with col3:
    goal = st.selectbox(
        "Growth Goal",
        [
            "Increase Sales",
            "Get More Customers",
            "Improve Retention",
            "Marketing"
        ]
    )

# =========================================================
# AI GROWTH STRATEGY
# =========================================================

st.markdown(
    '<div class="section-title">🧠 AI Growth Strategy</div>',
    unsafe_allow_html=True
)

st.caption(
    "Get a practical strategy tailored to your business, industry and goal."
)

if st.button("🚀 Generate Growth Strategy"):

    if not business:
        st.warning("Please enter your business name.")

    elif not api_key:
        st.error("Gemini API key not found.")

    else:

        prompt = f"""
You are GrowthPilot AI, an expert business growth consultant.

Business: {business}
Industry: {industry}
Goal: {goal}

Create a practical growth strategy with:

1. Three key opportunities
2. Three specific actions
3. Customer acquisition strategy
4. Marketing idea
5. Expected business impact

Make the answer clear, practical and actionable.
"""

        with st.spinner("🤖 AI is analyzing your business..."):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

                st.success("Growth strategy generated!")

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                st.write(response.text)

                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error("Gemini API error")
                st.write(str(e))

st.divider()

# =========================================================
# AUTONOMOUS GROWTH AGENT
# =========================================================

st.markdown(
    '<div class="section-title">🤖 Autonomous Growth Agent</div>',
    unsafe_allow_html=True
)

st.caption(
    "Let the GrowthPilot agent analyze your business and recommend actions."
)

if st.button("🤖 Run Growth Agent"):

    if not business:

        st.warning("Enter your business name first.")

    else:

        with st.spinner("🤖 Agent is analyzing your business..."):

            try:

                result = run_growth_agent(
                    business,
                    industry,
                    goal
                )

                st.success("Agent analysis completed!")

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                st.write(result)

                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:

                st.error("Growth Agent error")
                st.write(str(e))

st.divider()

# =========================================================
# CUSTOMER INTELLIGENCE
# =========================================================

st.markdown(
    '<div class="section-title">👥 Customer Intelligence</div>',
    unsafe_allow_html=True
)

st.caption(
    "Discover your highest-value customers and identify growth opportunities."
)

col1, col2 = st.columns(2)

# ---------------------------------------------------------
# FIND BEST CUSTOMERS
# ---------------------------------------------------------

with col1:

    if st.button("🔎 Find Best Customers"):

        try:

            customers = pd.read_csv(
                "data/customers.csv"
            )

            customers["opportunity_score"] = (
                customers["visits"] * 2
                + customers["purchases"] * 5
                + customers["total_spent"] / 1000
            )

            customers = customers.sort_values(
                "opportunity_score",
                ascending=False
            )

            st.dataframe(
                customers,
                use_container_width=True
            )

            st.success(
                f"🎯 Best opportunity: "
                f"{customers.iloc[0]['name']}"
            )

        except Exception as e:

            st.error("Customer data error")
            st.write(str(e))

# ---------------------------------------------------------
# AI CUSTOMER ANALYSIS
# ---------------------------------------------------------

with col2:

    if st.button("🤖 Analyze Customers with AI"):

        if not api_key:

            st.error("Gemini API key not found.")

        else:

            try:

                customers = pd.read_csv(
                    "data/customers.csv"
                )

                customer_data = customers.to_string(
                    index=False
                )

                prompt = f"""
You are an AI business growth analyst.

Analyze this customer data:

{customer_data}

Identify:

1. Top 3 customers to target
2. Why each customer is valuable
3. Customers needing re-engagement
4. Recommended offer for each group
5. Recommended next action

Give practical recommendations.
"""

                with st.spinner(
                    "🤖 AI is analyzing customers..."
                ):

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                st.write(response.text)

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            except Exception as e:

                st.error("Customer AI analysis error")
                st.write(str(e))

st.divider()

# =========================================================
# PERSONALIZED MARKETING MESSAGE
# =========================================================

st.markdown(
    '<div class="section-title">✍️ Personalized Marketing</div>',
    unsafe_allow_html=True
)

st.caption(
    "Generate a personalized message designed to convert customers."
)

customer_name = st.text_input(
    "Customer Name",
    placeholder="e.g. Rahul"
)

if st.button("✨ Generate Personalized Message"):

    if not customer_name:

        st.warning("Enter a customer name.")

    elif not api_key:

        st.error("Gemini API key not found.")

    else:

        prompt = f"""
Create a short, friendly personalized marketing message.

Customer: {customer_name}
Business: {business if business else "our business"}
Industry: {industry}

Requirements:

- Feel personal
- Do not sound spammy
- Encourage a purchase
- Include a clear call to action
- Under 80 words
"""

        with st.spinner(
            "🤖 Creating personalized message..."
        ):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

                st.success(
                    "Marketing message generated!"
                )

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                st.write(response.text)

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            except Exception as e:

                st.error("Gemini API error")
                st.write(str(e))

st.divider()

# =========================================================
# 7-DAY GROWTH PLAN
# =========================================================

st.markdown(
    '<div class="section-title">📅 7-Day AI Growth Plan</div>',
    unsafe_allow_html=True
)

st.caption(
    "Get a practical day-by-day action plan focused on measurable growth."
)

if st.button("🚀 Create 7-Day Plan"):

    if not business:

        st.warning("Enter your business name first.")

    elif not api_key:

        st.error("Gemini API key not found.")

    else:

        prompt = f"""
You are GrowthPilot AI.

Create a practical 7-day growth plan.

Business: {business}
Industry: {industry}
Goal: {goal}

For each day provide:

Day 1:
- Action
- Reason
- Expected result

Day 2:
- Action
- Reason
- Expected result

Day 3:
- Action
- Reason
- Expected result

Day 4:
- Action
- Reason
- Expected result

Day 5:
- Action
- Reason
- Expected result

Day 6:
- Action
- Reason
- Expected result

Day 7:
- Action
- Reason
- Expected result

Make the plan realistic for a small business
and focus on measurable growth.
"""

        with st.spinner(
            "🤖 Creating your 7-day growth plan..."
        ):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

                st.success(
                    "7-day growth plan created!"
                )

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                st.write(response.text)

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

            except Exception as e:

                st.error("Gemini API error")
                st.write(str(e))

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; opacity:0.6;">
        🚀 <b>GrowthPilot AI</b><br>
        Turn business data into growth decisions.
    </div>
    """,
    unsafe_allow_html=True
)