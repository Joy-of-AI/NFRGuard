# agents/knowledge_agent/agent.py
from google.adk.agents import Agent
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import subscribe

def explain_event(event: dict) -> str:
    txid = event.get("transaction_id")
    action = event.get("action", "none")
    return f"Transaction {txid} was marked '{action}'. Please review: rule={event.get('rule','unknown')}."

def handle_risk_event(event: dict) -> str:
    """Handle risk.flagged events and create human-readable explanations"""
    print(f"[KNOWLEDGE] Received risk event: {event}")
    return explain_event(event)

def handle_compliance_event(event: dict) -> str:
    """Handle compliance.action events and create human-readable explanations"""
    print(f"[KNOWLEDGE] Received compliance event: {event}")
    return explain_event(event)

def handle_ops_alert(event: dict) -> str:
    """Handle ops.alert events and create human-readable explanations"""
    print(f"[KNOWLEDGE] Received ops alert: {event}")
    customer_id = event.get("customer_id", "unknown")
    sentiment = event.get("sentiment", "unknown")
    severity = event.get("severity", "unknown")
    return f"Customer {customer_id} reported {sentiment} sentiment with {severity} severity. Keywords: {event.get('keywords', [])}"

# Subscribe to multiple event types
subscribe("risk.flagged", handle_risk_event)
subscribe("compliance.action", handle_compliance_event)
subscribe("ops.alert", handle_ops_alert)

root_agent = Agent(
    name="knowledge_agent",
    model="gemini-2.5-flash",
    description="Creates human readable alerts for risk events",
    instruction="Generate concise plain-English alerts for risk/compliance events",
    tools=[explain_event, handle_risk_event, handle_compliance_event, handle_ops_alert]
)
