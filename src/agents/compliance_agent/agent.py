# agents/compliance_agent/agent.py
from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import publish
import os

AUSTRAC_THRESHOLD = float(os.getenv("AUSTRAC_THRESHOLD", "10000"))

def compliance_check(risk: dict) -> dict:
    txid = risk["transaction_id"]
    # in real code, call transaction API to fetch details
    # For demo, assume amount provided externally; if above threshold, require hold
    # Here, assume risk includes score and we map to action
    action = "hold_and_report" if risk.get("score",0) > 0.8 else "monitor"
    publish("compliance.action", {
        "event_type": "compliance.action",
        "transaction_id": txid,
        "action": action,
        "rule": "AUSTRAC_threshold"
    })
    return {"transaction_id": txid, "action": action}

root_agent = Agent(
    name="compliance_agent",
    model="gemini-1.5-flash",
    description="Applies regulatory checks and emits compliance actions",
    instruction="Receive risk.flagged events and determine regulatory actions",
    tools=[compliance_check],
)
