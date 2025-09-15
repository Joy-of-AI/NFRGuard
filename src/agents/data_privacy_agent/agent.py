# agents/data_privacy_agent/agent.py
from google.adk.agents import Agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import publish
import re
import os

def check_privacy_violation(log_entry: dict) -> dict:
    """Check for PII leaks in log entries."""
    content = log_entry.get("content", "")
    
    # Simple PII detection patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    
    violations = []
    if re.search(email_pattern, content):
        violations.append("email_address")
    if re.search(phone_pattern, content):
        violations.append("phone_number")
    if re.search(ssn_pattern, content):
        violations.append("ssn")
    
    if violations:
        publish("privacy.violation", {
            "event_type": "privacy.violation",
            "log_id": log_entry.get("log_id", "unknown"),
            "violations": violations,
            "severity": "high" if "ssn" in violations else "medium",
            "detected_by": "data_privacy_agent_v1"
        })
    
    return {
        "log_id": log_entry.get("log_id", "unknown"),
        "violations": violations,
        "action": "block" if violations else "allow"
    }

root_agent = Agent(
    name="data_privacy_agent",
    model="gemini-1.5-flash",
    description="Monitors logs and requests for PII violations",
    instruction="Scan log entries and requests for personal information leaks",
    tools=[check_privacy_violation],
)
