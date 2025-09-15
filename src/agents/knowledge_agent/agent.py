# agents/knowledge_agent/agent.py
from google.adk.agents import Agent
import json
import os

def explain_event(event: dict) -> str:
    txid = event.get("transaction_id")
    action = event.get("action", "none")
    return f"Transaction {txid} was marked '{action}'. Please review: rule={event.get('rule','unknown')}."

root_agent = Agent(
    name="knowledge_agent",
    model="gemini-1.5-flash",
    description="Creates human readable alerts for risk events",
    instruction="Generate concise plain-English alerts for risk/compliance events",
    tools=[explain_event]
)
