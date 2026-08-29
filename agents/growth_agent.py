import os
from google import genai


def run_growth_agent(business, industry, goal):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "API key not found."

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are GrowthPilot, an autonomous AI business growth agent.

Business: {business}
Industry: {industry}
Goal: {goal}

Follow this process:

1. Analyze the business situation.
2. Identify the biggest growth opportunity.
3. Decide the best customer strategy.
4. Create a marketing action.
5. Create a 7-day action plan.
6. Explain why your recommendations should work.

Return the result using these sections:

BUSINESS ANALYSIS
TOP OPPORTUNITY
CUSTOMER STRATEGY
MARKETING ACTION
7-DAY ACTION PLAN
EXPECTED IMPACT
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text