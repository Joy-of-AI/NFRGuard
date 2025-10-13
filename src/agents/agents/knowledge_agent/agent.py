# agents/knowledge_agent/agent.py
import os
from shared.bedrock_agent import BedrockAgent
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

root_agent = BedrockAgent(
    name="knowledge_agent",
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    description="Creates human readable alerts for risk events",
    instruction="Generate concise plain-English alerts for risk/compliance events",
    tools=[explain_event, handle_risk_event, handle_compliance_event, handle_ops_alert]
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
            response = {"status": "healthy", "agent": "knowledge_agent"}
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
    print("knowledge_agent Agent running on port 8080...")
    server.serve_forever()
