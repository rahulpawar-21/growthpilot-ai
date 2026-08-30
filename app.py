import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from agents.growth_agent import run_growth_agent

load_dotenv()

st.set_page_config(
    page_title="GrowthPilot AI",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 GrowthPilot AI")
st.write("AI-powered business growth assistant")
# ==============================
# DASHBOARD
# ==============================

st.sidebar.title("🚀 GrowthPilot AI")
st.sidebar.write("AI Business Growth Platform")

st.sidebar.divider()

st.sidebar.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🤖 AI Agents", "1")

with col2:
    st.metric("🎯 Growth Tools", "4")

with col3:
    st.metric("📈 Business Focus", "Growth")

# ==============================
# BUSINESS INFORMATION
# ==============================

business = st.text_input("🏢 Business Name")

industry = st.selectbox(
    "📌 Industry",
    [
        "Retail",
        "Food",
        "Education",
        "Technology",
        "Healthcare",
        "Other"
    ]
)

goal = st.selectbox(
    "🎯 Growth Goal",
    [
        "Increase Sales",
        "Get More Customers",
        "Improve Retention",
        "Marketing"
    ]
)

# ==============================
# GEMINI CLIENT
# ==============================

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


# ==============================
# AI GROWTH STRATEGY
# ==============================

if st.button("🚀 Generate Growth Strategy"):

    if not business:
        st.warning("Please enter your business name.")

    elif not api_key:
        st.error("Gemini API key not found. Check your .env file.")

    else:

        prompt = f"""
You are GrowthPilot AI, an expert business growth consultant.

Business: {business}
Industry: {industry}
Goal: {goal}

Create a practical growth strategy with:

1. Three key opportunities
2. Three specific actions
3. A customer acquisition strategy
4. A marketing idea
5. Expected business impact

Keep the answer clear and actionable.
"""

        with st.spinner("🤖 AI is analyzing..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        st.subheader("📈 AI Growth Strategy")
        st.write(response.text)


st.divider()


# ==============================
# AUTONOMOUS GROWTH AGENT
# ==============================

st.subheader("🤖 Autonomous Growth Agent")

if st.button("Run Growth Agent"):

    if not business:
        st.warning("Enter your business name first.")

    else:

        with st.spinner("Agent is analyzing your business..."):

            result = run_growth_agent(
                business,
                industry,
                goal
            )

        st.subheader("🧠 GrowthPilot Agent Report")
        st.write(result)


st.divider()



# ==============================
# CUSTOMER OPPORTUNITY ANALYSIS
# ==============================

st.subheader("🎯 Customer Opportunity Analysis")
# ==============================
# AI CUSTOMER INSIGHTS
# ==============================

st.subheader("🧠 AI Customer Insights")

if st.button("🤖 Analyze Customers with AI"):

    if not api_key:
        st.error("Gemini API key not found. Check your .env file.")

    else:
        customers = pd.read_csv("data/customers.csv")

        customer_data = customers.to_string(index=False)

        prompt = f"""
You are an AI business growth analyst.

Analyze the following customer data:

{customer_data}

Identify:

1. The top 3 customers to target
2. Why each customer is valuable
3. Which customers may need re-engagement
4. What offer should be given to each group
5. A recommended next action

Give practical business recommendations.
"""

        with st.spinner("🤖 AI is analyzing customer data..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        st.subheader("📊 AI Customer Analysis")
        st.write(response.text)

st.divider()

if st.button("🔎 Find Best Customers"):

    customers = pd.read_csv("data/customers.csv")

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
        f"🎯 Best opportunity: {customers.iloc[0]['name']}"
    )


st.divider()


# ==============================
# PERSONALIZED AI MESSAGE
# ==============================

st.subheader("✍️ AI Personalized Customer Message")

customer_name = st.text_input("Customer Name")

if st.button("✨ Generate Personalized Message"):

    if not customer_name:

        st.warning("Enter a customer name.")

    elif not api_key:

        st.error("Gemini API key not found. Check your .env file.")

    else:

        prompt = f"""
Create a short, friendly personalized marketing message
for this customer.

Customer: {customer_name}
Business: {business if business else "our business"}
Industry: {industry}

The message should:

- Feel personal, not spammy
- Encourage the customer to make a purchase
- Include a clear call to action
- Be under 80 words
"""

        with st.spinner("🤖 Creating personalized message..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        st.success("Message generated!")

        st.write(response.text)
        # ==============================
# 7-DAY AI GROWTH PLAN
# ==============================

st.divider()

st.subheader("📅 7-Day AI Growth Plan")

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

Continue through Day 7.

Make the plan realistic for a small business
and focus on measurable growth.
"""

        with st.spinner("🤖 Creating your 7-day growth plan..."):

            try:
   try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    st.subheader("📈 AI Growth Strategy")
    st.write(response.text)

except Exception as e:
    st.error("Gemini API error")
    st.write(str(e))

    except Exception as e:
    st.error("Gemini API request failed.")
    st.code(str(e))
    st.stop()

    st.subheader("📈 Your 7-Day Growth Plan")
    st.write(response.text)