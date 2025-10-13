# agents/compliance_agent/agent.py
import os
from shared.bedrock_agent import BedrockAgent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.messaging import publish, subscribe
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

def handle_risk_event(event: dict) -> dict:
    """Handle risk.flagged events from transaction_risk_agent"""
    print(f"[COMPLIANCE] Received risk event: {event}")
    return compliance_check(event)

# Subscribe to risk events
subscribe("risk.flagged", handle_risk_event)

root_agent = BedrockAgent(
    name="compliance_agent",
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    description="Applies regulatory checks and emits compliance actions",
    instruction="Receive risk.flagged events and determine regulatory actions",
    tools=[compliance_check, handle_risk_event],
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
            response = {"status": "healthy", "agent": "compliance_agent"}
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
    print("compliance_agent Agent running on port 8080...")
    server.serve_forever()
