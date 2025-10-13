# agents/transaction_risk_agent/agent.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.bedrock_agent import BedrockAgent
from shared.messaging import publish
import requests

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

root_agent = BedrockAgent(
    name="transaction_risk_agent",
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    description="Detects suspicious transactions and emits risk events",
    instruction="Listen for transaction.created events and check for anomalies.",
    tools=[on_transaction_event],
)


# Simple HTTP server to keep the agent running
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/ready':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "agent": "transaction_risk_agent"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                response = root_agent.invoke(message)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                result = {"response": response}
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error = {"error": str(e)}
                self.wfile.write(json.dumps(error).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), AgentHandler)
    print("transaction_risk_agent Agent running on port 8080...")
    server.serve_forever()
