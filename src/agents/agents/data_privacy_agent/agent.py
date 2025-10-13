# agents/data_privacy_agent/agent.py
import os
from shared.bedrock_agent import BedrockAgent
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

root_agent = BedrockAgent(
    name="data_privacy_agent",
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    description="Monitors logs and requests for PII violations",
    instruction="Scan log entries and requests for personal information leaks",
    tools=[check_privacy_violation],
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
            response = {"status": "healthy", "agent": "data_privacy_agent"}
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
    print("data_privacy_agent Agent running on port 8080...")
    server.serve_forever()
