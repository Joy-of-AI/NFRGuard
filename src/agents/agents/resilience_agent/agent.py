# agents/resilience_agent/agent.py
import os
from shared.bedrock_agent import BedrockAgent
import requests
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import subscribe

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

def handle_compliance_action(event: dict) -> dict:
    """Handle compliance.action events from compliance_agent"""
    print(f"[RESILIENCE] Received compliance action: {event}")
    return apply_hold(event)

# Subscribe to compliance actions
subscribe("compliance.action", handle_compliance_action)

root_agent = BedrockAgent(
    name="resilience_agent",
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    description="Performs operational actions such as placing holds",
    instruction="Receive compliance.action events and call APIs to perform actions",
    tools=[apply_hold, handle_compliance_action],
)


# Simple HTTP server to keep the agent running
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "agent": "resilience_agent"}
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
    print("resilience_agent Agent running on port 8080...")
    server.serve_forever()
