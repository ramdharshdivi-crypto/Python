from google.adk.agents import LlmAgent

order_summary_agent = LlmAgent(
    name="order_summary_agent",
    description="An order summary agent that gives a summary of the complete order",
    model="gemini-2.0-flash",
    instruction="""
    Goal:
    - Read the COMPLETE ORDER INFORMATION from SESSION STATE.
    - Present a clear, friendly summary of the order to the user.

    Use the following information from the state object
    and generate an order summary. The summary should be user friendly and
    should look like how amazon or flipkart generates them.

    {name} {email} {mobile}
    {item} {quantity} {price} {shipping_address}

    Rule:
    Read ONLY from state; do NOT invent random information that are not in state.

    """
)