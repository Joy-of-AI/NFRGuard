# agents/transaction_risk_agent/agent.py
from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import publish
import requests
import os

ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.8"))

def check_transaction_anomaly(tx: dict) -> dict:
    """Very small heuristic anomaly check; replace with ML model or rules."""
    amount = tx.get("amount", 0)
    # example rule: > 10000 and cross-border flagged
    suspicious = amount > 10000 or tx.get("metadata", {}).get("cross_border", False)
    score = 0.95 if suspicious else 0.1
    return {"transaction_id": tx["transaction_id"], "score": score, "suspicious": suspicious}

def on_transaction_event(event: dict) -> dict:
    result = check_transaction_anomaly(event)
    if result["suspicious"]:
        publish("risk.flagged", {
            "event_type": "risk.flagged",
            "transaction_id": event["transaction_id"],
            "reason": "high_amount_or_cross_border",
            "score": result["score"],
            "detected_by": "transaction_risk_agent_v1"
        })
    return result

root_agent = Agent(
    name="transaction_risk_agent",
    model="gemini-2.5-flash",   # model optional; agent can be purely procedural
    description="Detects suspicious transactions and emits risk events",
    instruction="Listen for transaction.created events and check for anomalies.",
    tools=[on_transaction_event],
)
