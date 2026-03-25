from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from catalog_agent.agent import catalog_agent

def save_user_info(tool_context: ToolContext,
                   name: str,
                   email: str,
                   mobile: str):

    tool_context.state["name"] = name
    tool_context.state["email"] = email
    tool_context.state["mobile"] = mobile

root_agent = LlmAgent(
    name="ecommerce_agent",
    description="An ecommerce agent that manages the ecommmerce workflow",
    model="gemini-2.0-flash",
    instruction="""
    Role: You are an ecommerce agent who can help the user with product catalog, checkout
    and order tracking.
    
    Workflow:
    - If you do not know, ask for the user's name, email and mobile number. Ask only one
    information at a time.
    - Once you have the above information, call the save_user_info() tool to 
    save these information.
    - Then understand the user's intent. Are they looking for new purchase or
    track an existing order.
    - Based on the user's request and route it to ONE of your sub-agents:
        - catalog_agent - For New purchases, questions about products, prices, availability etc.
        - checkout_agent - For checkout of items in cart.
        - tracking_agent - For tracking existing orders.
    
    Rules:
    1. NEVER answer the question yourself. Always delegate to exactly one sub-agent.
    2. If the user's message clearly matches one category, immediately call that agent.
    3. If you are unsure, ask a short clarifying question instead of guessing.
    4. After a sub-agent responds, you may send that response back as-is to the user,
    without adding extra content.
    """,
    tools=[save_user_info],
    sub_agents=[catalog_agent]
)