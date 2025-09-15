# agents/resilience_agent/agent.py
from google.adk.agents import Agent
import requests
import os

ANTHOS_API_BASE = os.getenv("ANTHOS_API_BASE", "http://localhost:8080")

def apply_hold(action_event: dict) -> dict:
    txid = action_event["transaction_id"]
    if action_event["action"] == "hold_and_report":
        # call anthos transaction service to set hold (HTTP call example)
        try:
            resp = requests.post(f"{ANTHOS_API_BASE}/transactions/{txid}/hold")
            return {"transaction_id": txid, "status": "held", "http_status": resp.status_code}
        except Exception as e:
            return {"transaction_id": txid, "status": "error", "error": str(e)}
    return {"transaction_id": txid, "status": "no_action"}

root_agent = Agent(
    name="resilience_agent",
    model="gemini-1.5-flash",
    description="Performs operational actions such as placing holds",
    instruction="Receive compliance.action events and call APIs to perform actions",
    tools=[apply_hold],
)
